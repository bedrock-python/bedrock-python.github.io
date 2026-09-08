---
date: 2026-09-07
authors:
  - alex
categories:
  - Design
tags:
  - clientwright
  - retries
  - circuit-breaker
  - reliability
  - microservices
---

# Retries can make an outage worse: designing a retry budget

<div class="bdr-post__hero" data-bdr-post="2026-09-07-retries-can-make-an-outage-worse" role="img" aria-label="Retries at every hop multiply; a budget turns the flood back into a trickle" markdown="0"></div>

Three retries at every hop of a five-service call is not resilience. It is a multiplier, and it multiplies hardest exactly when the bottom service is failing, which is the one moment it can least afford the traffic. Everybody knows this in the abstract and configures `max_attempts=3` anyway, because three is a small number. So I built a chain of services that each retry three times, put a failing origin at the bottom, sent ten requests in at the top, and counted what arrived at the bottom. Eight hundred and ten. This post is that measurement, the two mechanisms that turn it back into a small number, and the case where the right answer is to let the caller fail.

<!-- more -->

The numbers come from [the post's lab script](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-retry-budget), against an in-process origin that fails on request. Versions: clientwright 0.2.2, httpx 0.28.1, Python 3.13.

## The arithmetic

A retry is a bet that the next attempt will do better than the last one. When a dependency is slow because it is overloaded, the bet is wrong in a specific way: every retry is one more request to the thing that is overloaded, sent by a caller who has just learned that it is. One caller retrying three times triples its share of the load. Fifty callers retrying three times triple the whole load. And that is one hop.

In a chain, the attempts multiply. A request enters at the top with three attempts. Each attempt becomes a call to the next service, which makes three attempts of its own, and so on down. Four layers of three attempts is `3⁴ = 81` requests at the bottom for one at the top, if nothing stops it. Nothing stopping it is the default.

## Measured: one hop

Fifty concurrent callers, one origin, and the origin answers `503` to everything:

```text
no retries                                   origin saw   50 requests (1.00x)  callers ok=0
max_attempts=3, no budget                    origin saw  150 requests (3.00x)  callers ok=0
max_attempts=3, budget_ratio=0.1 (default)   origin saw   60 requests (1.20x)  callers ok=0  retries refused by budget=50
```

The first two rows are the arithmetic. Nobody succeeded either way, because the origin was down, and the second configuration sent it three times the traffic to find that out. The third row is a retry budget: the same three attempts allowed, but the retries, as distinct from the first attempts, are drawn from a per-origin allowance of about ten per cent of the request rate. Fifty first attempts, ten retries, forty refused, and a counter that says so. The origin saw a twenty per cent bump instead of a threefold one.

That is what a budget is: a cap on the *ratio* of retries to requests, per origin, refilled by traffic. It does not say how many times one call may retry. It says how much of the total load may be retries, which is the number the origin cares about.

## When the budget is invisible, and when it hurts

A budget is only worth having if it costs nothing in the case retries exist for. Fifty callers, five of which hit a request that fails once and then recovers:

```text
max_attempts=3, no budget                    origin saw   55 requests (1.10x)  callers ok=50
max_attempts=3, budget_ratio=0.1             origin saw   55 requests (1.10x)  callers ok=50
```

Identical. Five retries out of fifty requests is inside the allowance, all five callers got their answer on the second try, and the budget never refused anything. This is the shape of a healthy system with a flaky dependency, and the budget does not know it is there.

Now the case where it does:

```text
--- every one of the fifty callers fails twice, then recovers ---
max_attempts=3, no budget                    origin saw  150 requests (3.00x)  callers ok=50
max_attempts=3, budget_ratio=0.1             origin saw   60 requests (1.20x)  callers ok=0   retries refused by budget=50
```

Read the last column of the second row. With the budget, every caller failed. Without it, every caller succeeded, at the cost of three times the traffic. This is the trade a budget makes, and it should be made with eyes open: when *every* request needs two retries to succeed, the dependency is not flaky, it is down, and the retries that would have rescued each individual caller are collectively the storm that keeps it down. The budget chooses the origin's survival over the caller's success. The caller gets an error in a hundred milliseconds instead of a success after three attempts, and the origin gets a fifth of the load, which is the load under which it might recover. Whether that trade is right depends on what the caller does with the error, and a caller that shows a retry button to a human is the caller that should receive it.

## Measured: three services deep

Ten callers at the top of a chain of three services, each service with its own client retrying three times, and the origin at the bottom answering `503`:

```text
3 attempts per hop, no budget, no breaker    origin saw  810 requests (81.00x)  2.82s
3 attempts per hop, no budget, breaker on    origin saw   30 requests ( 3.00x)  0.31s
3 attempts per hop, budget on, breaker on    origin saw   20 requests ( 2.00x)  0.13s
```

The first row is the arithmetic made real: `3⁴` requests per caller, eight hundred and ten at the origin for ten at the top, and nearly three seconds of a dead dependency being hammered by callers who had been told it was dead, in triplicate, four layers deep.

The second row is a circuit breaker at every hop, with default settings. A breaker watches the outcomes of calls to one origin and, after enough consecutive failures, refuses further calls for a while without making them. It caught the storm after the first five failures at each hop and cut the multiplier from eighty-one to three. The breaker is the mechanism that works *after* the fact: it needs failures to count before it opens, and while it is counting, the retries flow.

The third row adds the budget. The breaker still opens, but the retries that would have been made while it was still closed are already bounded by the allowance, and the multiplier drops to two. The two mechanisms are complementary and neither replaces the other: the budget bounds the retries proportionally from the first request, the breaker stops the traffic altogether once the dependency has proven it is down.

## Where retries belong

The chain measurement suggests the rule that the arithmetic already implied. Retries multiply per layer, so the fewer layers that retry, the smaller the multiplier. The common advice is to retry at one layer only: the edge, which knows the user is waiting and can decide whether the whole request is worth another try, or the last hop, which is closest to the failure and can classify it. Every layer in between that retries adds a factor.

When more than one layer has to retry, because they are owned by different teams or the failure they retry is different, each one needs its own budget and its own breaker, and all of them need to spend the same deadline rather than their own timeouts, which is the subject of [the deadlines post](2026-09-06-timeouts-are-not-deadlines.md). And nothing here changes what may be retried at all: only calls whose repeat is safe, which is the subject of [the gRPC retries post](2026-09-07-safe-grpc-retries.md) and applies to HTTP just the same.

## The policy

```python
from clientwright import CircuitBreakerConfig, ClientConfig, RetryConfig, TimeoutConfig, build

config = ClientConfig(
    service_name="orders",
    timeout=TimeoutConfig(total=5.0),              # the deadline the attempts share
    retry=RetryConfig(
        max_attempts=3,                            # per call
        budget_ratio=0.1,                          # per origin: retries may be ~10% of requests
    ),
    circuit_breaker=CircuitBreakerConfig(fail_threshold=5, recovery_timeout=30.0),
)
client = build("httpx", config)
```

Three numbers. The attempts per call, which is the one everybody sets. The share of traffic that may be retries, which is the one that bounds the storm from the first request. The failures before the breaker opens, which is the one that stops it once the dependency has proven it is down. The budget is on by default at ten per cent, and turning it off, `budget_ratio=None`, is how the first row of every table above was produced.

That client is [clientwright](https://bedrock-python.github.io/clientwright/guide/retries/), whose retry policy keeps a per-origin token bucket in the application-scoped runtime, refuses a retry the bucket cannot pay for, and counts the refusal as `http_client_retry_skipped_total{reason="budget"}` so the dashboard shows the storm that did not happen.

The point was the first row of the last table. Eight hundred and ten, for ten.
