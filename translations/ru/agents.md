---
title: Сборка сервиса
description: Одна страница для ИИ-ассистента, который собирает продакшн-сервис на async Python из библиотек Bedrock Python.
copy_page: true
---

# Сервис на библиотеках Bedrock Python

> Одна страница для ИИ-ассистента, который с нуля собирает продакшн-сервис на async
> Python из библиотек Bedrock Python: какая библиотека закрывает какую задачу, как они
> собираются в одну кодовую базу и где у каждой библиотеки своя страница для агентов.
> Дайте агенту сначала эту страницу, потом страницы для агентов тех библиотек, которые он
> выберет.

## Как читать эту страницу

У каждой библиотеки есть одностраничный справочник для ассистентов:
`https://bedrock-python.github.io/<repo>/agents/`, а его Markdown лежит по адресу
`https://bedrock-python.github.io/<repo>/agents.md`. Markdown этой страницы:
`https://bedrock-python.github.io/ru/agents.md`, английской версии:
`https://bedrock-python.github.io/agents.md`. Здесь показано, как библиотеки соединяются
между собой, а не весь их API. Прежде чем писать код под библиотеку, загрузите её страницу
для агентов. Если имя на этой странице расходится со страницей библиотеки, права страница
библиотеки.

Код ниже это один сервис `orders`, собранный из опубликованных версий библиотек и
запущенный 11 ноября 2026 года против PostgreSQL 17, Redis 7 и Kafka 3.9: API, воркер,
миграции и их тесты. Копируйте устройство, а не предметную область.

## Выбор библиотек

Ставьте только то, что сервису нужно. Python 3.12 или новее: этого требуют servicewright и
omni-box.

