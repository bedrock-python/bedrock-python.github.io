---
date: 2026-09-07
authors:
  - alex
categories:
  - Design
tags:
  - servicewright
  - kubernetes
  - health-checks
  - graceful-shutdown
  - lifecycle
  - asyncio
---

# Warmup, readiness and liveness are three different things

Most services answer all three questions with one handler, usually one that pings the database. Each conflation has its own outage. A liveness probe that checks the database restarts every pod in the fleet during a database blip. A readiness probe that never goes false sends traffic to a pod that is shutting down. A warmup folded into readiness serves cold caches, or, more often, gets the pod killed before it finishes. I put a warmup, a dependency outage and a `SIGTERM` through one service and watched the two probes and a route disagree, on purpose.

<!-- more -->

The numbers come from [the post's lab](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-warmup-readiness-liveness), which polls both probes and a route every hundred milliseconds through a whole lifecycle. Versions: servicewright 0.10.0, FastAPI 0.141.1, Python 3.13.

## The whole life of a pod, in six transitions

```text
      0.0 s  livez=ConnectError  readyz=ConnectError  /cached=ConnectError
      3.3 s  livez=200           readyz=200           /cached=200
      6.1 s  livez=200           readyz=503           /cached=200
      9.2 s  livez=200           readyz=200           /cached=200
     11.2 s  livez=200           readyz=503           /cached=200
     13.2 s  livez=ConnectError  readyz=ConnectError  /cached=ConnectError
```

A three-second warmup, then a Redis outage from six to nine seconds, then `SIGTERM` at eleven. Every line where the columns differ is a decision somebody has to make.

## Warmup is not readiness, and neither is it liveness

For the first 3.3 seconds nothing answered anything: not the route, not readiness, not liveness. The listener is bound after the warmup, because a service that accepts connections before its caches, pools and clients are primed is a service that serves errors.

That is the right ordering and it has a consequence people meet the hard way: **during warmup, an HTTP liveness probe fails, because there is nothing to answer it.** Not "returns 503" — the connection is refused. A liveness probe with `failureThreshold: 3` and `periodSeconds: 5` kills a pod whose warmup takes longer than fifteen seconds, and it does it again to the replacement, and again, and the deployment never comes up. The symptom is a `CrashLoopBackOff` with no error in the application log, because the application was doing exactly what it was told.

The answer is a `startupProbe`: it gates the other two, it may be given a long failure budget, and once it passes, liveness takes over with its short one. Warmup is a phase, not a state, and it is the only one of the three that has a natural end.

Two more things follow from the ordering. A warmer that fails must abort startup rather than let the service serve cold — the pod is replaced instead of quietly serving misses. And a `SIGTERM` during warmup must skip straight to cleanup: a rollout that changes its mind about a pod should not have to wait out a sixty-second cache prime first.

## Liveness is about the process, not the dependencies

From 6.1 to 9.2 seconds Redis was gone. Readiness went to 503; liveness stayed 200; the route that does not need Redis kept serving:

```text
      6.1 s  livez=200  readyz=503  /cached=200
```

If liveness had included the Redis check, every pod in the deployment would have failed liveness at the same moment, and Kubernetes would have restarted all of them, at the same time, while their shared dependency was already unhealthy. The restarts do not fix Redis. What they do is throw away the warm caches and the in-flight requests of every replica, so when Redis comes back the fleet is cold, and a stampede of newly started pods hits it at once.

So the rule is: **liveness answers "is this process wedged", and nothing else.** Deadlocked event loop, a thread pool that no longer completes anything, a state the process cannot leave. If a restart would not fix it, it does not belong in liveness. That makes liveness almost boring — it is healthy while the loop turns — and boring is correct.

Readiness is the opposite: it is allowed to depend on everything the pod needs to serve. But not on everything the pod *has*. In this run the route kept working while readiness was false, because it does not need Redis, and a readiness check drawn too widely takes a pod out of rotation for endpoints it could still serve. Where that distinction matters, per-service readiness beats one global flag; where it does not, one flag is simpler and the trade is explicit.

There is a version of this that goes further and is worth naming: if *every* replica fails readiness for a shared dependency, you have taken the whole service down. A cache that could have been bypassed, a recommendation service that could have degraded to a default, now return nothing at all, because the load balancer has no healthy pod to send to. Readiness on a hard dependency is right; readiness on a soft one is an outage with extra steps. That decision is per use, which is [the Redis fail-open argument](2026-09-07-when-should-redis-fail-open.md) in a different place.

## Readiness has to go false before the pod stops serving

At `SIGTERM` the sequence is the one that matters for a rollout:

```text
    SIGTERM at 11.1 s, process exited at 13.3 s with code 0
    readyz stopped saying 200 at 11.2 s (0.1 s after SIGTERM)
    the route stopped answering at 13.2 s (2.1 s after SIGTERM)
    requests kept succeeding for 2.0 s after readiness went false
```

Readiness went false within a tenth of a second, and the service kept serving for two more seconds. That gap is the entire point of readiness during shutdown, and it exists because Kubernetes does not remove a pod from its Service the moment it sends `SIGTERM`. The endpoint removal propagates to kube-proxy, the ingress and every client's connection pool, and while it propagates, requests keep arriving at a pod that has been told to stop.

A service that closes its listener on `SIGTERM` turns each of those in-flight requests into a connection reset, which the caller sees as a 502 and, if it retries, sends into another pod that may also be shutting down. That is the "why does every deploy produce a spike of 502s" question, and the answer is almost never in the application's error log.

So the order is: flip readiness false, keep serving for as long as endpoint removal takes, then close the listener and drain what is in flight. The delay is not a guess, it is a property of your cluster, and it is the number to measure once and set: how long between a pod's readiness going false and traffic actually stopping. The rest of the arithmetic — drain grace, `terminationGracePeriodSeconds`, the longest request — is in [the shutdown post](2026-09-07-graceful-shutdown-is-a-protocol.md).

## The three, in one table

| | Liveness | Readiness | Startup |
|---|---|---|---|
| Asks | is this process wedged | should traffic come here now | has initialisation finished |
| Includes dependencies | no | the ones this pod needs to serve | no |
| During warmup | not answerable yet | false | the only probe that runs |
| During a dependency outage | true | false | done |
| After SIGTERM | true, until the process exits | false immediately | done |
| A failure means | restart the pod | stop routing to it | keep waiting, then restart |

The column that surprises people is the last row of the readiness column: a readiness failure is *not* an error. It is a routing decision, and a pod that is legitimately not ready — warming, draining, waiting for a dependency — is behaving correctly. Alerting on readiness failures directly produces noise on every deploy. Alert on the fleet-level consequence: no ready replicas, or fewer than you need.

## The pieces

The lifecycle above is [servicewright](https://bedrock-python.github.io/servicewright/): warmers that run before anything binds, a readiness flag that flips true only after every entrypoint is bound and false before any drain, a health registry where liveness deliberately ignores your checks and readiness is the flag plus all of them, and a configurable delay between readiness going false and the listener closing. The probes are served by whichever adapter you use; the ordering is the same for HTTP, gRPC and workers, which is the point of having the lifecycle in one place rather than in each framework's lifespan.

Three questions, three answers, six transitions. Answering all of them with one database ping gets you a restart loop and a spike of 502s on every deploy.
