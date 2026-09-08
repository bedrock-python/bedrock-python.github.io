---
date: 2026-09-07
authors:
  - alex
categories:
  - Design
tags:
  - idempotency-kit
  - idempotency
  - http
  - redis
  - distributed-systems
  - payments
---

# Idempotency keys: the part everyone gets wrong

<div class="bdr-post__hero" data-bdr-post="2026-09-07-idempotency-keys-the-part-everyone-gets-wrong" role="img" aria-label="The case that matters is the retry that arrives while the first request is still running" markdown="0"></div>

An `Idempotency-Key` header is the most widely copied idea in payment APIs, and the most widely misimplemented. The version that gets written first is a result cache: look the key up, return the stored response if there is one, otherwise run the operation and store the result. It passes every test, because every test sends the second request after the first one finished. The one case an idempotency key exists for is the one where it does not: a client that timed out and retried while the first request is still running. I built a payment provider that counts its charges and sent it that case, under three implementations of the same key. The result cache charged the card twice.

<!-- more -->

The numbers come from [the post's lab script](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-idempotency-keys), against Redis 7 in a container. Versions: idempotency-kit 0.3.0, redis 8.1.0, Python 3.13.

## What the key promises

The contract, from the client's side, is short. If I send the same request twice with the same key, the effect happens once, and I get the same response both times. That is what lets a client retry a `POST` on a timeout without wondering whether the first one went through: the retry either replays the answer or produces it, and either way there is one charge.

Notice that the promise has two halves and that they are usually implemented in the wrong order. "The same response both times" is a cache. "The effect happens once" is a concurrency guarantee. A cache gives you the first half for free, and it gives you the second half only in the case that never needed it, where the second request arrives after the first one is done. The interesting request is the one in flight.

## Measured: the request that is still running

The provider takes 300 ms to charge a card. The client sends a charge, and 50 ms later, having timed out on its side, sends the identical request with the identical key. Three implementations, same store, same key:

```text
in_flight='run'    (a result cache)         responses=['ch_1', 'ch_1']                     charges made=['ch_1', 'ch_2']
in_flight='wait'   (the default)            responses=['ch_1', 'ch_1']                     charges made=['ch_1']
in_flight='raise'  (409 for the second)     responses=['ch_1', 'IdempotencyInProgressError'] charges made=['ch_1']
```

Look at the first row carefully, because it is the one that looks correct. Both callers got `ch_1`. The client is happy; the response is consistent; every assertion on the response passes. The provider charged the card twice. The second request found no record, because the first had not finished writing one, ran the charge, and then lost the race to store the result, so it read the winner's record and returned that. Consistent responses, duplicate effect. This is what "the part everyone gets wrong" means: it is not visible from the outside, it is visible on the card statement.

The second row is the fix, and it is a reservation. Before running the action, the coordinator writes a *pending* marker under the key with a short lease. The second caller finds the marker, knows an identical request is in flight, and waits for its result instead of producing one. Both callers get `ch_1`, the provider charged once, and the client that retried never learns it retried.

The third row is the same reservation with the other answer to "someone is already doing this": fail fast. The second caller gets an error that an HTTP layer maps to `409 Conflict`, which is what Stripe does, and which is the right choice for a public API where the caller should not be holding a connection open while somebody else's request runs. Internal callers usually prefer to wait. Both are correct; both are one setting; the cache is neither.

## It is still not a lock

The reservation looks like a lock and people call it one, and then they try to use it as one, so it is worth saying what it is not. A lock protects a resource for a duration. A reservation protects a *key* for the length of one attempt: it says "this request is being handled" and nothing about the order, the account balance, or anything else two different keys might contend for. Two requests with two keys that both charge the same card go through in parallel, as they should; the key is the client's statement that these two are the same request, not a claim on the card.

The lease is what keeps it from becoming a lock by accident. A pending marker with no expiry is a key wedged forever by a worker that died mid-charge. With a lease, an expired marker counts as absent, the next caller takes the key and runs the action, and the worst case is the old at-least-once behaviour for one request whose worker crashed, which is a case where the truth was unknowable anyway. The lease has to outlive the slowest honest attempt, and thirty seconds is the usual default.

## The key is not the request

The second thing a cache gets wrong is quieter. A key identifies a request; it does not describe one. A client that derives its key from the order id, which is the natural thing to do, and then makes a *different* request against the same order, has reused a key by mistake, and a store keyed on the key alone answers with the first request's result:

```text
same key, same amount     -> replayed ch_1, charges made=1
same key, amount 5        -> IdempotencyKeyReuseError, charges made=1
```

The fix is a fingerprint stored beside the result: a hash of the parts of the request that make it that request. A hit with a matching fingerprint replays. A hit with a different one is refused, with both fingerprints on the error, and the HTTP layer maps it to `422`, which is again what Stripe does: keys are for identical requests. What goes into the fingerprint is a per-operation decision, because a request also carries things that legitimately differ between honest retries, a timestamp, a trace id, and a fingerprint over all of them would refuse the retries the key exists to allow. Name the fields, hash those.

## Failures are not cached, and neither is the store

Two smaller rules that a result cache also tends to get wrong.

An action that raises must leave nothing behind, so that the retry runs it again:

```text
first call  -> provider timed out
second call -> ch_1, charges made=1
```

The pending marker is released when the action fails; the second call finds no record and charges once. Caching a failure would turn a transient provider timeout into a permanent "this order cannot be charged" for the key's lifetime, which is the opposite of what a retry is for.

And the store itself can be down. This is the design decision that a library cannot make for you, and the one I would want a team to make out loud:

```text
Redis unreachable -> the action ran anyway: ch_1, charges made=1  (availability over exactly-once, by design)
```

With the store gone there is no way to know whether this key was seen before. Fail closed and every write in the system stops until Redis is back; fail open and the operation runs, with the risk that it ran before. The library fails open, logs and counts the storage error, and leaves the choice of turning that into a hard failure to the caller who knows what the operation costs to repeat. For a cache invalidation, open is obviously right. For a card charge, it depends on whether the provider deduplicates on its own key, which the good ones do, and the honest answer is to pass the key downstream too.

## Scope and lifetime

A few decisions that are settings rather than code, but that every implementation has to make:

- **Scope.** A key is unique per operation, not per system. The same key under `order.create` and under `order.cancel` are two records, so a client may reuse one key across a workflow's steps. Per user or per tenant scoping is the caller's job: put the tenant in the key.
- **Lifetime.** A record has to outlive the longest plausible retry, which for a client that retries on timeouts is minutes, and for a client that retries on a crashed batch job is a day. Twenty-four hours is a common default; the floor is a minute, because a shorter record than that cannot outlive the request it was written by.
- **Size.** The key is at most 255 characters and the stored result is JSON, so a response that is too large to store is a response that should not be idempotent-cached at all. Store a reference and fetch it on replay.

## The shape

The whole thing, on a use case:

```python
from idempotency_kit import AsyncIdempotencyCoordinator, IdempotencyDomainService, PydanticResultAdapter, async_idempotent
from idempotency_kit.infra.storage.redis.aio import RedisAsyncIdempotencyRepository

coordinator = AsyncIdempotencyCoordinator(
    RedisAsyncIdempotencyRepository(redis, key_prefix="idempotency:"),
    IdempotencyDomainService(default_ttl_minutes=60 * 24),
    in_flight="wait",                       # or "raise" for a public API: 409 for the second caller
    in_flight_lease_seconds=30,             # longer than the slowest honest attempt
)


class ChargeOrder:
    def __init__(self, coordinator: AsyncIdempotencyCoordinator) -> None:
        self.coordinator = coordinator

    @async_idempotent(
        operation="payment.charge",
        adapter=PydanticResultAdapter(Charge),
        infra_param="coordinator",
        fingerprint_params=("order_id", "amount"),   # the parts of the request that make it this request
    )
    async def execute(self, order_id: str, amount: int, *, idempotency_key: str | None = None) -> Charge:
        return await self.provider.charge(order_id, amount, idempotency_key=idempotency_key)
```

Three decisions are visible in it: what the second concurrent caller gets, how long a crashed worker can hold a key, and which arguments make two requests the same. The fourth, what happens when Redis is gone, is the default and is documented as one. The provider call at the bottom passes the key downstream, because the provider has its own idempotency layer and the two together are what "once" actually means across a network.

That library is [idempotency-kit](https://bedrock-python.github.io/idempotency-kit/), and 0.3.0 is the release that turned its result cache into a reservation, after the first table in this post was run against the version before it.

The point was the first table. Consistent responses, two charges.
