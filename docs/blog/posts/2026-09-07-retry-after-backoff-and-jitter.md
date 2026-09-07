---
date: 2026-09-07
authors:
  - alex
categories:
  - Tutorials
tags:
  - clientwright
  - httpx
  - retries
  - backoff
  - jitter
  - reliability
---

# Retry-After, backoff and jitter: what a production HTTP client actually does

The retry loop every codebase has is four lines: try, catch, sleep, try again. A production HTTP client's retry policy is a checklist of about eight decisions that the four lines silently made wrong. It sleeps a fixed time, so every caller that failed together retries together. It ignores the header where the server said when to come back. It retries a `POST` whose request may have been received. It retries a `500`, which is the server saying the request itself is broken. None of these is exotic; each one is a line in an incident review I have read. This post is the checklist, with each item measured against an origin built to misbehave in exactly one way.

<!-- more -->

The numbers come from [the post's lab script](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-retry-after-backoff-jitter), against an in-process origin. Versions: clientwright 0.2.2, httpx 0.28.1, Python 3.13.

## Honour Retry-After

When a server answers `503` or `429` with a `Retry-After` header, it is telling you the one thing a backoff formula can only guess: how long it needs. A client that computes its own delay anyway comes back too early and joins the problem. Two attempts against an origin that answers `503` with `Retry-After: 1`:

```text
respect_retry_after=True (default)   -> 503 after 1.02s (server asked for 1 s between attempts)
respect_retry_after=False            -> 503 after 0.06s (server asked for 1 s between attempts)
```

The first client waited the second it was asked for. The second waited its own fifty milliseconds and hit the server again while it was still recovering. The header replaces the computed backoff when it is present, and a cap on what the server may ask for (sixty seconds by default) keeps a misconfigured upstream from parking a request for an hour.

## Jitter, or the herd

Fifty callers hit the same failure at the same moment, because that is what a failure does: a dependency drops, and every request in flight fails at once. Each of them backs off and retries. With a fixed backoff they retry at the same moment too, and the retry is a second wave of exactly the size of the first:

```text
fixed backoff 0.3 s, no jitter   retries landed between 0.39s and 0.40s  (spread 12 ms, 49 within 10 ms of the median)
backoff 0.3 s, jitter=0.5        retries landed between 0.17s and 0.49s  (spread 314 ms, 5 within 10 ms of the median)
```

Forty-nine of fifty retries inside a ten-millisecond window: the dependency that just recovered from fifty simultaneous requests gets fifty simultaneous requests. With jitter, a random factor on each caller's delay, the same fifty retries spread across a third of a second, and the peak is five. Jitter costs nothing, the formula is one multiplication, and it is the difference between a retry policy that smooths a blip and one that repeats it. Exponential growth between attempts (0.1 s, 0.2 s, 0.4 s) does the same job over time that jitter does across callers, and both are on by default in a policy written for production; the four-line loop has neither.

## A read timeout is not a connection error

A connection error means the request never left: retrying it repeats nothing. A read timeout means the request was sent and the response did not come back in time, and there is no way to tell whether the server received it. For a `GET` the distinction does not matter. For a `POST` that charges a card, it is the whole question. A `POST` to an origin that takes two seconds to answer, with a read timeout of 0.3 s and three attempts allowed:

```text
POST, read timeout at 0.3 s, 3 attempts allowed -> ReadTimeout; the origin received 1 POST(s)
the same POST marked idempotent=True           -> ReadTimeout; the origin received 3 POST(s)
```

By default the client did not retry the `POST`, and the origin received it once. Marked idempotent by the caller, who is the only party that can know whether repeating it is safe, the client retried, and the origin received three requests that say `charge 10 EUR`. Both behaviours are correct; the mistake is a client that picks the second one without being told. The method decides the default (`GET`, `HEAD`, `PUT`, `DELETE`, `OPTIONS`, `TRACE` are idempotent by the RFC and `POST` is not), and the call site overrides it in either direction: a `POST` with an idempotency key may say so, and a `GET` with side effects may say it is not.

## What is retried at all

Six requests against six kinds of answer, three attempts allowed:

```text
GET 503          -> 503            attempts=3
GET 500          -> 500            attempts=1
GET 429          -> 429            attempts=3
GET disconnect   -> 200            attempts=2
POST 503         -> 503            attempts=1
DELETE 503       -> 503            attempts=3
```

A `503` is the server saying it cannot serve right now, and it is retried. A `500` is the server saying the request broke something, and retrying it is sending the same broken request to the same code; it is not retried by default, and the teams who make it retryable usually regret it during the next deploy. A `429` is retried, with the server's `Retry-After` if it sent one, and it never counts as a failure for the circuit breaker, because the server is up. A dropped connection is retried, and here the second attempt succeeded. And the `POST` with the same `503` that the `GET` and the `DELETE` retried is not retried, for the reason in the previous section.

The remaining gates are ones this table cannot show: a retry has to fit inside the call's total deadline, including its backoff sleep, or it is not attempted (the [deadlines post](2026-09-06-timeouts-are-not-deadlines.md)); a request body that cannot be replayed, a streaming upload, forbids every retry; and the origin's retry budget may refuse a retry that all of the above allowed (the [retry budget post](2026-09-07-retries-can-make-an-outage-worse.md)).

## The checklist

Every item above, as the configuration that makes it true:

```python
from clientwright import ClientConfig, RetryConfig, TimeoutConfig, build

config = ClientConfig(
    service_name="orders",
    timeout=TimeoutConfig(total=5.0),          # every attempt and every sleep fit inside this
    retry=RetryConfig(
        max_attempts=3,
        initial_backoff=0.1, multiplier=2.0,   # 0.1 s, 0.2 s, ... between attempts
        max_backoff=10.0,
        jitter=0.2,                            # ±20 %: no herd
        respect_retry_after=True,              # the server's number beats the formula
        retry_after_max=60.0,
        retryable_status={429, 502, 503, 504}, # 500 is not on this list on purpose
        # methods: the idempotent ones; a call site may say otherwise for one request
    ),
)
client = build("httpx", config)
```

The four-line loop has one of those nine decisions in it, the attempt count, and it usually gets that one wrong too. This configuration is the default of [clientwright](https://bedrock-python.github.io/clientwright/guide/retries/), spelled out; the only line a service normally changes is the total, and the only thing a call site normally adds is the idempotency of a `POST` it has made safe to repeat.

The point was the second table's first column. One request, or three requests that say charge.
