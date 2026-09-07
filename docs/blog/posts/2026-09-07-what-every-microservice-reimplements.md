---
date: 2026-09-07
authors:
  - alex
categories:
  - Meta
tags:
  - bedrock-python
  - architecture
  - microservices
  - servicewright
  - sqlalchemy-foundation-kit
  - clientwright
  - deadline-budget
---

# What every production Python microservice reimplements

<div class="bdr-post__hero" data-bdr-post="2026-09-07-what-every-microservice-reimplements" role="img" aria-label="The same infrastructure code, rebuilt in every service, around a small product core" markdown="0"></div>

Open the repository of any backend service that has been in production for a year and look for the code that is not the product. It is there, in every one of them, and it is the same code: a startup sequence, a health endpoint, a shutdown handler that mostly works, a retry helper, a timeout that means the wrong thing, a session factory, a base model, a Kafka producer that needs closing, an outbox nobody finished, a metrics registry, a tracing setup, and a test that runs the migrations once. None of it is what the service is for. All of it is what the service falls over without. This post is that list, why the usual answer to it, a framework, is the wrong shape, and a hundred-line service that has all of it and none of it, run end to end.

<!-- more -->

## The list

Here is what I have found myself writing, from scratch or by copy from the previous project, in every service I have started in the last several years:

```text
lifecycle          startup order, warmup, readiness, a stop signal, teardown in reverse
health             liveness and readiness that mean different things
graceful shutdown  keep serving while the load balancer catches up, drain, close pools, exit 0

HTTP retries       with backoff, jitter, Retry-After, and only for idempotent calls
timeouts           that bound the call, not the attempt
deadlines          carried from the inbound request into every outbound one
circuit breakers   per origin, with a threshold that survives the retry count

DB sessions        a factory, a pool, settings that survive PgBouncer
transactions       one owner, commit once, roll back on exception
Redis              a client, a health check, a decision about failing open
Kafka              a producer with a lifecycle, a consumer that shuts down mid-batch

idempotency        a key, a store, a rule for two concurrent callers
outbox             so the row and the event happen together

metrics            one registry, the same labels everywhere
tracing            a provider, propagation across every hop
migration tests    up, down, up again, and a diff against the models
```

Every line is a week the first time and a day the fifth time, and the fifth copy has a bug the second copy fixed. The other posts in this series each take one line of that list and measure what goes wrong when it is missing. This one is about the shape of the answer.

## Why not a framework

The obvious answer is a framework: one package that does all of it, `from company.platform import Service`, and every team inherits the plumbing. I have built that too, and it fails in a specific way. The framework owns the application. It decides the web server, the DI container, the settings loader, the logging format, the version of every dependency, and its release is everybody's release. A team that needs one line of the list, say deadlines, has to take the whole thing, and a team that has its own answer to one line, say a settings loader they like, has to fight the framework to keep it. Within two years the framework is the biggest dependency in the organisation, the hardest to upgrade, and the reason the Python floor cannot move.

The shape I ended up with instead is the opposite: one small library per line of the list, each with a core that depends on nothing, each usable alone, each releasing on its own schedule, and each talking to the others through the shape of an object rather than through an import. A service takes the four it needs and ignores the rest. A team with its own settings loader passes an object of the right shape. Nothing is inherited.

That is easy to claim and only convincing when the pieces actually compose, so here they are composing.

## A hundred lines

