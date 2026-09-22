"""Observe connection lifetimes, concurrent sessions and external waits on PostgreSQL."""

import asyncio
from pathlib import Path
import sys

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, TimeoutError as PoolTimeout
from sqlalchemy_foundation_kit import AsyncSQLAlchemyUnitOfWork
from testcontainers.community.postgres import PostgresContainer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "2026-09-07-unit-of-work-sqlalchemy-2"))
import order_flow as flow
from models import Base
from uow_lab import counts, reset


async def compare_external_wait(engine, sessions, uow, *, inside):
    release, both_waiting = asyncio.Event(), asyncio.Event()
    arrivals = 0

    async def quote_shipping(sku):
        nonlocal arrivals
        arrivals += 1
        if arrivals == 2:
            both_waiting.set()
        await release.wait()
        return 250

    async def slow_order(sku):
        if not inside:
            return await flow.place_order_after_quote(uow, quote_shipping, sku)
        async with uow.transaction() as tx:
            order = await tx.orders.add(sku)
            order.delivery_cents = await quote_shipping(sku)
            await tx.events.add(order.id)
            result = {"order_id": order.id}
        return result

    tasks = [asyncio.create_task(slow_order(f"sku-{i}")) for i in range(2)]
    try:
        await asyncio.wait_for(both_waiting.wait(), 5)
        held = engine.pool.checkedout()
        assert held == (2 if inside else 0), held
        try:
            async with sessions() as observer:
                assert await observer.scalar(text("SELECT 1")) == 1
        except PoolTimeout:
            assert inside, "No connection should be held while quoting before the transaction"
            print("quote inside transaction: both connections held, third request hits pool timeout")
        else:
            assert not inside, "Both connections should still be occupied"
            print("quote before transaction: no connections held, third request succeeds")
    finally:
        release.set()
        results = await asyncio.gather(*tasks, return_exceptions=True)
    assert all(isinstance(result, dict) for result in results), results
    assert await counts(sessions) == (2, 2, 0)
    async with sessions() as observer:
        assert await observer.scalar(text("SELECT sum(delivery_cents) FROM orders")) == 500
    assert engine.pool.checkedout() == 0


async def main(url):
    engine, sessions = flow.open_database(url)
    uow = flow.make_uow(sessions)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
            print("PostgreSQL", await connection.scalar(text("SHOW server_version")))

        async with sessions() as session:
            assert engine.pool.checkedout() == 0
            await session.execute(text("SELECT 1"))
            assert engine.pool.checkedout() == 1
        assert engine.pool.checkedout() == 0
        print("new session: 0 connections; first query: 1; closed session: 0")

        await compare_external_wait(engine, sessions, uow, inside=True)
        await reset(sessions)
        await compare_external_wait(engine, sessions, uow, inside=False)
        await reset(sessions)

        # Drain both tasks before closing the session, including the rejected operation.
        async with sessions() as shared:
            results = await asyncio.gather(
                shared.execute(text("SELECT pg_sleep(0.05)")),
                shared.execute(text("SELECT pg_sleep(0.05)")),
                return_exceptions=True,
            )
            errors = [result for result in results if isinstance(result, BaseException)]
            assert all(isinstance(error, SQLAlchemyError) for error in errors), results
        # Unsupported sharing need not fail on every run: some calls may be serialized.
        outcome = ", ".join(type(error).__name__ for error in errors) if errors else "both calls completed"
        print("one session used concurrently:", outcome, "(not a supported usage contract)")
        assert engine.pool.checkedout() == 0

        # Keep references so session object IDs cannot be reused during the assertion.
        opened_sessions = []

        class ObservedTransaction(flow.OrderTransaction):
            def __init__(self, session):
                super().__init__(session)
                opened_sessions.append(session)

        observed_uow = AsyncSQLAlchemyUnitOfWork(
            sessions, transaction_factory=ObservedTransaction,
        )
        results = await flow.place_independent_orders(
            observed_uow, [f"sku-{i}" for i in range(6)],
        )
        assert len(results) == 6
        assert len({result["order_id"] for result in results}) == 6
        assert len({id(session) for session in opened_sessions}) == 6
        assert await counts(sessions) == (6, 6, 0)
        assert engine.pool.checkedout() == 0
        print("six independent orders: six sessions, six order/event pairs, all connections returned")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    with PostgresContainer("postgres:17-alpine", driver="asyncpg") as postgres:
        asyncio.run(main(postgres.get_connection_url()))
    print("PASS: session and pool scenarios")
