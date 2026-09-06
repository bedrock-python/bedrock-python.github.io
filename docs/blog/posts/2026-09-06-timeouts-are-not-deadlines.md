---
date: 2026-09-06
authors:
  - alex
categories:
  - Design
tags:
  - deadline-budget
  - clientwright
  - grpc-client-kit
  - timeouts
  - deadlines
  - httpx
  - grpc
  - microservices
---

# Timeouts are not deadlines: how latency budgets break across microservices

Every service I have run had a timeout on every outgoing call, and every one of them still managed to take longer than any number in its config. That is not a bug in any HTTP client. The number in the config is a timeout, the number the SLO talks about is a deadline, and the two only look alike. This post measures the gap three times: on one HTTP call, on one HTTP call with retries, and across a chain of three gRPC services where a card gets charged a full second after the customer saw an error. Then the fix, which is arithmetic, and the three places the arithmetic has to live.

<!-- more -->

Every number below was measured on one laptop, with the servers on loopback, using the scripts in [the post's lab directory](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-06-timeouts-are-not-deadlines). Package versions: httpx 0.28.1, grpcio 1.83.1, deadline-budget 0.1.2, clientwright 0.2.0, grpc-client-kit 0.1.0, Python 3.13.

## A timeout limits an operation

Here is a server that answers immediately and then takes four seconds to finish. It sends the status line and headers at once, then one byte of body every half second, eight times:

```python
async def drip(reader, writer):
    await reader.readuntil(b"\r\n\r\n")
    writer.write(b"HTTP/1.1 200 OK\r\nContent-Length: 8\r\n\r\n")
    for _ in range(8):
        await asyncio.sleep(0.5)
        writer.write(b"x")
        await writer.drain()
    writer.close()
```

And here is a client that has been told it may wait one second:

```python
async with httpx.AsyncClient(timeout=1.0) as client:
    response = await client.get(url)
```

| Call | Result | Took |
|---|---|---|
| httpx, `timeout=1.0`, body drips | `200`, 8 bytes | 4.02 s |
| httpx, `timeout=1.0`, headers stall for 4 s | `ReadTimeout` | 1.00 s |

The first row is the whole post in miniature. `timeout=1.0` in httpx is four numbers, one each for connect, read, write and acquiring a pooled connection, and the read timeout is the longest the client will wait *between two chunks of data*. Every chunk here arrives inside half a second, so the clock resets eight times and never fires. The second row shows the same number doing its job: a server that says nothing for four seconds is caught at one. Same config, same client, a factor of four between the two, and neither is wrong. The timeout is behaving exactly as documented. It measures patience, not time.

A deadline is a point on the clock. In the standard library it is one line:

```python
async with asyncio.timeout(1.0):
    response = await client.get(url)
```

| Call | Result | Took |
|---|---|---|
| httpx inside `asyncio.timeout(1.0)`, body drips | `TimeoutError` | 1.00 s |

Same dripping server, cancelled at one second because the clock is outside the call and nothing inside the call can reset it. That is the entire difference between the two words. Everything else in this post is what happens when the difference is ignored at a larger scale.

## Retries multiply it

Every codebase has this loop somewhere, usually written on the day a downstream service first flaked:

```python
async with httpx.AsyncClient(timeout=1.0) as client:
    for attempt in range(3):
        try:
            return await client.get(url)
        except httpx.TimeoutException:
            continue
```

Against a server that accepts the connection and never answers, it behaves like this:

| Policy | Result | Took | Requests that reached the server |
|---|---|---|---|
| loop of 3, `timeout=1.0` each | `ReadTimeout` | 3.04 s | 3 |

The author of that loop believed the call was bounded at one second. The caller of the function waited three. The server, which was already in trouble, received three requests where it used to receive one. Multiply that by every hop that has the same loop and you have the retry storm that turns a slow dependency into an outage, but that is a separate post.

The fix is not a smaller number. It is one clock for the whole logical call, with the attempts, the backoff sleeps and any redirects all spent out of it. That is how [clientwright](https://bedrock-python.github.io/clientwright/) spells a timeout, and it is the reason `TimeoutConfig` has a field called `total`:

```python
from clientwright import ClientConfig, RetryConfig, TimeoutConfig, build

config = ClientConfig(
    service_name="orders",
    timeout=TimeoutConfig(total=1.0),
    retry=RetryConfig(max_attempts=3),
)
client = build("httpx", config)         # a real httpx.AsyncClient, not a wrapper
response = await client.get(url)
```

| Policy | Result | Took | Requests that reached the server |
|---|---|---|---|
| loop of 3, `timeout=1.0` each | `ReadTimeout` | 3.04 s | 3 |
| `total=1.0`, 3 attempts allowed | `DeadlineExceededError` | 1.00 s | 1 |
| `total=3.0`, `read=1.0`, 3 attempts allowed | `DeadlineExceededError` | 3.00 s | 3 |

The second row is what the loop's author thought they had written: one second, then an answer, whatever the retry policy says. The third row is the same three attempts as the loop, but now the three seconds is a number you chose, written in the config, and the retry policy fits inside it. The difference between rows one and three is not the behaviour. It is who decided the total: you, or the multiplication.

One honest note on the boundary. On httpx the engine sits in the transport, and the transport hands back a response once the headers are in, so the total covers connecting, every attempt, every backoff sleep and every redirect hop up to the response headers. The adapter's capability record says so, `boundary=headers`, and I checked it against the dripping server from the first section: clientwright's `total=1.0` let it finish in 4.01 s, exactly like bare httpx. A body that drips after the headers is still httpx's read timeout. If the body is the slow part, `asyncio.timeout` around the call is still the tool.

## Across a hop, the timeout becomes a lie

Now three services. A gateway calls Orders and gives it two seconds. Orders calls Inventory to reserve stock, then Billing to charge the card, in that order. Each of those takes a second and a half, and each of them is a commit: once started, it completes, because that is what a database write or a payment API does whether or not anyone is still listening. Orders' gRPC clients are configured the way most are, with a per-call timeout of five seconds.

Here is what each service saw, timed from the moment the gateway made its call. The deadline column is what the server read from its own request context, so nothing here is an assertion about the client's internals:

```text
fresh 5 s timeout on every call

  0.00 s  gateway    calls orders, timeout 2.0 s
  0.00 s  orders     deadline seen 2.00 s
  0.00 s  inventory  deadline seen 5.01 s
  1.50 s  inventory  reserve completed
  1.51 s  billing    deadline seen 5.00 s
  2.01 s  gateway    DEADLINE_EXCEEDED
  2.01 s  orders     cancelled
  2.01 s  billing    caller gone, but the charge is already running
  3.01 s  billing    charge completed
```

Read the Billing lines. It was called at 1.51 s and told it had five seconds. The request that was paying for it had 0.49 s left. Billing did what it was told and finished the charge at 3.01 s, a second after the customer saw an error, and the customer did what customers do with an error on a payment page. The five-second timeout was true about Orders' config and false about the request, and Billing had no way to tell the difference.

The same chain, with one change: Orders takes the deadline it was given and carries it into every call it makes.

```text
the gateway's 2 s carried down the chain

  0.00 s  gateway    calls orders, timeout 2.0 s
  0.00 s  orders     deadline seen 2.00 s
  0.00 s  inventory  deadline seen 2.00 s
  1.50 s  inventory  reserve completed
  1.51 s  billing    deadline seen 0.49 s
  1.51 s  billing    refuses: 1.5 s of work does not fit in 0.49 s
  1.51 s  orders     DEADLINE_EXCEEDED
  1.51 s  gateway    DEADLINE_EXCEEDED
```

The request still fails. It fails half a second sooner, nobody is charged, and the reason is on the wire: Billing was told the truth, that it had 0.49 s, and a service that knows its charge takes 1.5 s can refuse before it starts. A fresh timeout tells the callee how patient the caller's configuration is. A deadline tells it how much time the request actually has. Only one of those is information the callee can act on.

Two things about that log are worth saying plainly. grpc.aio does cancel the server-side handler when the caller's deadline passes, and the log shows it doing so at 2.01 s in the first run. What it cannot cancel is a charge that has already been sent, which is why the fix has to happen before the call, not after. And the safety margin between 1.51 s and 2.00 s in the second run is not luck: Orders answered with time to spare because the refusal cost nothing.

## Where the deadline lives

The rule that makes the second log possible is simple to state. The deadline is created once, where the request enters the system. At every hop, the callee reads what arrived and rebuilds its own budget from it. Each outgoing call is issued with the smaller of what the client is configured for and what the request has left.

For gRPC, the deadline as it crossed the wire is `context.time_remaining()`. This is Orders' handler from the second run:

```python
from deadline_budget import BudgetContext
from grpc_client_kit import DeadlineBudgetConfig, TimeoutConfig, build_interceptors, use_budget

chain = build_interceptors(
    timeout=TimeoutConfig(default=5.0),       # the client's own ceiling per call
    deadline_budget=DeadlineBudgetConfig(),   # trimmed to what the request has left
)

class Orders:
    async def Submit(self, request, context):
        left = context.time_remaining()       # None when the caller sent no deadline
        budget = BudgetContext.create(total_seconds=left) if left else None
        with use_budget(budget):
            await self.inventory.Reserve(request)
            await self.billing.Charge(request)
```

The budget's clock starts on the line that creates it, and every call made inside the `with` block asks it how much is left before dialing. Inventory was issued with 2.00 s, not 5, because two is smaller. Billing was issued with 0.49 s because that is what remained after Inventory. A budget can only tighten a call, never loosen one: I also ran a 50-second budget against the same 5-second configuration, and the server saw 5.00 s.

HTTP has no deadline in the protocol, so the number rides in a header. The client stamps what is left of the budget, in whole milliseconds, before each attempt:

```python
from clientwright import AdapterDeps, ClientConfig, RetryConfig, TimeoutConfig, build
from clientwright.contrib.deadline import AmbientDeadlineSource, use_budget

config = ClientConfig(
    service_name="orders",
    timeout=TimeoutConfig(total=10.0),        # the client's own opinion
    retry=RetryConfig(max_attempts=3, initial_backoff=0.3),
    deadline_header="X-Deadline-Ms",
)
client = build("httpx", config, AdapterDeps(deadline_source=AmbientDeadlineSource()))

with use_budget(BudgetContext.create(total_seconds=2.0)):
    await client.get(inventory_url)           # first attempt gets a 503, the retry succeeds
    await do_our_own_work()                   # half a second
    await client.get(inventory_url)
```

The inventory service logged the header on each of the three requests it received:

```text
attempt 1: X-Deadline-Ms: 1999
attempt 2: X-Deadline-Ms: 1685
attempt 3: X-Deadline-Ms: 1179
```

The config says ten seconds. Nobody downstream ever hears that number. The first attempt carries the full budget, the retry carries the budget minus the backoff, and the second call carries what our own work left. On the receiving side the first line of the handler is the same move as the gRPC one: read the header, build a budget from it.

```python
budget = DeadlineBudget(total_seconds=int(headers["X-Deadline-Ms"]) / 1000, safety_margin=0.2)
```

Notice what does not travel: the budget object. It holds a reading of a monotonic clock whose zero point means nothing in another process. Only the number crosses, and the callee's budget starts after transit, so it is always a little shorter than what the caller had. That is the safe direction to be wrong in.

## The safety margin

The arithmetic has one more term, and it is the one that separates a request that fails cleanly from one that fails at the worst possible moment. The last hop has to stop early enough to roll back its transaction and serialise an error response. If it is granted every remaining millisecond, it will be mid-rollback when its own caller gives up.

The whole of the budget calculation is this:

```python
remaining = (total_seconds - safety_margin) - elapsed
available = max(remaining - reserve_for_next, min_timeout)
return min(available, cap)
```

`safety_margin` is what the service keeps for itself at the end. `reserve_for_next` is what one call leaves for the call after it. `min_timeout` is a floor, because a three-millisecond timeout is not a timeout, it is a guaranteed failure that still costs a round trip. The floor means the last call can be granted slightly more than the budget has, which is what the margin pays for. Every one of those is a number you decide, and none of them exist in a config that has only `timeout=5.0`.

## What changed in the code

Before, Orders had five timeouts in five places, each true about the client it belonged to and none of them true about the request. After, it has one number, created where the request enters, that every client reads before it dials. That is the only structural change, and it is the one that let Billing refuse.

The arithmetic lives in [deadline-budget](https://bedrock-python.github.io/deadline-budget/), which does exactly that and nothing else: no timers, no tasks, no context variable, no transport, no dependencies. It takes a total and tells you, at each call, how many seconds that call may have. The two clients that read it are [grpc-client-kit](https://bedrock-python.github.io/grpc-client-kit/guide/deadlines/), whose interceptor trims every outgoing RPC to the budget, and [clientwright](https://bedrock-python.github.io/clientwright/guide/deadline-budget/), whose engine does the same for httpx, aiohttp, requests and urllib3 while leaving you the native client. Both are optional extras on their side, and both accept any object with `remaining()` and `expired()` if you already track deadlines your own way.

The point was never the libraries. It was the log where Billing says "0.49 s, no".
