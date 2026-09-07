---
date: 2026-09-07
authors:
  - alex
categories:
  - Design
tags:
  - servicewright
  - fastapi
  - lifecycle
  - architecture
  - kubernetes
---

# Why application lifecycle should not belong to FastAPI

<div class="bdr-post__hero" data-bdr-post="2026-09-07-why-application-lifecycle-should-not-belong-to-fastapi" role="img" aria-label="The lifecycle does not belong to the HTTP framework" markdown="0"></div>

FastAPI's `lifespan` is a good API. It is an async context manager: whatever you set up before the `yield` is the startup, whatever you do after it is the shutdown, and it runs exactly once per process. Every FastAPI service I have seen keeps its database pool, its warmup, its health checks and its clients there, and that is where the trouble starts, not because the lifespan does it badly but because the lifespan belongs to the HTTP framework and the application does not. The moment the same service needs a worker, a consumer or a nightly job, there is no lifespan for it, and the plumbing gets written a second time by hand. This post is the argument, with the two files it produces and the one file it should have been.

<!-- more -->

The code is in [the post's lab directory](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-lifecycle-not-fastapi) and in [the one-lifecycle lab](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-one-lifecycle) from the previous post. Versions: FastAPI 0.141.1, uvicorn 0.52.4, servicewright 0.10.0, Python 3.13.

## The API, as usually written

```python
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    log("pool opened")                      # startup: the pool, warmup, health registration, ...
    app.state.pool = Pool()
    yield
    log("pool closed")                      # shutdown: ... in whatever order uvicorn gets here


app = FastAPI(lifespan=lifespan)


@app.get("/work")
async def work() -> dict[str, str]:
    await app.state.pool.use("http request")
    return {"status": "ok"}
```

Forty lines with the imports, and nothing wrong with any of them. The pool opens before the first request and closes after the last. Warmup goes above the `yield`, health checks get registered there, the metrics server starts there. The lifespan is the application's lifecycle, and it lives inside `FastAPI(...)`.

Notice three things it does not do, because they are not the framework's to do. It does not decide when the process is ready; uvicorn does, by starting to accept, and a readiness probe is a route you add. It does not decide how shutdown is ordered against a load balancer; uvicorn does, by closing its socket on `SIGTERM`, which is the [refused-requests problem](2026-09-07-graceful-shutdown-is-a-protocol.md). And it does not exist outside an HTTP server at all.

## The worker, as usually written

Six months later the service needs a consumer, or a nightly job, or a queue poller. There is no FastAPI in that process, so there is no lifespan, and the file that gets written looks like this:

```python
async def main() -> None:
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGTERM, stop.set)     # the API got this from uvicorn
    log("pool opened")                                    # the API got this from the lifespan
    pool = Pool()
    try:
        while not stop.is_set():
            await pool.use("worker loop")
            try:
                await asyncio.wait_for(stop.wait(), timeout=0.4)
            except TimeoutError:
                pass
        log("worker loop saw the stop event")
    finally:
        log("pool closed")                                # and this
```

Thirty-seven lines, nine of them plumbing that the API got for free: a stop event, a signal handler, the pool opened and closed in a `finally`. Run it and send it `SIGTERM`:

```text
 0.00 s  pool opened
 0.80 s  worker loop used the pool
 0.97 s  worker loop saw the stop event
 0.97 s  pool closed
```

It works, and that is the problem, because it works differently. It has no readiness: Kubernetes cannot tell a worker that is warming up from one that is stuck. It has no drain window and no grace budget: a batch that takes ten seconds to finish is killed at whatever the deployment's grace period is. It has no health registry, so the pool it opened is checked by nobody. The warmup that the API does above the `yield` is not here, because the person who wrote this file copied the pool and not the warmup. And the next worker copies this file, with whatever it got wrong.

This is the actual cost of putting the lifecycle in the lifespan: not that the API's lifecycle is bad, but that it is *not reusable*, and everything in the service that is not an HTTP server reinvents it, each time a little differently, until the day the consumer loses messages on a deploy and the investigation finds that its shutdown never waited for anything.

## The framework is an entrypoint

The mistake is a category error. FastAPI is one way for work to enter the process. So is the consumer loop; so is the scheduler; so is a gRPC server. None of them is the process. The process has one lifecycle, startup through shutdown, and it needs to be owned by something that is not any of the entrypoints, so that every entrypoint can be hosted by it.

In that model the FastAPI app is still a normal FastAPI app, deliberately without a container-managing lifespan, because the host already did the container, the warmup, the health registration and the readiness flip before the app served its first request, and will do the drain and the teardown after its last. The worker is a function of a scope and a stop event, and the scheduler is a list of jobs, and all three answer the same four calls the host makes on every entrypoint: bind, serve, drain, stop.

The previous post measured what that looks like at run time, and the part worth repeating here is the diff. This is the whole of the two files above, in the host model:

```python
api = FastApiEntrypoint(config=HttpConfig(port=8000), routers=(router,))
worker = DaemonEntrypoint(consume)

ENTRYPOINTS = {"all": [api, worker], "api": [api], "worker": [worker]}

spec = AppSpec(service_name="orders", create_container=lambda settings: Container(), drain_delay_seconds=1.0)
run_sync(Service(spec, entrypoints=ENTRYPOINTS[role]), Settings())
```

The worker file is gone. The signal handler, the stop event, the pool's `finally`, the readiness, the drain budget and the warmup are on the host, once, and the worker is the loop and nothing else. Adding the scheduler was one more entry in the dictionary. Splitting the API and the worker into two deployments was the dictionary's keys.

## What FastAPI's lifespan is still for

Not nothing. Things that are genuinely about the HTTP app and nothing else, a template engine, a router-level cache, an OpenAPI customisation, belong in the lifespan, because the app is their lifecycle. The rule is the same one that decides where any code goes: the lifespan owns what only the HTTP entrypoint needs; the host owns what the process needs. A database pool is the second kind, and it was only ever in the lifespan because there was nowhere else to put it.

Expect disagreement on this one. The counter-argument is that most services are only an API, and for those the lifespan is exactly right and the host is a layer of indirection. I think that is true on the day the service is written and false within a year, because the worker always comes, and the day it comes is the day the lifespan's contents have to move anyway. Moving them on the first day costs one file.

The host is [servicewright](https://bedrock-python.github.io/servicewright/concepts/lifecycle/), whose FastAPI entrypoint builds a normal FastAPI app with no lifespan of its own and hands the lifecycle to the Host.

The point was the second file. Thirty-seven lines that should not exist.
