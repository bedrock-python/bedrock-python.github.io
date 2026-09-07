"""What a SQLAlchemy connection pool looks like from the outside while it runs out of connections."""

import asyncio
import re
import time

from prometheus_client import REGISTRY, generate_latest
from sqlalchemy import text
from sqlalchemy.exc import TimeoutError as PoolTimeout
from testcontainers.postgres import PostgresContainer

from sqlalchemy_foundation_kit import AsyncSessionManager
from sqlalchemy_foundation_kit.contrib.metrics import PostgresMetrics
from sqlalchemy_foundation_kit.contrib.settings import PoolSettings

WORKERS = 8


def sample() -> dict[str, float]:
    out: dict[str, float] = {}
    for line in generate_latest(REGISTRY).decode().splitlines():
        if line.startswith("postgres_db_") and not line.startswith("#"):
            name, value = line.rsplit(" ", 1)
            out[name] = float(value)
    return out


previous = {"count": 0.0, "sum": 0.0}


def describe(s: dict[str, float]) -> str:
    size = s.get("postgres_db_pool_size", 0)
    out = s.get("postgres_db_pool_checked_out", 0)
    over = s.get("postgres_db_pool_overflow", 0)
    count = s.get("postgres_db_connection_checkout_duration_seconds_count", 0)
    total = s.get("postgres_db_connection_checkout_duration_seconds_sum", 0)
    timeouts = sum(v for k, v in s.items() if k.startswith("postgres_db_connection_timeouts_total"))
    errors = sum(v for k, v in s.items() if k.startswith("postgres_db_connection_errors_total"))
    dc, ds = count - previous["count"], total - previous["sum"]
    previous.update(count=count, sum=total)
    wait = ds / dc if dc else 0.0
    return f"in_use={out:.0f}/{size + over:.0f}  checkouts/s={dc * 2:4.0f}  checkout wait={wait * 1000:5.0f} ms  timeouts_total={timeouts:.0f} errors_total={errors:.0f}"


async def main(url: str) -> None:
    manager = AsyncSessionManager(url, poolclass="async_adapted_queue", metrics=PostgresMetrics(),
                                  pool_settings=PoolSettings(size=2, max_overflow=2, timeout=1.0))
    query_seconds = {"value": 0.05}
    stop = asyncio.Event()
    failures = {"pool_timeout": 0}

    async def worker() -> None:
        while not stop.is_set():
            try:
                async with manager.get_session() as session:
                    await session.execute(text("SELECT pg_sleep(:s)"), {"s": query_seconds["value"]})
            except PoolTimeout:
                failures["pool_timeout"] += 1
                await asyncio.sleep(0.05)

    tasks = [asyncio.create_task(worker()) for _ in range(WORKERS)]
    t0 = time.perf_counter()
    print(f"--- {WORKERS} workers, pool_size=2, max_overflow=2, pool_timeout=1.0 s ---")
    for tick in range(16):
        await asyncio.sleep(0.5)
        if tick == 6:
            query_seconds["value"] = 1.0   # the database slows down: each query now holds a connection for a second
            print("  ... the database slows down: queries take 1.0 s instead of 0.05 s")
        print(f"  {time.perf_counter() - t0:4.1f} s  {describe(sample())}  requests failed on pool timeout={failures['pool_timeout']}")
    stop.set()
    await asyncio.gather(*tasks)
    await manager.aclose()


with PostgresContainer("postgres:17-alpine") as pg:
    asyncio.run(main(pg.get_connection_url().replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)))
