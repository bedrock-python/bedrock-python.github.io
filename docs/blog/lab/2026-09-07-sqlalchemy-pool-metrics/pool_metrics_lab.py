"""Locate waits with real PostgreSQL/PgBouncer and the kit's exported Prometheus metrics."""
import asyncio
from pathlib import Path
import sys

from prometheus_client import REGISTRY
from sqlalchemy import text
from sqlalchemy.exc import TimeoutError as PoolTimeout
from sqlalchemy_foundation_kit import create_async_session_manager

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "2026-09-07-pgbouncer-async-sqlalchemy"))
from lab_support import DatabaseLab, Shipping, seed, wait_until
from pool_flow import (
    get_order, instrumented_manager, order_with_quote_after, order_with_quote_inside,
)


def metric(prefix, suffix):
    return REGISTRY.get_sample_value(f"{prefix}_postgres_db_{suffix}") or 0.0


async def local_queue(config):
    config = config.model_copy(update={"pool": config.pool.model_copy(update={"size": 1, "pre_ping": False})})
    async with instrumented_manager(config, "local") as manager:
        started, release = asyncio.Event(), asyncio.Event()
        async def holder():
            async with manager.get_transaction() as session:
                await session.execute(text("SELECT 1"))
                started.set()
                await release.wait()
        first = asyncio.create_task(holder())
        try:
            await started.wait()
            assert manager.engine.pool.checkedout() == 1
            before = metric("local", "connection_timeouts_total")
            try:
                await get_order(manager, 42)
            except PoolTimeout:
                pass
            else:
                raise AssertionError("Second checkout must hit the local pool timeout")
            assert metric("local", "connection_timeouts_total") == before + 1
            assert metric("local", "connection_checkout_wait_seconds_count") == 2
        finally:
            release.set()
            await first
        assert manager.engine.pool.checkedout() == 0
        assert await get_order(manager, 42) == {"id": 42, "total": 1999}
    print("PASS local pool: one held connection, one timeout, exported counter +1, recovery")


async def holding(config):
    async with instrumented_manager(config, "holding") as manager:
        await get_order(manager, 42)  # Warm connection and caches before observations.
        before = metric("holding", "connection_held_duration_seconds_sum")
        async with manager.get_transaction() as session:
            await session.execute(text("SELECT pg_sleep(0.2)"))
        held = metric("holding", "connection_held_duration_seconds_sum") - before
        assert held >= 0.19
        print(f"PASS slow SQL: held histogram grew by {held:.3f}s for pg_sleep(0.2)")

        for action, expected in ((order_with_quote_inside, 1), (order_with_quote_after, 0)):
            shipping = Shipping()
            task = asyncio.create_task(action(manager, 42, shipping))
            try:
                await shipping.started.wait()
                assert manager.engine.pool.checkedout() == expected
                # There is no SQL in flight now; the remote-service fixture holds the task.
                await asyncio.sleep(0.05)
                assert not task.done()
            finally:
                shipping.release.set()
                response = await task
            assert response == {"id": 42, "total": 1999, "shipping": 350}
            assert manager.engine.pool.checkedout() == 0
            print(f"PASS {action.__name__}: connections held during external wait={expected}")


async def second_queue(bouncer):
    config = bouncer.config()
    config = config.model_copy(update={
        "db_schema": None,
        "pool": config.pool.model_copy(update={"pre_ping": False}),
    })
    async with instrumented_manager(config, "bouncer") as manager:
        # Warm both client connections. No pre-ping or schema hook can issue SQL during checkout.
        async with manager.engine.connect() as a, manager.engine.connect() as b:
            await a.execute(text("SELECT 1"))
            await a.commit()
            await b.execute(text("SELECT 1"))
            await b.commit()
        acquired, release, second_acquired = asyncio.Event(), asyncio.Event(), asyncio.Event()
        async def holder():
            async with manager.engine.begin() as connection:
                await connection.execute(text("SELECT 1"))
                acquired.set()
                await release.wait()
        async def waiter():
            async with manager.engine.connect() as connection:
                second_acquired.set()
                return (await connection.execute(text("SELECT 42"))).scalar_one()
        first = asyncio.create_task(holder())
        second = None
        try:
            await acquired.wait()
            count = metric("bouncer", "connection_checkout_wait_seconds_count")
            second = asyncio.create_task(waiter())
            await second_acquired.wait()
            assert metric("bouncer", "connection_checkout_wait_seconds_count") == count + 1
            def is_queued():
                pools = bouncer.admin("SHOW POOLS")
                return any(row["database"] == "test" and int(row["cl_waiting"]) == 1 for row in pools)
            await wait_until(is_queued)
            assert not second.done()
            assert manager.engine.pool.checkedout() == 2
            assert metric("bouncer", "connection_timeouts_total") == 0
            assert bouncer.admin("SHOW STATS")
        finally:
            release.set()
            await first
            if second is not None:
                assert await second == 42
        assert manager.engine.pool.checkedout() == 0
    print("PASS PgBouncer queue: SQLAlchemy checkout completed; cl_waiting=1; no local timeout")


async def main(lab, bouncer):
    async with asyncio.timeout(40):
        config = lab.direct_config()
        async with create_async_session_manager(config) as manager:
            await seed(manager)
        await local_queue(config)
        await holding(config)
        await second_queue(bouncer)


if __name__ == "__main__":
    with DatabaseLab() as lab:
        bouncer = lab.bouncer(default_pool_size=1)
        asyncio.run(main(lab, bouncer))