| Сервису нужно | Библиотека | Установка |
|---|---|---|
| Один жизненный цикл процесса для HTTP, gRPC, cron, демонов и разовых задач: пробы здоровья, плавная остановка, логи и метрики | [servicewright](https://bedrock-python.github.io/servicewright/agents/) | `servicewright[fastapi,dishka,settings,metrics,observability]`, плюс `apscheduler3` для cron, `grpc` для gRPC-сервера, `postgres` / `redis` для готовых проверок здоровья |
| PostgreSQL через асинхронную SQLAlchemy | [sqlalchemy-foundation-kit](https://bedrock-python.github.io/sqlalchemy-foundation-kit/agents/) | `sqlalchemy-foundation-kit[settings,dishka,metrics]` |
| Миграции Alembic, проверенные до продакшна | [alembic-gauntlet](https://bedrock-python.github.io/alembic-gauntlet/agents/) | только для разработки: `alembic-gauntlet[asyncio,testcontainers]` |
| Событие, которое уходит ровно тогда, когда закоммичена транзакция (outbox), или входящие сообщения, обработанные один раз (inbox) | [omni-box](https://bedrock-python.github.io/omni-box/agents/) | `omni-box[postgres,kafka]` |
| Повторный POST не должен создать второй заказ | [idempotency-kit](https://bedrock-python.github.io/idempotency-kit/agents/) | `idempotency-kit[redis,dishka,prometheus]` |
| Redis | [redis-client-kit](https://bedrock-python.github.io/redis-client-kit/agents/) | `redis-client-kit[settings,providers,metrics]` |
| Продюсеры и консьюмеры Kafka | [aiokafka-foundation-kit](https://bedrock-python.github.io/aiokafka-foundation-kit/agents/) | `aiokafka-foundation-kit[models,dishka]` |
| Исходящие HTTP-вызовы с ретраями, circuit breaker и общим дедлайном | [clientwright](https://bedrock-python.github.io/clientwright/agents/) | `clientwright[httpx,settings,dishka,metrics,servicewright]` |
| gRPC-сервер | extra `grpc` у servicewright, построенный на [grpc-server-kit](https://bedrock-python.github.io/grpc-server-kit/agents/) | `servicewright[grpc]` |
| gRPC-клиент | [grpc-client-kit](https://bedrock-python.github.io/grpc-client-kit/agents/) | `grpc-client-kit[settings,dishka,metrics,health]` |
| Один бюджет времени на запрос, поделённый между вызовами вниз по цепочке | [deadline-budget](https://bedrock-python.github.io/deadline-budget/agents/) | `deadline-budget` или extra `deadline` у clientwright / grpc-client-kit |
| Таблицы, секционированные по времени: секции создаются заранее и удаляются после срока хранения | [pg-partsmith](https://bedrock-python.github.io/pg-partsmith/agents/) | `pg-partsmith` |
| Одинаковые AGENTS.md, гайдлайны и CI-файлы во всех репозиториях | [touchmark](https://bedrock-python.github.io/touchmark/agents/) и [engineering-assets-template](https://github.com/bedrock-python/engineering-assets-template) | репозиторий-хаб, см. [Engineering assets](#engineering-assets) |

## Устройство сервиса

Одна кодовая база, один образ, несколько процессов. У API и воркера общие настройки,
контейнер и проверки здоровья; различается только список точек входа.

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

В деплое один и тот же образ запускается разными командами:
`python -m orders_service.api_main`, `python -m orders_service.worker_main` и
`alembic upgrade head` отдельной задачей перед выкаткой новой версии. В большой кодовой
базе `orders.py` раскладывается на `core/`, `use_cases/` и `infra/`; это дерево показано в
[project layout](https://bedrock-python.github.io/servicewright/blueprints/project-layout/)
у servicewright.

## 1. Настройки

Один класс pydantic-settings. Каждая библиотека поставляет свою секцию как модель; вложите
их, и имена переменных окружения получатся с `__` между уровнями.

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

В `BaseServiceSettings` уже есть секции `logging`, `metrics`, `tracing` и
`error_tracking` и поле `app_version`; servicewright читает их по форме объекта.
Обязательные поля в этом примере: `POSTGRES__CONNECTION__PASSWORD`,
`POSTGRES__CONNECTION__DATABASE`, `POSTGRES__APPLICATION_NAME`, `REDIS__KEY_PREFIX`,
`IDEMPOTENCY__KEY_PREFIX`, `KAFKA__BOOTSTRAP_SERVERS`.

## 2. Модели

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

`Base` несёт соглашение об именах из sqlalchemy-foundation-kit (`orders_pkey`,
`orders_amount_positive_check`), поэтому имена ограничений не меняются между
автогенерированными миграциями. Давайте имя каждому `CheckConstraint`.

## 3. Сценарии

Строка заказа и его событие коммитятся в одной транзакции. Ретранслятор в воркере
отправляет событие позже. Декоратор идемпотентности на повторный ключ отдаёт первый ответ.

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

Сценарии не импортируют ни servicewright, ни dishka. Репозитории делают `flush()`,
коммитит только `uow.transaction()`. `uow.query()` открывает транзакцию только на чтение.

## 4. Контейнер

dishka сопоставляет зависимости по точному типу. Каждая библиотека запрашивает свои
настройки по протоколу, поэтому один провайдер раздаёт всем библиотекам их секции.

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

servicewright отображает `Scope.APP` из dishka на процесс, а `Scope.REQUEST` на одну
единицу работы: HTTP-запрос, запуск задачи, цикл демона. Не вызывайте вдобавок
`setup_dishka` из dishka на приложении FastAPI: два request-скоупа на запрос дают
`RuntimeError`.

## 5. Spec: наблюдаемость и здоровье

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

`ObsConfig()` без аргументов включает все четыре бэкенда; передавайте `None` для каждого,
который не используете. В Kubernetes `terminationGracePeriodSeconds` должен быть больше
`drain_delay_seconds + drain_grace_seconds + cleanup_timeout_seconds`: здесь это 45 секунд,
значит 60.

## 6. API

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

Пробы: `/system/health/livez` и `/system/health/readyz`. Ошибки отдаются документами
problem details по RFC 9457. Любое исключение, которое не `ServiceError`, превращается в
500 с кодом `internal_error`, а его текст остаётся в логе, поэтому ошибки библиотек, которые
клиент должен увидеть, переводите в `ServiceError`, как выше.

## 7. Воркер

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

Планировщик работает внутри процесса: держите воркер в одной реплике или вынесите
планировщик в отдельный деплой. Упавшая задача пишется в лог, планировщик продолжает
работу. Есть и `apscheduler4`, но все релизы APScheduler 4 пока пре-релизы, и pip с uv
по умолчанию их пропускают. У воркера нет HTTP-порта; для проб и метрик либо включите
`METRICS__ENABLED=true` (отдельный порт для метрик), либо добавьте `FastApiEntrypoint` без
роутеров. Консьюмер Kafka это `ScopedEntrypoint` примерно на тридцать строк: он есть в
blueprint [background worker](https://bedrock-python.github.io/servicewright/blueprints/worker/)
у servicewright, а однократную обработку ему даёт `InboxConsumerRunner` из omni-box.

## 8. Миграции

`env.py` должен брать соединение и схему, которые подставляет alembic-gauntlet, а в
остальных случаях строить свой движок из тех же настроек, что и сервис.

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

Семь унаследованных тестов прогоняют каждую миграцию вверх и вниз по одному шагу,
сравнивают результат с моделями и проверяют имена, enum-ы и единственную голову. Запускайте
pytest из каталога, где лежит `alembic.ini`. Миграции там идут в одной транзакции, поэтому
`CREATE INDEX CONCURRENTLY` нужна отдельная миграция с `autocommit_block()`.

Пишите каждую миграцию так, чтобы предыдущая версия сервиса продолжала работать, пока она
идёт: добавить колонку, писать в обе, заполнить, переключить чтение, удалить старую, по
разным релизам. Применяйте их `alembic upgrade head` отдельной задачей перед выкаткой,
никогда не при старте сервиса.

## Остальные библиотеки, по абзацу

**clientwright.** `build("httpx", config, deps)` возвращает настоящий `httpx.AsyncClient`, под
которым уже стоят ретраи, circuit breaker и общий дедлайн. Один `ClientRuntime` на процесс;
с dishka по одному `ClientwrightProvider("httpx", config, component="payments")` на каждый
внешний сервис. `AdapterDeps(header_providers=servicewright_headers())` пробрасывает
request id. POST не ретраится, пока не помечен идемпотентным; tenacity сверху не добавляйте.

**grpc-server-kit и grpc-client-kit.** gRPC-сервер это `GrpcEntrypoint` из servicewright,
при желании в одном процессе с HTTP; `GrpcConfig.from_settings(settings.grpc)` читает
`BaseGrpcServerSettings` из кита. Готовность уходит в стандартный health-сервис. Вызывающая
сторона использует grpc-client-kit: `*grpc_client_providers(settings.users_grpc)` в
контейнере, затем `factory.create_client(UserStub)`. Входите в фабрику до первого RPC; не
смешивайте ретраи кита с нативной `retryPolicy`.

**aiokafka-foundation-kit.** Строит `AIOKafkaProducer` и `AIOKafkaConsumer` из настроек:
`producer_lifecycle(settings)`, `consumer_lifecycle(settings, topics=...)`. Цикла
потребления, ретраев и dead-letter топика в нём нет: цикл это ваш `ScopedEntrypoint`,
однократная обработка это inbox из omni-box. Автокоммит выключен; коммитьте после
обработки.

**deadline-budget.** `BudgetContext.create(total_seconds=..., call_caps={...})` один раз на
запрос и никогда в APP-скоупе: отсчёт начинается при создании. Передавайте
`ctx.timeout_for_call("payments.charge")` в каждый вызов. clientwright и grpc-client-kit
видят бюджет из контекста только после своего `use_budget(ctx)`; общего у них нет.

**pg-partsmith.** Для таблицы, секционированной по времени: `TablePartitionConfig` и
`PartitionMaintainer(service).run_maintenance_safe(config)` из задачи по расписанию, с
`AsyncEngine` (`AsyncSessionManager.engine`), никогда с сессией. Родительская таблица и её
индексы остаются в ваших миграциях Alembic; pg-partsmith заранее создаёт секции, отцепляет
и удаляет устаревшие.

## Правила, без которых сервис ломается

1. Процессом владеет servicewright: никакого lifespan у FastAPI, никакого своего
   `asyncio.run` вокруг приложения, никакого второго request-скоупа из `setup_dishka`.
2. Каждый клиент живёт в APP-скоупе и создаётся своим провайдером; ничего не создаётся при
   импорте или на каждый запрос.
3. Одна транзакция на единицу работы, её открывает `uow.transaction()`; репозитории делают
   flush и никогда не коммитят. Никакого `asyncio.gather` по одной сессии.
4. События идут через outbox в той же транзакции, что и состояние, которое они описывают.
   Не отправляйте в Kafka внутри транзакции базы.
5. Доставка как минимум один раз: консьюмеры дедуплицируют (inbox из omni-box), записи по
   HTTP принимают `Idempotency-Key` (idempotency-kit).
6. У каждого исходящего вызова есть таймаут, а ретраи живут ровно в одном слое.
7. Миграции обратно совместимы с работающей версией и проверены alembic-gauntlet в CI.
8. Передавайте `None` для каждого бэкенда наблюдаемости, который не используете, и
   ставьте extras для тех, что используете.

## Engineering assets { #engineering-assets }

Репозиторий сервиса получает инструкции для агентов, гайдлайны и скиллы Claude Code из
хаба, так же как каждая библиотека Bedrock Python получает их из
[bedrock-python/engineering-assets](https://github.com/bedrock-python/engineering-assets).
Хаб это репозиторий, который организация создаёт из
[engineering-assets-template](https://github.com/bedrock-python/engineering-assets-template);
[touchmark](https://bedrock-python.github.io/touchmark/) открывает pull request в каждом
подписанном репозитории при любом изменении пака и никогда не перезаписывает файл, который
команда изменила.

Для сервиса из шаблона нужны паки `agents` (`AGENTS.md`, профиль проекта
`.agents/project.md`, промпты для ревью), `python-service` (гайдлайны по Python, тестам и
базе данных в `.agents/guidelines/`; скиллы `app-start`, `app-stop`, `test` и `fmt`) и
`claude` (`CLAUDE.md`, настройки, сабагент-ревьюер).

```yaml title="targets.yml в хабе"
version: 1
targets:
  - org: acme
    match: [acme/*-service]
    packs: [agents, python-service, claude]
```

```yaml title=".engineering-assets.yml в сервисе; достаточно пустого файла"
version: 1
```

После первой синхронизации заполните `.agents/project.md` (команды установки, тестов и
запуска, соглашения): он принадлежит репозиторию, и хаб его больше не трогает. Пока CI хаба
не настроен, `touchmark apply --hub <checkout хаба>` записывает паки в локальный checkout
репозитория, который указан в `targets.yml`. Настройка для GitHub, GitLab, Gitea, Forgejo,
Bitbucket и Azure DevOps описана в README шаблона.

## Перед выкаткой

- [ ] `alembic upgrade head` идёт отдельной задачей перед выкаткой; тесты gauntlet проходят в CI.
- [ ] Проба готовности на `/system/health/readyz`, живости на `/system/health/livez`.
- [ ] `terminationGracePeriodSeconds` больше суммы delay + grace + cleanup.
- [ ] Планировщик работает в одной реплике.
- [ ] `POSTGRES__POOL__*` подобраны так, что реплики × размер пула меньше лимита соединений базы.
- [ ] Секреты приходят из окружения, никогда из образа или репозитория.
- [ ] Метрики собираются со всех процессов, включая воркер.

## Страницы для агентов

| Библиотека | Страница |
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
