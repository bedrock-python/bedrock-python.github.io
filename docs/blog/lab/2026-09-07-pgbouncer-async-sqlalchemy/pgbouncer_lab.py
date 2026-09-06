"""PostgreSQL behind PgBouncer in transaction mode: what breaks for asyncpg, and what does not."""

import asyncio
import collections
import sys
import time

from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.postgres import PostgresContainer

from sqlalchemy_foundation_kit import create_async_session_manager
from sqlalchemy_foundation_kit.contrib.settings import BasePostgresConfig, ConnectionSettings, PoolSettings

CLIENTS = 20          # concurrent application connections
QUERIES = 20          # distinct statements per client, so caches fill
DEFAULT_POOL_SIZE = 5 # server connections PgBouncer keeps per user/database


def start_pgbouncer(network, *, extra_env: dict[str, str] | None = None) -> DockerContainer:
    env = {
        "DB_HOST": "db", "DB_PORT": "5432", "DB_USER": "test", "DB_PASSWORD": "test", "DB_NAME": "test",
        "POOL_MODE": "transaction", "AUTH_TYPE": "scram-sha-256",
        "DEFAULT_POOL_SIZE": str(DEFAULT_POOL_SIZE), "MAX_CLIENT_CONN": "200",
        **(extra_env or {}),
    }
    bouncer = DockerContainer("edoburu/pgbouncer:latest").with_exposed_ports(5432).with_network(network)
    for k, v in env.items():
        bouncer = bouncer.with_env(k, v)
    bouncer.start()
    wait_for_logs(bouncer, "process up", timeout=30)
    return bouncer


def url_for(bouncer) -> str:
    return f"postgresql+asyncpg://test:test@{bouncer.get_container_host_ip()}:{bouncer.get_exposed_port(5432)}/test"


first_error: dict[str, str] = {}


async def hammer(engine, label: str) -> None:
    """CLIENTS connections each run QUERIES distinct statements, twice, through the pool."""
    errors: collections.Counter[str] = collections.Counter()
    ok = 0

    async def client(n: int) -> None:
        nonlocal ok
        for round_ in range(2):
            for i in range(QUERIES):
                try:
                    async with engine.connect() as conn:
                        await conn.execute(text(f"SELECT {i} + {n * 0} AS v"))  # distinct text per i
                    ok += 1
                except Exception as error:  # noqa: BLE001
                    errors[type(error).__name__] += 1
                    first_error.setdefault(label, str(error).splitlines()[0][:160])

    started = time.perf_counter()
    await asyncio.gather(*(client(n) for n in range(CLIENTS)))
    took = time.perf_counter() - started
    print(f"  {label:<58} ok={ok:<4} errors={dict(errors) or 'none'}  ({took:.1f}s)")
    if label in first_error:
        print(f"      first error: {first_error[label]}")


async def session_state_leak(url: str) -> None:
    engine = create_async_engine(url, poolclass=__import__("sqlalchemy.pool", fromlist=["NullPool"]).NullPool,
                                 connect_args={"statement_cache_size": 0})
    async with engine.connect() as a:
        await a.execute(text("SET search_path TO leaked"))     # plain SET, no transaction around it
        await a.commit()
    async with engine.connect() as b:                           # a different client connection
        seen = (await b.execute(text("SHOW search_path"))).scalar()
    print(f"  client A ran SET search_path TO leaked; client B sees search_path = {seen!r}")
    await engine.dispose()


async def scenarios(direct_url: str, bouncer_url: str, bouncer_ps0_url: str, bouncer_ignore_url: str) -> None:
    print("--- plain SQLAlchemy + asyncpg, driver defaults (statement cache on) ---")
    for label, url in (("direct to PostgreSQL", direct_url),
                       ("PgBouncer transaction mode, defaults (max_prepared_statements=200)", bouncer_url),
                       ("PgBouncer transaction mode, max_prepared_statements=0 (pre-1.22 default)", bouncer_ps0_url)):
        engine = create_async_engine(url, pool_size=10, max_overflow=10)
        await hammer(engine, label)
        await engine.dispose()

    print("\n--- sqlalchemy-foundation-kit, its pgbouncer-safe settings ---")
    for label, url in (("PgBouncer transaction mode, defaults", bouncer_url),
                       ("PgBouncer with ignore_startup_parameters=jit,search_path", bouncer_ignore_url)):
        host, port = url.split("@")[1].split("/")[0].split(":")
        config = BasePostgresConfig(
            connection=ConnectionSettings(host=host, port=int(port), user="test", password=SecretStr("test"), database="test"),
            pool=PoolSettings(size=10, max_overflow=10),
            application_name="pgbouncer-lab",
            use_orjson_serialization=False,
        )
        manager = create_async_session_manager(config)
        await hammer(manager.engine, label)
        await manager.aclose()

    print("\n--- session state through PgBouncer, transaction mode, one server connection ---")
    await session_state_leak(bouncer_url)


with Network() as network:
    with PostgresContainer("postgres:17-alpine", username="test", password="test", dbname="test").with_network(network).with_network_aliases("db") as pg:
        direct = pg.get_connection_url().replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
        b1 = start_pgbouncer(network)
        b2 = start_pgbouncer(network, extra_env={"MAX_PREPARED_STATEMENTS": "0"})
        b3 = start_pgbouncer(network, extra_env={"IGNORE_STARTUP_PARAMETERS": "jit,search_path"})
        try:
            asyncio.run(scenarios(direct, url_for(b1), url_for(b2), url_for(b3)))
        finally:
            b1.stop(); b2.stop(); b3.stop()
