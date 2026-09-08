---
date: 2026-09-07
authors:
  - alex
categories:
  - Design
tags:
  - clientwright
  - circuit-breaker
  - retries
  - reliability
  - httpx
---

# Circuit breakers should be per origin, not per client

<div class="bdr-post__hero" data-bdr-post="2026-09-07-circuit-breakers-should-be-per-origin" role="img" aria-label="One breaker per upstream, not one breaker for the client" markdown="0"></div>

A circuit breaker is the simplest reliability pattern to explain and the easiest to key wrong. The explanation fits in a sentence: after enough failures, stop calling for a while, then probe. The mistake fits in a variable name: the counter lives on the client, and the client talks to three services. One of them goes down, the counter fills, the breaker opens, and the two healthy services go dark with it. I have shipped that breaker, and I measured it again for this post: one client, three upstreams, one of them failing, ten rounds of traffic. The breaker keyed on the client refused half the requests to the two services that were fine.

<!-- more -->

The numbers come from [the post's lab script](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-circuit-breakers-per-origin), against three in-process origins. Versions: clientwright 0.2.2, httpx 0.28.1, Python 3.13.

## Measured: one counter, three upstreams

An orders service calls three upstreams through one HTTP client: `stock`, `pricing` and `reviews`. `reviews` is down and answers `503` to everything. The traffic goes round-robin, ten rounds, thirty calls. First with a breaker written the way they usually are, a window of the last twenty outcomes with a threshold of five failures, one window for the client:

```text
breaker keyed on the client (hand-rolled)
    stock      {'200': 5, 'refused by breaker': 5}
    pricing    {'200': 5, 'refused by breaker': 5}
    reviews    {'503': 5, 'refused by breaker': 5}
```

Five failures from `reviews` opened the circuit, and from then on the client refused everything, including the two upstreams that had answered `200` to every request they were given. The service that depended on this client lost stock and pricing for the duration of the recovery timeout because a third, unrelated dependency was down. That is not a breaker protecting the system; it is a breaker converting one outage into three.

The same traffic, with the breaker keyed on the origin:

```text
breaker keyed on the origin (clientwright)
    stock      {'200': 10}
    pricing    {'200': 10}
    reviews    {'503': 5, 'refused by breaker': 5}
```

Five failures opened the circuit for `reviews` and nothing else. `stock` and `pricing` never noticed. The breaker's job is to stop traffic to a dependency that has proven it is down, and a dependency is an origin: a scheme, a host and a port. One upstream, one health verdict. A client is an implementation detail of the caller and has no health of its own.

## What counts as a failure

The second most common breaker mistake is counting the wrong things. Ten calls each against four kinds of answer, with a threshold of five:

```text
429 Too Many Requests      {'429': 10}
503 Service Unavailable    {'503': 5, 'refused by breaker': 5}
connection refused         {'ConnectError': 5, 'refused by breaker': 5}
404 Not Found              {'404': 10}
```

A `503` and a refused connection are the dependency telling you it cannot serve, and after five of them the breaker opens. A `429` is the dependency telling you it *can* serve and you are asking too fast; opening a breaker on it would turn a rate limit into an outage, and the right response is backoff, not silence. A `404` is an answer. It is the caller's bug or a business fact, and it trips nothing. The rule is that a breaker counts signs that the upstream is *unable* to answer: timeouts, connection and TLS and DNS errors, disconnects, protocol errors, and `5xx`. Everything else is the upstream working.

## One signal per logical call

The third mistake is subtle enough that the libraries get it wrong too: the breaker hears about every *attempt* instead of every *call*. Under a retry policy, one logical call can fail twice and succeed on the third attempt, and a breaker that counted attempts sees two failures where the caller saw a success. Ten calls to an upstream that fails twice per request and then answers:

```text
attempts counted (hand-rolled)         calls ok=2  refused by breaker=8
logical calls counted (clientwright)   calls ok=10 refused by breaker=0  attempts=30 circuit transitions=0
```

Thirty attempts, twenty of them failures, ten successful calls. The attempt-counting breaker opened after the second call and refused the other eight, on an upstream that answered every single request it was given three chances at. The one that counts logical calls, with the call's *final* outcome, saw ten successes and never moved. Retries are the caller absorbing a flaky upstream on purpose; a breaker that opens because of them defeats the retry policy it sits under. (The retry policy has its own limits, which are the subject of [the retry budget post](2026-09-07-retries-can-make-an-outage-worse.md).)

Cancelled calls are the third category and the one nobody counts: if the caller gave up, or a request deadline cancelled the task, the upstream did not fail and did not succeed. The breaker should be told to forget the call, which matters most in the half-open state, where a cancelled probe must release its slot without closing or reopening anything.

## The probe

Open is not forever. After the recovery timeout the next call becomes a probe: it goes out, and its outcome decides whether the circuit closes or opens again for another timeout. Everyone else keeps getting the fast local refusal until the probe answers, so a recovering upstream sees one request, not a stampede:

```text
 0.00 s  503
 0.00 s  503
 0.00 s  503
 0.01 s  refused, probe in 0.50s
 0.61 s  200
 0.61 s  200
```

Threshold three, recovery half a second. Three failures, one refusal that says exactly when the probe will happen, and after the timeout the first call through is the probe, finds the upstream recovered, and closes the circuit for the call after it. The refusal carries the time until the next probe, so a caller that wants to degrade gracefully knows how long to serve from cache.

## The configuration

```python
from clientwright import CircuitBreakerConfig, CircuitKey, ClientConfig, build

config = ClientConfig(
    service_name="orders",
    circuit_breaker=CircuitBreakerConfig(
        fail_threshold=5,            # consecutive tripping calls, final outcomes only
        recovery_timeout=30.0,       # seconds open before the next call becomes the probe
        half_open_max_calls=1,       # probes in flight at once
        key=CircuitKey.ORIGIN,       # the default: one verdict per scheme://host:port
    ),
)
client = build("httpx", config)
```

Two finer keys exist for the cases where one origin has parts with separate health, a per-route key for an upstream whose one slow endpoint should not take its fast ones down, and a per-method key. Both are narrower than the origin, never wider; there is no per-client key, because that is the one this post is about.

The breaker's state lives in the application-scoped runtime, not on the client object, which is the other half of getting it right: a breaker created per request has no memory and therefore no function, and a service that builds a fresh client for every request has, without knowing it, no breaker at all. It is on by default in [clientwright](https://bedrock-python.github.io/clientwright/guide/circuit-breaker/), with the origin as the key, `5xx` and transport failures as the triggers, and one signal per logical call.

The point was the first table's second column. Five refusals each, for two services that never failed.
