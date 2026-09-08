---
date: 2026-09-07
authors:
  - alex
categories:
  - Design
tags:
  - servicewright
  - kubernetes
  - graceful-shutdown
  - asyncio
  - fastapi
  - uvicorn
---

# Graceful shutdown in Kubernetes is a protocol, not a signal handler

<div class="bdr-post__hero" data-bdr-post="2026-09-07-graceful-shutdown-is-a-protocol" role="img" aria-label="Stop being routed first, then drain, then finish, then exit" markdown="0"></div>

Every web framework handles `SIGTERM`. It stops accepting connections, lets the requests already in flight finish, and exits cleanly. That is what "graceful" means in the changelog, and it is what I believed for years. Then I measured what happens to the requests that arrive in the second after the signal, which in Kubernetes is exactly the second in which they keep arriving, and the framework's graceful shutdown refused 44 of them. This post is that measurement, the four-step protocol a pod actually has to follow, the one step almost everyone skips, and the arithmetic that keeps the kubelet from killing you halfway through.

<!-- more -->

Every number below comes from [the post's lab directory](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-graceful-shutdown): two servers with the same two routes and a driver that plays Kubernetes against them. Versions: uvicorn 0.52.4, FastAPI 0.141.1, servicewright 0.10.0, httpx 0.28.1, Python 3.13.

## What Kubernetes actually does

When a pod is deleted, during a rollout or a scale-down, two things happen at the same time and neither waits for the other:

1. The pod is marked `Terminating`, and the endpoints controller removes it from the Service's endpoint list. That removal then propagates to every kube-proxy, every ingress controller and every service mesh sidecar in the cluster, each on its own schedule. Hundreds of milliseconds on a small cluster; several seconds on a large one.
2. The kubelet sends `SIGTERM` to the container's main process and starts the `terminationGracePeriodSeconds` clock. When it runs out, `SIGKILL`.

The word that matters is *propagates*. For some window after the signal, load balancers that have not yet heard the news keep routing new connections to the pod. A process that closes its listening socket the moment it gets `SIGTERM` refuses every one of them, and from the client's side that is a connection error on a healthy-looking service in the middle of a routine deploy. This is the 5xx blip on the dashboard during every rollout that nobody can explain, and it is not a bug in the load balancer. It is the pod leaving before the room has been told.

## The measurement

The lab has two servers with the same two routes: `/work`, which takes 20 ms, and `/slow`, which takes two seconds and stands in for the report, the export or the payment that is in flight when the signal lands. The driver starts a server, waits until it is ready, starts one `/slow` request, and then sends `SIGTERM` and starts the clock. From that moment it keeps sending one `/work` request every 20 ms for one second, playing a load balancer that has not yet heard about the removal, while polling the readiness endpoint every 50 ms. It counts what came back.

First, FastAPI under `uvicorn.run`, with uvicorn's own signal handling, the way most services ship:

```text
uvicorn, SIGTERM, then 1 s of traffic at one request per 20 ms
   0.00 s  SIGTERM sent
   0.00 s  readiness probe -> 200
   0.06 s  readiness probe -> refused
   1.90 s  in-flight /slow request -> ok
   2.40 s  process exited
  requests after SIGTERM: {'ok': 3, 'refused': 44, '5xx': 0, 'other': 0}
```

Read the two halves separately. The in-flight request finished: uvicorn waited two seconds for it, which is the graceful part and it works. But the listening socket closed within a hundred milliseconds of the signal, and every request the load balancer sent after that was refused at the TCP level. Forty-four of forty-seven. The readiness probe went from `200` straight to `refused`, so nothing ever told the load balancer to stop; the pod simply vanished from under it.

uvicorn is not doing anything wrong here. It cannot know that requests are still coming, because the only way to know that is to know how Kubernetes works, and a web server should not. The knowledge has to live one layer up, in the thing that runs the server.

## The protocol

Graceful shutdown in Kubernetes is four steps, in a fixed order, with a timing constraint across them. Two of the steps are the ones the framework already does. The other two are the ones it cannot.

**One: stop saying you are ready, and keep serving.** The moment the signal arrives, the readiness endpoint starts answering `503`. Nothing else changes. The listening socket stays open, requests are still accepted and answered, and the pod is, for the next few seconds, a healthy server that is telling everyone who asks that it is about to leave. This is the step that closes the window from the first section: the ingress controllers that poll readiness see the `503` and drop the pod on their own schedule, while the ones that only learn from the endpoint list get the time to hear it.

**Two: wait for the news to travel.** A fixed delay, sized to your cluster's propagation lag, during which step one holds. This is the step almost everyone skips, because nothing in the process needs it: the process would be perfectly happy to exit. The requests need it. The usual way to get it is a `preStop` hook in the manifest that sleeps for five seconds before the signal is even sent, and it works, but it lives in YAML rather than in the code, it delays the signal rather than flipping readiness, and every service in the fleet has to remember it independently.

**Three: drain.** Now close the listening socket, and let the requests already in flight finish, up to a grace period. This is the part uvicorn does well, and the only difference is when it starts.

**Four: clean up, in reverse order.** Stop the servers, run the shutdown hooks while the application scope is still open, close the database pools and the clients, flush the tracer, exit `0`. Each of those has a budget too, because a pool that hangs on dispose must not be the reason the kubelet's clock runs out.

The constraint across them:

```text
terminationGracePeriodSeconds  >  delay + drain grace + cleanup budget + slack
```

Get it wrong and the kubelet sends `SIGKILL` in the middle of step three, and the in-flight request that step three exists to protect dies anyway.

## The same measurement, with the protocol

servicewright runs a service through exactly this sequence: `serve()` returns when the stop event fires while the server is still accepting, the Host flips readiness to false, waits `drain_delay_seconds`, then drains every entrypoint in reverse order, stops them, and runs cleanup within `cleanup_timeout_seconds`. The service definition is the two routes under a FastAPI entrypoint and three numbers:

```python
from servicewright import AppSpec, Service, run_sync
from servicewright.adapters.fastapi import FastApiEntrypoint, HttpConfig

spec = AppSpec(
    service_name="shutdown-lab",
    create_container=lambda settings: Container(),
    drain_delay_seconds=1.5,     # step two: how long the news takes to travel in this cluster
    drain_grace_seconds=10.0,    # step three: how long in-flight work may take
    cleanup_timeout_seconds=5.0, # step four: per teardown step
)
service = Service(spec, entrypoints=[FastApiEntrypoint(config=HttpConfig(port=8000), routers=(router,))])
run_sync(service, Settings())
```

The same driver, the same second of traffic:

```text
servicewright, drain_delay_seconds=1.5
   0.00 s  SIGTERM sent
   0.00 s  readiness probe -> 503
   1.90 s  in-flight /slow request -> ok
   2.41 s  process exited with 0
  requests after SIGTERM: {'ok': 47, 'refused': 0, '5xx': 0, 'other': 0}
```

Readiness answers `503` from the first poll after the signal, and not one request is refused: the load balancer that had not heard the news got its requests served for the whole second it kept sending them. The in-flight request finishes at 1.90 s, the drain runs after the delay, and the process exits `0` shortly after. The only difference between this log and uvicorn's is a second and a half in which the pod was unready and open.

The delay is the whole trick, and it is worth seeing what happens without it. The same service with `drain_delay_seconds` left at its default of zero:

```text
servicewright, drain_delay_seconds=0
   0.00 s  SIGTERM sent
   0.00 s  readiness probe -> 503
   0.11 s  readiness probe -> refused
   1.90 s  in-flight /slow request -> ok
   2.41 s  process exited with 0
  requests after SIGTERM: {'ok': 5, 'refused': 42, '5xx': 0, 'other': 0}
```

The readiness flip is there, the order is right, and the listener still closes in the same tick readiness goes red, so the load balancer that polls readiness every five seconds never sees the `503` before the socket is gone. A correct order with no window is the same outcome as no protocol at all, which is why the delay is not an optimisation. It is the step.

## Sizing the numbers

`drain_delay_seconds` is your cluster's endpoint propagation lag, measured, plus a margin. On most clusters one to three seconds is right; a service mesh or a slow ingress controller can push it to five. It costs exactly that much on every pod termination and nothing at any other time, and it is the number to reach for when the rollout blip appears, before anything else.

`drain_grace_seconds` is the longest request you are willing to finish. Thirty seconds is the usual default; a service whose longest request is two seconds can afford ten.

`cleanup_timeout_seconds` bounds each teardown step. A pool dispose that hangs is logged and skipped after this long, so the other steps still get their turn.

And then the manifest, which is arithmetic, not opinion:

```yaml
readinessProbe:
  httpGet:
    path: /system/health/readyz
    port: 8000
  periodSeconds: 5
terminationGracePeriodSeconds: 60   # 1.5 + 10 + 5, and a lot of slack
```

## Not only HTTP

The same protocol applies to every entrypoint a service runs, and a service usually runs more than one. A Kafka consumer that receives `SIGTERM` mid-batch has the same four steps with different verbs: stop being ready, stop fetching new records, finish the batch it holds and commit its offsets, leave the group cleanly so the rebalance is cheap, then close the producer and the pools. A scheduler stops starting new jobs and waits for the running one. A gRPC server stops accepting new streams and waits for the open ones. The order and the budgets are the same for all of them, which is why they belong in one place rather than in each framework's own shutdown hook, and why the service that runs an HTTP API and a consumer in one process drains them in reverse of the order it started them.

## What changed in the code

Nothing in the routes, nothing in the handlers, nothing in uvicorn. One lifecycle that owns the order, and three numbers on it. The lifecycle is [servicewright](https://bedrock-python.github.io/servicewright/), whose Host runs Bootstrap, Warmup, Ready, Serve, Drain and Cleanup for any set of entrypoints, and whose [Kubernetes page](https://bedrock-python.github.io/servicewright/operations/kubernetes/) carries the arithmetic above. The entrypoint that serves FastAPI is a normal FastAPI application under a normal uvicorn; the only thing the runtime takes from it is the decision about when to stop.

The point was the second half of the log: a second and a half of `503`, and zero refused.
