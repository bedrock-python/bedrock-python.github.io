---
date: 2026-09-07
authors:
  - alex
categories:
  - Libraries
tags:
  - servicewright
  - lifecycle
  - fastapi
  - apscheduler
  - workers
  - kubernetes
---

# One lifecycle for HTTP, gRPC, workers and cron jobs

An HTTP API, a gRPC server, a Kafka consumer and a nightly job are one application with four ways for work to enter it. Most codebases treat them as four applications: the API has FastAPI's lifespan, the consumer has a `while True` with its own signal handler, the cron job has a `main()` that opens a database connection and forgets to close it, and each has its own idea of what "ready" and "shutting down" mean. The plumbing is the same four times and it agrees with itself zero times. This post is the alternative, one lifecycle that hosts any number of entrypoints, and a measurement of what it does when the same service runs as one process and as two.

<!-- more -->

The timelines below come from [the post's lab](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-one-lifecycle): one service definition, run three ways, with every lifecycle call printed. Versions: servicewright 0.10.0, FastAPI 0.141.1, uvicorn 0.52.4, APScheduler 4.0.0a6, Python 3.13.

## Host and entrypoints

The model has two nouns. An **entrypoint** is a way for work to enter: an HTTP server, a gRPC server, a scheduler, a loop that polls a queue, a one-shot job. Every entrypoint answers the same four calls: `bind`, which allocates and subscribes but takes no traffic; `serve`, which runs until told to stop and then returns while still accepting; `drain`, which stops intake and lets in-flight work finish within a grace period; and `stop`, the hard stop. The **host** is the thing that makes those calls, in a fixed order, on every entrypoint it was given, and it never asks what kind of entrypoint it is talking to.

Around the entrypoints sits everything they share: the settings object, the dependency container with its application scope and its per-unit scope, the warmers that run before readiness, the health registry, the observability setup, and the shutdown budgets. Those belong to the service, not to any one entrypoint, so they are declared once, on the spec:

```python
spec = AppSpec(
    service_name="orders",
    create_container=lambda settings: Container(),
    drain_delay_seconds=0.3,
    drain_grace_seconds=5.0,
)
ENTRYPOINTS = {"all": [api, cron, worker], "api": [api], "worker": [cron, worker]}
run_sync(Service(spec, entrypoints=ENTRYPOINTS[role]), Settings())
```

The lab's three entrypoints are a FastAPI server with one route, an APScheduler job that fires every half second, and a daemon loop that stands in for a consumer. All three use the same pool through the container, and the role decides which of them this process runs.

## One process

The service started as `all`, driven for a second, then sent `SIGTERM`:

```text
 0.02 s  pool opened
 0.02 s  bind    http
 0.02 s  bind    scheduler
 0.03 s  bind    daemon
 0.03 s  ready = true, post_start hook
 0.03 s  serve   http
 0.03 s  serve   scheduler
 0.03 s  serve   daemon
 0.03 s  worker loop used the pool (use #1)
 0.59 s  scheduled job used the pool (use #3)
 0.59 s  http request used the pool (use #4)
 1.02 s  scheduled job used the pool (use #7)
 1.03 s  http request used the pool (use #8)
 1.23 s  serve   scheduler returned (still accepting)
 1.23 s  worker loop saw the stop event and finished its batch
 1.23 s  serve   daemon returned (still accepting)
 1.23 s  serve   http returned (still accepting)
 1.52 s  scheduled job used the pool (use #9)
 1.54 s  drain   daemon
 1.54 s  drain   scheduler
 1.54 s  drain   http
 1.71 s  stop    daemon
 1.71 s  stop    scheduler
 1.71 s  stop    http
 1.71 s  pre_shutdown hook, app scope still open
 1.71 s  pool closed
 exit code 0
```

Read it top to bottom, because the order is the whole point. The pool opens once, before anything can use it. The three entrypoints bind in the order they were listed, and readiness flips to true only after the last bind returned, so a load balancer that sees the service ready sees a service whose scheduler and worker are also up. All three serve concurrently, sharing one pool, and the counter shows the requests, the jobs and the loop iterations interleaving on it.

Then the signal. Every `serve` returns, and the wrapper's line says "still accepting": the scheduler is still scheduled, the worker loop finished the batch it was on, the HTTP socket is still open. Readiness went false at that moment, and for the next three tenths of a second the process keeps serving whatever arrives, which is why the scheduler fires once more at 1.52 s; that is the window the [shutdown post](2026-09-07-graceful-shutdown-is-a-protocol.md) is about. Then the drains, in *reverse* bind order: the daemon first, the scheduler second, the HTTP server last, so the thing that entered the process first is the last to leave it, the way a stack unwinds. Then the stops, same order. Then the pre-shutdown hook, with the application scope still open, which is where an outbox gets its last flush. Then the pool closes, and only then, because nothing can need it any more. Exit zero.

None of the entrypoints knows about the others, and none of them knows about the pool's lifetime. The order came from the host.

## Two processes

The same file, the same spec, run twice with different roles. First `api`:

```text
 0.01 s  pool opened
 0.01 s  bind    http
 0.01 s  ready = true, post_start hook
 0.01 s  serve   http
 0.02 s  http request used the pool (use #1)
 0.46 s  http request used the pool (use #3)
 0.67 s  serve   http returned (still accepting)
 0.97 s  drain   http
 1.14 s  stop    http
 1.14 s  pre_shutdown hook, app scope still open
 1.14 s  pool closed
 exit code 0
```

Then `worker`:

```text
 0.01 s  pool opened
 0.01 s  bind    scheduler
 0.02 s  bind    daemon
 0.02 s  ready = true, post_start hook
 0.02 s  serve   scheduler
 0.02 s  serve   daemon
 0.02 s  worker loop used the pool (use #1)
 0.51 s  scheduled job used the pool (use #4)
 0.93 s  serve   scheduler returned (still accepting)
 0.93 s  worker loop saw the stop event and finished its batch
 0.93 s  serve   daemon returned (still accepting)
 1.23 s  drain   daemon
 1.23 s  drain   scheduler
 1.23 s  stop    daemon
 1.23 s  stop    scheduler
 1.23 s  pre_shutdown hook, app scope still open
 1.23 s  pool closed
 exit code 0
```

This is the deployment most services end up with: the API scaled on request rate, the workers scaled on queue depth, each with its own resource limits and its own replica count. Usually that split costs a second codebase, or a second `main()` with a second copy of the startup and shutdown code, and the two drift until the worker's shutdown is the one that loses messages during deploys. Here it cost one dictionary. The container, the warmers, the health checks, the budgets and the order are the same in both processes, because they were never the entrypoint's to define.

The worker process has no HTTP server, and it still has readiness: it flips after both binds, and a Kubernetes deployment with an exec probe, or a tiny health entrypoint added to the list, gets the same signal the API gives. Readiness was never an HTTP concept either.

## What the entrypoints look like

A daemon loop, which is the shape of a consumer or a poller, is a function of the unit scope and the stop event:

```python
async def consume(scope, stop: asyncio.Event) -> None:
    pool = await scope.get("pool")
    while not stop.is_set():
        await pool.use("worker loop")
        with contextlib.suppress(TimeoutError):
            await asyncio.wait_for(stop.wait(), timeout=0.4)

worker = DaemonEntrypoint(consume)
```

A scheduled job is a function of the unit scope, and the entrypoint opens a fresh scope for every run:

```python
async def nightly_report(scope) -> None:
    await (await scope.get("pool")).use("scheduled job")

cron = SchedulerEntrypoint(jobs=[ScheduledJob(id="report", func=nightly_report, trigger=IntervalTrigger(seconds=0.5))])
```

And the HTTP server is a normal FastAPI application whose routes take the unit scope as a dependency; the entrypoint's middleware opens the scope per request and the route never sees the container:

```python
@router.get("/work")
async def work(unit: UnitScopeDep) -> dict[str, str]:
    await (await unit.get("pool")).use("http request")
    return {"status": "ok"}

api = FastApiEntrypoint(config=HttpConfig(port=8000), routers=(router,))
```

Three different frameworks' worth of "how work enters", and the same two questions answered the same way for each: where does the scope come from, and how do I stop. A gRPC server is a fourth answer to the same questions and slots into the same list.

## The one thing to get right

Every entrypoint has to return from `serve` while it is still accepting work, and leave the closing to `drain`. It is the single rule in the model that is easy to get backwards, because every framework's own shutdown does both at once, and doing both at once inside `serve` throws away the window between readiness going false and intake closing. The four calls exist so that the host can own that window on behalf of every entrypoint at once, which is what makes the shutdown in the first timeline one sequence instead of three.

That host is [servicewright](https://bedrock-python.github.io/servicewright/concepts/entrypoints/), which ships the FastAPI, Litestar, gRPC, APScheduler, daemon and one-shot entrypoints, and whose Host runs Bootstrap, Warmup, Ready, Serve, Drain and Cleanup for whichever of them a process is given.

The point was the two `pool closed` lines. One each, last each, in both processes.
