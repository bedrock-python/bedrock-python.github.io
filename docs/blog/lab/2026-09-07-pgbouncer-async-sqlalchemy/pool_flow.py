"""Application code extracted verbatim into the article."""

# snippet:config
from pydantic import SecretStr
from sqlalchemy_foundation_kit import create_async_session_manager
from sqlalchemy_foundation_kit.contrib.settings import (
    BasePostgresConfig, ConnectionSettings, PoolSettings, QuerySettings,
)


def database_config(host, port, user, password, database):
    return BasePostgresConfig(
        connection=ConnectionSettings(
            host=host, port=port, user=user,
            password=SecretStr(password), database=database,
        ),
        application_name="orders-api",
        db_schema="app",
        jit=None,
        use_orjson_serialization=False,
        pool=PoolSettings(size=2, max_overflow=0, timeout=0.2),
        query=QuerySettings(
            statement_cache_size=100,
            prepared_statement_cache_size=100,
        ),
    )
# /snippet:config

# snippet:lookup
from sqlalchemy import text


async def get_order(manager, order_id):
    async with manager.get_transaction() as session:
        row = (await session.execute(
            text("SELECT id, total FROM orders WHERE id = :id"),
            {"id": order_id},
        )).mappings().one()
        return dict(row)
# /snippet:lookup

# snippet:settings
async def effective_settings(manager):
    async with manager.get_transaction() as session:
        return {
            name: (await session.execute(text(f"SHOW {name}"))).scalar_one()
            for name in ("jit", "search_path", "application_name")
        }
# /snippet:settings

# snippet:local_timeout
async def slow_query_with_limit(manager):
    async with manager.get_transaction() as session:
        await session.execute(text("SET LOCAL statement_timeout = '100ms'"))
        await session.execute(text("SELECT pg_sleep(1)"))
# /snippet:local_timeout

# snippet:bad_hold
async def order_with_quote_inside(manager, order_id, shipping):
    async with manager.get_transaction() as session:
        row = (await session.execute(
            text("SELECT id, total FROM orders WHERE id = :id"),
            {"id": order_id},
        )).mappings().one()
        quote = await shipping.quote(order_id)
        return {**dict(row), "shipping": quote}
# /snippet:bad_hold

# snippet:good_hold
async def order_with_quote_after(manager, order_id, shipping):
    order = await get_order(manager, order_id)
    quote = await shipping.quote(order_id)
    return {**order, "shipping": quote}
# /snippet:good_hold

# snippet:metrics
from sqlalchemy_foundation_kit.contrib.metrics import PostgresMetrics


def instrumented_manager(config, prefix="orders"):
    metrics = PostgresMetrics(prefix=prefix)
    return create_async_session_manager(config, metrics=metrics)
# /snippet:metrics
