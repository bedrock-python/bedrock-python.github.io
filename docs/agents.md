---
title: Building a service
description: One page for a coding assistant that builds a production async Python service on the Bedrock Python libraries.
copy_page: true
---

# Building a service with Bedrock Python

> One page for a coding assistant that starts a production async Python service from
> scratch on the Bedrock Python libraries: which library covers which need, how they fit
> together in one codebase, and where each library's own page for agents is. Give an agent
> this page first, then the agent page of every library it picks.

## How to read this page

Every library has a one-page reference for assistants at
`https://bedrock-python.github.io/<repo>/agents/`, and its raw Markdown at
`https://bedrock-python.github.io/<repo>/agents.md`. This page is raw Markdown at
`https://bedrock-python.github.io/agents.md`. It shows how the libraries connect, not their
full API. Before writing code against a library, fetch its agent page. When a name on this
page and a library's own page disagree, the library page wins.

The code below is one service, `orders`, assembled from the released libraries and run
against PostgreSQL 17, Redis 7 and Kafka 3.9 on 2026-11-11: the API, the worker, the
migrations and their tests. Copy the shape, not the domain.

## Pick the libraries

Install only what the service needs. Python 3.12 or newer: servicewright and omni-box
require it.

| The service needs | Library | Install |
|---|---|---|
| One process lifecycle for HTTP, gRPC, cron, daemons and one-shot jobs: health probes, graceful drain, logs and metrics | [servicewright](https://bedrock-python.github.io/servicewright/agents/) | `servicewright[fastapi,dishka,settings,metrics,observability]`, plus `apscheduler3` for cron, `grpc` for a gRPC server, `postgres` / `redis` for the ready-made health checks |
| PostgreSQL through async SQLAlchemy | [sqlalchemy-foundation-kit](https://bedrock-python.github.io/sqlalchemy-foundation-kit/agents/) | `sqlalchemy-foundation-kit[settings,dishka,metrics]` |
| Alembic migrations, tested before they reach production | [alembic-gauntlet](https://bedrock-python.github.io/alembic-gauntlet/agents/) | dev only: `alembic-gauntlet[asyncio,testcontainers]` |
| An event that must leave exactly when the database commit happens (outbox), or incoming messages handled once (inbox) | [omni-box](https://bedrock-python.github.io/omni-box/agents/) | `omni-box[postgres,kafka]` |
| A retried POST must not create a second order | [idempotency-kit](https://bedrock-python.github.io/idempotency-kit/agents/) | `idempotency-kit[redis,dishka,prometheus]` |
| Redis | [redis-client-kit](https://bedrock-python.github.io/redis-client-kit/agents/) | `redis-client-kit[settings,providers,metrics]` |
| Kafka producers and consumers | [aiokafka-foundation-kit](https://bedrock-python.github.io/aiokafka-foundation-kit/agents/) | `aiokafka-foundation-kit[models,dishka]` |
| Outbound HTTP calls with retries, a circuit breaker and a total deadline | [clientwright](https://bedrock-python.github.io/clientwright/agents/) | `clientwright[httpx,settings,dishka,metrics,servicewright]` |
| A gRPC server | servicewright's `grpc` extra, built on [grpc-server-kit](https://bedrock-python.github.io/grpc-server-kit/agents/) | `servicewright[grpc]` |
| A gRPC client | [grpc-client-kit](https://bedrock-python.github.io/grpc-client-kit/agents/) | `grpc-client-kit[settings,dishka,metrics,health]` |
| One time budget per request, split across downstream calls | [deadline-budget](https://bedrock-python.github.io/deadline-budget/agents/) | `deadline-budget`, or the `deadline` extra of clientwright / grpc-client-kit |
| Time-partitioned tables created ahead and dropped after retention | [pg-partsmith](https://bedrock-python.github.io/pg-partsmith/agents/) | `pg-partsmith` |
| The same AGENTS.md, guidelines and CI files in every repository | [touchmark](https://bedrock-python.github.io/touchmark/agents/) and [engineering-assets-template](https://github.com/bedrock-python/engineering-assets-template) | a hub repository, see [Engineering assets](#engineering-assets) |

## The shape of a service

One codebase, one image, several processes. The API and the worker share settings, the
container and the health checks, and differ only in their list of entrypoints.

```
orders-service/
├── src/orders_service/
│   ├── db.py                 # ORM models (sqlalchemy-foundation-kit Base, omni-box outbox table)
│   ├── orders.py             # use cases: CreateOrder, ExpireOrders
│   ├── api.py                # FastAPI routers
│   ├── runtime/              # the only package that imports servicewright and dishka
│   │   ├── settings.py       # Settings: one class, one section per library
│   │   ├── container.py      # build_container(settings)
│   │   └── spec.py           # build_spec(settings) -> AppSpec: observability, health checks
│   ├── api_main.py           # Service(spec, entrypoints=[http])
│   └── worker_main.py        # Service(spec, entrypoints=[scheduler, outbox relay])
├── migrations/               # Alembic: env.py, versions/
├── tests/test_migrations.py  # alembic-gauntlet
├── alembic.ini
└── pyproject.toml
```

Deployments run the same image with different commands:
`python -m orders_service.api_main`, `python -m orders_service.worker_main`, and
`alembic upgrade head` as a job before the new version starts. A larger codebase splits
`orders.py` into `core/`, `use_cases/` and `infra/`; servicewright's
[project layout](https://bedrock-python.github.io/servicewright/blueprints/project-layout/)
shows that tree.

## 1. Settings

One pydantic-settings class. Every library ships its section as a model; nest them, and
the environment names follow with `__` between levels.

```python title="runtime/settings.py"
from aiokafka_foundation_kit.contrib.models import BaseKafkaProducerSettings
from idempotency_kit.settings import BaseIdempotencySettings
from redis_client_kit.settings import BaseRedisSettings
from servicewright.adapters.fastapi import HttpServerSettings
from servicewright.adapters.settings import BaseServiceSettings
from sqlalchemy_foundation_kit.contrib.settings import BasePostgresConfig


class Settings(BaseServiceSettings):     # env_nested_delimiter="__" is inherited
    server: HttpServerSettings = HttpServerSettings()   # SERVER__PORT, ...
    postgres: BasePostgresConfig         # POSTGRES__CONNECTION__HOST, POSTGRES__APPLICATION_NAME, ...
    redis: BaseRedisSettings             # REDIS__KEY_PREFIX, REDIS__CONNECTION__HOST, ...
    idempotency: BaseIdempotencySettings # IDEMPOTENCY__KEY_PREFIX, ...
    kafka: BaseKafkaProducerSettings     # KAFKA__BOOTSTRAP_SERVERS
```

`BaseServiceSettings` already carries `logging`, `metrics`, `tracing` and `error_tracking`
sections and `app_version`; servicewright reads them structurally. Required fields in this
example: `POSTGRES__CONNECTION__PASSWORD`, `POSTGRES__CONNECTION__DATABASE`,
`POSTGRES__APPLICATION_NAME`, `REDIS__KEY_PREFIX`, `IDEMPOTENCY__KEY_PREFIX`,
`KAFKA__BOOTSTRAP_SERVERS`.

## 2. Models

```python title="db.py"
import uuid

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from omni_box.infra.storage.postgres import OutboxEventDBBase
from sqlalchemy_foundation_kit import Base, BaseTable, DatetimeColumnsMixin


class OrderDB(BaseTable, DatetimeColumnsMixin):
    __tablename__ = "orders"
    __table_args__ = (CheckConstraint("amount > 0", name="amount_positive"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID]
    amount: Mapped[int]
    status: Mapped[str] = mapped_column(String(32), default="new")


class OutboxEventDB(Base, OutboxEventDBBase):    # omni-box's table, in your metadata and migrations
    pass
```

`Base` carries the kit's naming convention (`orders_pkey`, `orders_amount_positive_check`),
so constraint names are stable across autogenerated migrations. Name every
`CheckConstraint`.

## 3. Use cases

The order row and its event commit in one transaction. The relay in the worker sends the
event later. The idempotency decorator replays the first response for a repeated key.

```python title="orders.py"
import uuid

from pydantic import BaseModel, Field
from sqlalchemy import update

from idempotency_kit import AsyncIdempotencyCoordinator, PydanticResultAdapter, async_idempotent
from omni_box import OmniBoxDomainService
from omni_box.infra.storage.postgres import PostgresOutboxRepository
from sqlalchemy_foundation_kit import AsyncSQLAlchemyUowTransaction, AsyncUnitOfWork

from orders_service.db import OrderDB, OutboxEventDB


class CreateOrderDTO(BaseModel):
    customer_id: uuid.UUID
    amount: int = Field(gt=0)


class OrderDTO(BaseModel):
    id: uuid.UUID
    status: str


class CreateOrder:
    def __init__(
        self,
        uow: AsyncUnitOfWork[AsyncSQLAlchemyUowTransaction],
        coordinator: AsyncIdempotencyCoordinator,
        events: OmniBoxDomainService,
    ) -> None:
        self._uow = uow
        self.coordinator = coordinator
        self._events = events

    @async_idempotent(
        operation="order.create",
        adapter=PydanticResultAdapter(OrderDTO),
        ttl_seconds=3600,
        infra_param="coordinator",
        fingerprint_params=("dto",),     # same key with a different body raises, never replays
    )
    async def execute(self, dto: CreateOrderDTO, *, idempotency_key: str | None = None) -> OrderDTO:
        async with self._uow.transaction() as tx:      # commits on exit, rolls back on error
            order = OrderDB(customer_id=dto.customer_id, amount=dto.amount)
            tx.session.add(order)
            await tx.session.flush()
            await PostgresOutboxRepository(tx.session, model_class=OutboxEventDB).create(
                self._events.create_outbox_event(
                    aggregate_type="order",
                    aggregate_id=order.id,
                    event_type="order.created",
                    topic="orders.events",
                    partition_key=str(order.id),
                    payload={"amount": dto.amount},
                    idempotency_key=f"order.created:{order.id}",
                )
            )
            return OrderDTO(id=order.id, status=order.status)


class ExpireOrders:
    def __init__(self, uow: AsyncUnitOfWork[AsyncSQLAlchemyUowTransaction]) -> None:
        self._uow = uow

    async def execute(self) -> int:
        async with self._uow.transaction() as tx:
            result = await tx.session.execute(
                update(OrderDB).where(OrderDB.status == "new").values(status="expired")
            )
            return result.rowcount
```

Use cases import no servicewright and no dishka. Repositories `flush()`; only
`uow.transaction()` commits. `uow.query()` is a read-only transaction.

## 4. Container

dishka matches dependencies by exact type. Each library asks for its settings by a
protocol, so one provider hands every library its section.

```python title="runtime/container.py"
from dishka import Provider, Scope, make_async_container, provide

from idempotency_kit.dishka import (
    AsyncIdempotencyCoordinatorProvider,
    AsyncRedisIdempotencyProvider,
    IdempotencyProvider,
    IdempotencySettingsProtocol,
)
from omni_box import OmniBoxDomainService
from redis_client_kit import RedisSettingsProtocol
from redis_client_kit.providers import AsyncRedisProvider
from servicewright.adapters.dishka import DishkaContainer
from sqlalchemy_foundation_kit import PostgresMetricsProtocol, PostgresSettingsProtocol
from sqlalchemy_foundation_kit.contrib.di import AsyncDatabaseProvider, AsyncUnitOfWorkProvider
from sqlalchemy_foundation_kit.contrib.metrics import PostgresMetrics

from orders_service.orders import CreateOrder, ExpireOrders
from orders_service.runtime.settings import Settings


class SettingsProvider(Provider):
    scope = Scope.APP

    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings

    @provide
    def postgres(self) -> PostgresSettingsProtocol:
        return self._settings.postgres

    @provide
    def postgres_metrics(self) -> PostgresMetricsProtocol | None:   # required, even as None
        return PostgresMetrics() if self._settings.postgres.metrics_enabled else None

    @provide
    def redis(self) -> RedisSettingsProtocol:
        return self._settings.redis

    @provide
    def idempotency(self) -> IdempotencySettingsProtocol:
        return self._settings.idempotency


class AppProvider(Provider):
    scope = Scope.APP

    @provide
    def events(self) -> OmniBoxDomainService:
        return OmniBoxDomainService()      # provide(OmniBoxDomainService) would ask for its int defaults

    create_order = provide(CreateOrder, scope=Scope.REQUEST)
    expire_orders = provide(ExpireOrders, scope=Scope.REQUEST)


def build_container(settings: Settings) -> DishkaContainer:
    return DishkaContainer(
        make_async_container(
            SettingsProvider(settings),
            AsyncDatabaseProvider(),           # AsyncSessionManager, async_sessionmaker; checks the DB at startup
            AsyncUnitOfWorkProvider(),         # AsyncUnitOfWork[AsyncSQLAlchemyUowTransaction]
            AsyncRedisProvider(),              # AsyncRedisClient; pings at startup, closes on shutdown
            IdempotencyProvider(),
            AsyncRedisIdempotencyProvider(),   # takes the client AsyncRedisProvider gives
            AsyncIdempotencyCoordinatorProvider(),
            AppProvider(),
        )
    )
```

servicewright maps dishka's `Scope.APP` to the process and `Scope.REQUEST` to one unit of
work: an HTTP request, a job run, a daemon loop. Do not also call dishka's `setup_dishka`
on the FastAPI app: two request scopes per request raise `RuntimeError`.

## 5. Spec: observability and health

```python title="runtime/spec.py"
from redis_client_kit import AsyncRedisClient
from servicewright import AppScopeProtocol, AppSpec, KeyRedactor, ObsConfig, ObservabilityManager
from servicewright.adapters.health.postgres import PostgresHealthCheck
from servicewright.adapters.health.redis import RedisHealthCheck
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from orders_service.runtime.container import build_container
from orders_service.runtime.settings import Settings


def build_spec(settings: Settings) -> AppSpec:
    spec = AppSpec(
        service_name="orders",
        create_container=build_container,
        observability=ObservabilityManager(
            ObsConfig(metrics="prometheus", logging="structlog", tracing=None, error_tracking=None),
            redactor=KeyRedactor(),
        ),
        drain_delay_seconds=5.0,           # keep accepting while the load balancer catches up
        drain_grace_seconds=30.0,
        cleanup_timeout_seconds=10.0,
    )

    async def register_health_checks(app_scope: AppScopeProtocol | None = None) -> None:
        # Runs before readiness. Resolving the clients opens the pools and runs the kits'
        # startup checks, so a dead database fails the start instead of the first request.
        maker = await app_scope.get(async_sessionmaker[AsyncSession])
        redis = await app_scope.get(AsyncRedisClient)
        spec.health.add_check("postgres", PostgresHealthCheck(maker, timeout=5.0))
        spec.health.add_check("redis", RedisHealthCheck(redis, timeout=5.0))

    spec.lifecycle.add_pre_start_hook(register_health_checks)
    return spec
```

`ObsConfig()` with no arguments selects all four backends; pass `None` for each one you do
not run. Kubernetes needs `terminationGracePeriodSeconds` above
`drain_delay_seconds + drain_grace_seconds + cleanup_timeout_seconds`: 45 seconds here, so 60.

## 6. The API

```python title="api.py"
from fastapi import APIRouter
from idempotency_kit import IdempotencyInProgressError, IdempotencyKeyReuseError, IdempotencyValidationError
from servicewright import ErrorKind, ServiceError
from servicewright.adapters.fastapi import IdempotencyKey, UnitScopeDep

from orders_service.orders import CreateOrder, CreateOrderDTO, OrderDTO

router = APIRouter(prefix="/orders", tags=["orders"])


class IdempotencyKeyInUseError(ServiceError):
    kind = ErrorKind.CONFLICT            # 409: the first request with this key is still running


class IdempotencyKeyMismatchError(ServiceError):
    kind = ErrorKind.INVALID             # 400: the key was used for another body, or is malformed


@router.post("", response_model=OrderDTO, status_code=201)
async def create_order(dto: CreateOrderDTO, scope: UnitScopeDep, idempotency_key: IdempotencyKey = None) -> OrderDTO:
    use_case = await scope.get(CreateOrder)
    try:
        return await use_case.execute(dto, idempotency_key=idempotency_key)
    except IdempotencyInProgressError as exc:
        raise IdempotencyKeyInUseError() from exc
    except (IdempotencyKeyReuseError, IdempotencyValidationError) as exc:
        raise IdempotencyKeyMismatchError() from exc
```

```python title="api_main.py"
from servicewright import Service, run_sync
from servicewright.adapters.fastapi import FastApiEntrypoint

from orders_service.api import router
from orders_service.runtime.settings import Settings
from orders_service.runtime.spec import build_spec


def main() -> None:
    settings = Settings()
    http = FastApiEntrypoint(
        config=settings.server.to_config(version=settings.app_version),
        middlewares=settings.server.middlewares.to_config(),
        routers=(router,),
        metrics=True,                    # /system/metrics on the same port
    )
    run_sync(Service(build_spec(settings), entrypoints=[http]), settings)


if __name__ == "__main__":
    main()
```

Probes: `/system/health/livez` and `/system/health/readyz`. Errors render as RFC 9457
problem documents. Any exception that is not a `ServiceError` becomes a 500 with code
`internal_error` and its text stays in the log, so translate library errors the client
should see, as above.

## 7. The worker

```python title="worker_main.py"
import asyncio
import contextlib

from aiokafka_foundation_kit import producer_lifecycle
from apscheduler.triggers.interval import IntervalTrigger
from omni_box import OutboxPublisher
from omni_box.core.converters import EnvelopeEventConverter
from omni_box.infra.brokers.kafka import KafkaEventPublisher
from omni_box.infra.storage.postgres import PostgresOutboxRepository
from servicewright import DaemonEntrypoint, Service, UnitScopeProtocol, run_sync
from servicewright.adapters.apscheduler3 import ScheduledJob, SchedulerEntrypoint
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from orders_service.db import OutboxEventDB
from orders_service.orders import ExpireOrders
from orders_service.runtime.settings import Settings
from orders_service.runtime.spec import build_spec


async def expire_orders(scope: UnitScopeProtocol) -> None:      # a job takes the scope first
    await (await scope.get(ExpireOrders)).execute()


def outbox_relay(settings: Settings):
    async def relay(scope: UnitScopeProtocol, stop: asyncio.Event) -> None:
        maker = await scope.get(async_sessionmaker[AsyncSession])
        async with producer_lifecycle(settings.kafka) as producer:
            broker = KafkaEventPublisher(producer=producer, converter=EnvelopeEventConverter())
            while not stop.is_set():
                async with maker() as session, session.begin():  # omni-box never commits
                    repo = PostgresOutboxRepository(session, model_class=OutboxEventDB)
                    result = await OutboxPublisher(repo, broker).publish_batch(
                        worker_id="orders-relay", batch_size=100  # [A-Za-z0-9.-/:] only
                    )
                if result.processed_event_ids:
                    continue                                      # drain a backlog without sleeping
                with contextlib.suppress(TimeoutError):
                    await asyncio.wait_for(stop.wait(), timeout=1.0)

    return relay


def main() -> None:
    settings = Settings()
    entrypoints = [
        SchedulerEntrypoint(
            jobs=[ScheduledJob(id="expire-orders", func=expire_orders,
                               trigger=IntervalTrigger(minutes=5), max_instances=1)],
        ),
        DaemonEntrypoint(outbox_relay(settings), kind="outbox"),
    ]
    run_sync(Service(build_spec(settings), entrypoints=entrypoints), settings)


if __name__ == "__main__":
    main()
```

The scheduler is in-process: run the worker at one replica, or split the scheduler into a
deployment of its own. A job that raises is logged and the scheduler keeps going.
`apscheduler4` exists too, but every APScheduler 4 release is a pre-release that pip and uv
skip by default. The worker has no HTTP port; for probes and metrics either set
`METRICS__ENABLED=true` (a standalone exposition port) or add a `FastApiEntrypoint` with no
routers. A Kafka consumer is a `ScopedEntrypoint` of about thirty lines:
servicewright's [background worker](https://bedrock-python.github.io/servicewright/blueprints/worker/)
blueprint has one, and omni-box's `InboxConsumerRunner` gives it once-only handling.

## 8. Migrations

`env.py` must use the connection and schema alembic-gauntlet injects, and otherwise build
its own engine from the same settings the service uses.

```python title="migrations/env.py"
import asyncio
import os

from alembic import context
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from sqlalchemy_foundation_kit import load_orm_metadata

config = context.config
target_schema = config.attributes.get("target_schema") or os.getenv("MIGRATION_SCHEMA", "public")
target_metadata = load_orm_metadata(["orders_service.db"])


def do_run_migrations(connection: Connection) -> None:
    if target_schema != "public":
        connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{target_schema}"'))
        connection.execute(text(f'SET LOCAL search_path TO "{target_schema}"'))   # LOCAL, never plain SET
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # None for public: an explicit "public" makes autogenerate drop alembic_version
        version_table_schema=None if target_schema == "public" else target_schema,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    from orders_service.runtime.settings import Settings

    engine = create_async_engine(Settings().postgres.to_dsn(), poolclass=NullPool)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


if config.attributes.get("connection") is not None:
    do_run_migrations(config.attributes["connection"])
else:
    asyncio.run(run_migrations_online())
```

```python title="tests/test_migrations.py"
from typing import ClassVar

import pytest
from sqlalchemy import MetaData

from alembic_gauntlet import MigrationTestBase
from alembic_gauntlet.contrib.testcontainers import migration_db_url  # noqa: F401  (PostgreSQL 17 in Docker)
from sqlalchemy_foundation_kit import load_orm_metadata


class TestMigrations(MigrationTestBase):
    # the kit's convention names indexes "<table>_<column>_idx"; omni-box's tables use "idx_..."
    allowed_index_prefixes: ClassVar[list[str]] = ["idx_"]

    @pytest.fixture
    def orm_metadata(self) -> MetaData:
        return load_orm_metadata(["orders_service.db"])
```

```toml title="pyproject.toml"
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

The seven inherited tests run every migration up and down one step at a time, compare the
result with the models, and check names, enums and a single head. Run pytest from the
directory that holds `alembic.ini`. Migrations run inside one transaction there, so
`CREATE INDEX CONCURRENTLY` needs a migration of its own with `autocommit_block()`.

Write each migration so the previous version of the service keeps working while it runs:
add a column, write both, backfill, switch reads, drop the old one, across releases. Apply
them with `alembic upgrade head` as a job before the rollout, never from the service's
startup.

## Other libraries, in one paragraph each

**clientwright.** `build("httpx", config, deps)` returns a real `httpx.AsyncClient` with
retries, a circuit breaker and a total deadline underneath. Build one `ClientRuntime` per
process; with dishka, `ClientwrightProvider("httpx", config, component="payments")` per
upstream. `AdapterDeps(header_providers=servicewright_headers())` forwards the request id.
A POST is not retried unless it is marked idempotent; do not add tenacity on top.

**grpc-server-kit and grpc-client-kit.** A gRPC server is servicewright's
`GrpcEntrypoint`, in the same process as the HTTP one if you like;
`GrpcConfig.from_settings(settings.grpc)` reads the kit's `BaseGrpcServerSettings`. Its
readiness goes to the standard health service. Callers use grpc-client-kit:
`*grpc_client_providers(settings.users_grpc)` in the container, then
`factory.create_client(UserStub)`. Enter the factory before the first RPC; keep kit retries
and a native `retryPolicy` apart.

**aiokafka-foundation-kit.** Builds `AIOKafkaProducer` and `AIOKafkaConsumer` from
settings: `producer_lifecycle(settings)`, `consumer_lifecycle(settings, topics=...)`. It has
no consumer loop, retries or dead-letter topic: the loop is your `ScopedEntrypoint`, the
once-only handling is omni-box's inbox. Auto-commit is off; commit after handling.

**deadline-budget.** `BudgetContext.create(total_seconds=..., call_caps={...})` once per
request, never at APP scope: the clock starts at construction. Pass
`ctx.timeout_for_call("payments.charge")` to each call. clientwright and grpc-client-kit
read an ambient budget only after their own `use_budget(ctx)`; they do not share one.

**pg-partsmith.** For a table partitioned by time: `TablePartitionConfig` plus
`PartitionMaintainer(service).run_maintenance_safe(config)` from a scheduled job, with an
`AsyncEngine` (`AsyncSessionManager.engine`), never a session. The parent table and its
indexes stay in your Alembic migrations; pg-partsmith creates partitions ahead and detaches
and drops expired ones.

## Rules that break a service when ignored

1. servicewright owns the process: no FastAPI lifespan, no `asyncio.run` of your own around
   the app, no second request scope from `setup_dishka`.
2. Every client lives in the APP scope and is built by its provider; nothing is built at
   import time or per request.
3. One transaction per unit of work, opened by `uow.transaction()`; repositories flush and
   never commit. Never `asyncio.gather` over one session.
4. Events go through the outbox in the same transaction as the state they describe. Never
   produce to Kafka inside a database transaction.
5. Delivery is at least once: consumers deduplicate (omni-box inbox), HTTP writes take an
   `Idempotency-Key` (idempotency-kit).
6. Every outbound call has a timeout, and retries live in exactly one layer.
7. Migrations are backward compatible with the running version and tested by
   alembic-gauntlet in CI.
8. Pass `None` for every observability backend you do not run, and install the extras for
   the ones you do.

## Engineering assets

A service repository gets its agent instructions, guidelines and Claude Code skills from a
hub, the way every Bedrock Python library gets them from
[bedrock-python/engineering-assets](https://github.com/bedrock-python/engineering-assets).
The hub is a repository your organisation creates from
[engineering-assets-template](https://github.com/bedrock-python/engineering-assets-template);
[touchmark](https://bedrock-python.github.io/touchmark/) opens a pull request in every
subscribed repository whenever a pack changes, and never overwrites a file a team has
changed.

For a service, the template's packs are `agents` (`AGENTS.md`, a project profile
`.agents/project.md`, review prompts), `python-service` (Python, testing and database
guidelines under `.agents/guidelines/`; `app-start`, `app-stop`, `test` and `fmt` skills)
and `claude` (`CLAUDE.md`, settings, a reviewer subagent).

```yaml title="targets.yml in the hub"
version: 1
targets:
  - org: acme
    match: [acme/*-service]
    packs: [agents, python-service, claude]
```

```yaml title=".engineering-assets.yml in the service; an empty file is enough"
version: 1
```

After the first sync, fill in `.agents/project.md` (commands to install, test and run,
conventions): it belongs to the repository and the hub never touches it again. Before the
hub's CI is set up, `touchmark apply --hub <hub checkout>` writes the packs into a local
checkout of a repository that `targets.yml` lists. The template's README has the setup for
GitHub, GitLab, Gitea, Forgejo, Bitbucket and Azure DevOps.

## Before shipping

- [ ] `alembic upgrade head` runs as a job before the rollout; the gauntlet tests pass in CI.
- [ ] Readiness probe on `/system/health/readyz`, liveness on `/system/health/livez`.
- [ ] `terminationGracePeriodSeconds` above delay + grace + cleanup.
- [ ] The scheduler runs at one replica.
- [ ] `POSTGRES__POOL__*` sized for replicas × pool size below the database's connection limit.
- [ ] Secrets come from the environment, never from the image or the repository.
- [ ] Metrics are scraped from every process, the worker included.

## Pages for agents

| Library | Page |
|---|---|
| servicewright | <https://bedrock-python.github.io/servicewright/agents.md> |
| sqlalchemy-foundation-kit | <https://bedrock-python.github.io/sqlalchemy-foundation-kit/agents.md> |
| alembic-gauntlet | <https://bedrock-python.github.io/alembic-gauntlet/agents.md> |
| omni-box | <https://bedrock-python.github.io/omni-box/agents.md> |
| idempotency-kit | <https://bedrock-python.github.io/idempotency-kit/agents.md> |
| redis-client-kit | <https://bedrock-python.github.io/redis-client-kit/agents.md> |
| aiokafka-foundation-kit | <https://bedrock-python.github.io/aiokafka-foundation-kit/agents.md> |
| clientwright | <https://bedrock-python.github.io/clientwright/agents.md> |
| grpc-server-kit | <https://bedrock-python.github.io/grpc-server-kit/agents.md> |
| grpc-client-kit | <https://bedrock-python.github.io/grpc-client-kit/agents.md> |
| deadline-budget | <https://bedrock-python.github.io/deadline-budget/agents.md> |
| pg-partsmith | <https://bedrock-python.github.io/pg-partsmith/agents.md> |
| touchmark | <https://bedrock-python.github.io/touchmark/agents.md> |