The service below is an orders API: it looks an order up in PostgreSQL, asks a warehouse service for stock, and answers. It has a lifecycle with warmup, readiness and drain, a session pool, an outbound HTTP client with retries and a total timeout, and a request deadline that travels from the inbound header to the outbound one. It is a hundred lines including the blank ones, and it is in [the post's lab directory](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-what-every-microservice-reimplements) with a runner that starts a real PostgreSQL and a stub warehouse around it.

```python
@dataclass(frozen=True)
class Settings:  # the shape the runtime reads; nothing to inherit
    logging: object | None = None
    metrics: object | None = None
    tracing: object | None = None
    error_tracking: object | None = None

    def get_app_version(self) -> str:
        return "1.0.0"
```

The settings object is a frozen dataclass with four fields and a method, because that is all the runtime reads. It does not inherit a base class, and it could be a pydantic model or a plain class; the runtime looks at its shape.

```python
class Container:  # your DI, in twelve lines: one app scope for singletons, one unit scope per request
    def __init__(self, db: AsyncSessionManager, http) -> None:
        self.db, self.http = db, http

    @contextlib.asynccontextmanager
    async def app_scope(self):
        try:
            yield Scope(db=self.db, http=self.http)
        finally:  # pools close here, after every entrypoint has drained
            await self.http.aclose()
            await self.db.aclose()

    @contextlib.asynccontextmanager
    async def unit_scope(self, context=None):
        async with self.db.get_session() as session:
            yield Scope(session=session, http=self.http)
```

The container is the whole dependency injection integration: two async context managers, one for the process and one per request. A real service would hand the runtime a dishka container here, and the runtime would not know the difference. What matters is what the shape gives you for free: the application scope closes *after* the drain, so the pools are disposed only once no request can need them, and the unit scope opens one session per request and closes it whatever happens in the handler.

```python
def create_container(settings: Settings) -> Container:
    db = AsyncSessionManager(os.environ["DATABASE_URL"], poolclass="async_adapted_queue")
    http = build("httpx", ClientConfig(
        service_name="orders",
        base_url=os.environ["WAREHOUSE_URL"],
        timeout=TimeoutConfig(total=5.0),
        retry=RetryConfig(max_attempts=3),
        deadline_header="X-Deadline-Ms",       # what is left of the request, on the wire
        on_unsupported="strict",
    ), AdapterDeps(deadline_source=AmbientDeadlineSource()))
    return Container(db, http)
```

Two singletons. The session manager is a pool with settings that survive a connection pooler. The HTTP client is a plain `httpx.AsyncClient` with a policy under it: three attempts inside a five-second total, and a header that carries the remaining deadline downstream, read from whatever budget the current request installed.

```python
@router.get("/orders/{order_id}")
async def get_order(order_id: int, unit: UnitScopeDep, x_deadline_ms: int | None = Header(default=None)):
    budget = BudgetContext.create(total_seconds=x_deadline_ms / 1000, safety_margin=0.1) if x_deadline_ms else None
    with use_budget(budget):                    # every outbound call below is trimmed to it
        session, http = await unit.get("session"), await unit.get("http")
        known = (await session.execute(text("SELECT count(*) FROM orders WHERE id = :id"), {"id": order_id})).scalar()
        stock = (await http.get(f"/stock/{order_id}")).json()
    return {"order_id": order_id, "known": bool(known), "stock": stock}
```

The handler is a normal FastAPI route on a normal FastAPI app. It takes the request's unit scope as a dependency, builds a budget from the inbound deadline header with a hundred milliseconds kept back for its own response, and does its two calls inside the budget. It does not pass a timeout to either of them. The database call is bounded by the session's settings; the HTTP call reads the budget through the context variable and issues itself with whatever the request has left, then writes that number into the outbound header.

```python
spec = AppSpec(
    service_name="orders",
    create_container=create_container,
    warmers_factory=lambda ctx: [PostgresWarmer(ctx.container.db)],   # readiness waits for a real query
    drain_delay_seconds=1.0,                                          # keep serving while endpoints propagate
    drain_grace_seconds=10.0,
    cleanup_timeout_seconds=5.0,
)
spec.lifecycle.add_pre_start_hook(register_health)
service = Service(spec, entrypoints=[FastApiEntrypoint(config=HttpConfig(port=8000), routers=(router,))])
run_sync(service, Settings())
```

And the lifecycle: a container factory, a warmer that runs a real query before readiness flips, the three shutdown budgets, a readiness check on the pool registered once the pool exists, and one HTTP entrypoint. The same spec with a second entrypoint in the list is the same service running a Kafka consumer next to its API; with a different list, it is the worker deployment.

## Run

The runner starts PostgreSQL in a container with one row in an `orders` table, a stub warehouse that answers every stock request with the deadline header it received, and the service as a subprocess. Then it calls it, sends `SIGTERM`, and keeps calling:

```text
   0.35 s  readyz -> 200 {'status': 'ok'}
   0.36 s  GET /orders/1 with X-Deadline-Ms: 800 -> 200 {'order_id': 1, 'known': True,  'stock': {'in_stock': 3, 'deadline_ms_seen': 697}}
   0.36 s  GET /orders/2 without a deadline       -> 200 {'order_id': 2, 'known': False, 'stock': {'in_stock': 3, 'deadline_ms_seen': 4999}}
   0.36 s  SIGTERM
   0.57 s  readyz during the drain delay -> 503
   0.57 s  GET /orders/1 during the drain delay -> 200
   1.64 s  process exited with 0
```

Line one: readiness went green only after the warmer's query succeeded against the real database, so the first request the load balancer sends will not be the one that opens the first connection. Line two: the request arrived with 800 ms, the handler kept 100 for itself, the database query cost a few, and the warehouse was told it had 697. Line three: a request with no deadline gets the client's own five-second total, and the warehouse is told that. Then the signal: readiness answers `503` within the second while the same process still answers `200` to a real request, the drain runs, the pools close, and the process exits with zero.

Every one of those lines is a thing from the list, and none of them is in the handler. The handler is six lines of business logic and one `with`.

## How the pieces stay apart

There are four libraries in that file and none of them imports another. The lifecycle runtime reads a settings object by its shape and calls a container by its two methods. The session manager is handed to the warmer and the health check, which only need `get_session()` and a session maker. The HTTP client reads the deadline through a protocol with two methods, `remaining()` and `expired()`, that the budget happens to satisfy; a service that tracks deadlines its own way passes its own object. The budget library itself has no dependencies, starts no tasks and knows nothing about HTTP; it does arithmetic on one countdown and returns floats.

That is the whole design of the organisation: small libraries, zero-dependency cores, extras for the integrations, and protocol-shaped seams between them, so that a service takes the lines of the list it needs and leaves the rest. The list has fourteen lines and there are twelve libraries; the ones this service did not need are the Redis client, the Kafka client, the idempotency store, the outbox, the migration tests, the partition manager and the two gRPC kits, and each of them has a post of its own in this series or will.

I kept seeing the same infrastructure code repeated across services. [Bedrock Python](https://bedrock-python.github.io/libraries/) is an attempt to pull those pieces into small independent libraries instead of creating another mega-framework. This was the smallest service that shows what that looks like when it runs.
