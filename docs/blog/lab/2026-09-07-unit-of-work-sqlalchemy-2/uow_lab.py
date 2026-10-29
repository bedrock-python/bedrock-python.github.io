"""Verify the article's transaction boundaries on a real PostgreSQL database."""

import asyncio
from importlib.metadata import version

from sqlalchemy import func, select, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from testcontainers.community.postgres import PostgresContainer

from models import Base, NewsletterSubscription, Order, OrderEvent
import order_flow as flow


async def counts(session_factory):
    async with session_factory() as session:
        return tuple([
            await session.scalar(select(func.count()).select_from(model))
            for model in (Order, OrderEvent, NewsletterSubscription)
        ])


async def reset(session_factory):
    async with session_factory.begin() as session:
        await session.execute(text(
            "TRUNCATE order_events, orders, newsletter_subscriptions RESTART IDENTITY"
        ))


async def expect_error(kind, command, sqlstate=None):
    try:
        await command
    except kind as error:
        if sqlstate is not None:
            assert error.orig.sqlstate == sqlstate, error
        return
    raise AssertionError(f"Expected {kind.__name__}")


async def main(url):
    engine, session_factory = flow.open_database(url)
    uow = flow.make_uow(session_factory)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
            print("PostgreSQL", await connection.scalar(text("SHOW server_version")))
        print(", ".join(f"{name} {version(name)}" for name in (
            "sqlalchemy-foundation-kit", "SQLAlchemy", "asyncpg",
        )))

        await expect_error(
            IntegrityError,
            flow.place_order_broken(session_factory, "sku-1", event_kind=""),
            "23514",
        )
        assert await counts(session_factory) == (1, 0, 0)
        print("two commits + rejected event: orders=1, events=0")
        await reset(session_factory)

        await expect_error(
            IntegrityError,
            flow.place_order_native(session_factory, "sku-1", event_kind=""),
            "23514",
        )
        assert await counts(session_factory) == (0, 0, 0)
        print("session_factory.begin() + rejected event: orders=0, events=0")

        await flow.verify_rollback(uow, session_factory)
        print("uow.transaction() + rejected event: orders=0, events=0")

        # A generated ID after flush is not evidence that the row has committed.
        async with uow.transaction() as tx:
            order = await tx.orders.add("sku-flushed")
            assert order.id is not None
            assert await counts(session_factory) == (0, 0, 0)
            await tx.events.add(order.id)
        assert await counts(session_factory) == (1, 1, 0)
        print("flush: ID available, observer sees no row; commit: both rows visible")
        await reset(session_factory)

        for create in (
            lambda: flow.place_order_native(session_factory, "sku-native"),
            lambda: flow.place_order(uow, "sku-kit", delivery_cents=250),
        ):
            result = await create()
            dto = await flow.read_order(uow, result["order_id"])
            assert dto["order_id"] == result["order_id"]
        assert await counts(session_factory) == (2, 2, 0)
        print("successful native and kit contexts: one order and event per operation")

        first = await flow.place_order_with_subscription(uow, "sku-1", "buyer@example.org")
        second = await flow.place_order_with_subscription(uow, "sku-2", "buyer@example.org")
        assert first != second
        assert await counts(session_factory) == (4, 4, 1)
        print("duplicate optional subscription: two orders committed, one subscription")

        # A different integrity error must escape, rolling back mandatory writes too.
        await expect_error(
            IntegrityError,
            flow.place_order_with_subscription(uow, "sku-invalid", ""),
            "23514",
        )
        assert await counts(session_factory) == (4, 4, 1)
        print("unexpected subscription error: whole operation rolled back")

        async with uow.query() as tx:
            await tx.orders.add("discarded")
        assert await counts(session_factory) == (4, 4, 1)
        # query() does not enforce READ ONLY: a caller can explicitly commit a write.
        async with uow.query() as tx:
            await tx.orders.add("explicitly-committed")
            await tx.session.commit()
        assert await counts(session_factory) == (5, 4, 1)
        print("query(): uncommitted INSERT discarded, explicit commit remains possible")

        try:
            async with uow.query() as tx:
                await tx.session.execute(text("SET TRANSACTION READ ONLY"))
                await tx.orders.add("forbidden")
        except DBAPIError as error:
            assert error.orig.sqlstate == "25006"
        else:
            raise AssertionError("PostgreSQL should reject the INSERT")
        assert await counts(session_factory) == (5, 4, 1)
        print("SET TRANSACTION READ ONLY: INSERT rejected by PostgreSQL (25006)")
        await reset(session_factory)

        # Cancel before commit, after the order INSERT has reached PostgreSQL.
        inserted, release = asyncio.Event(), asyncio.Event()

        async def cancelled_order():
            async with uow.transaction() as tx:
                await tx.orders.add("cancelled")
                inserted.set()
                await release.wait()
                await tx.events.add(1)

        task = asyncio.create_task(cancelled_order())
        try:
            await asyncio.wait_for(inserted.wait(), 5)
            task.cancel()
            await expect_error(asyncio.CancelledError, task)
        finally:
            release.set()
            await asyncio.gather(task, return_exceptions=True)
        assert await counts(session_factory) == (0, 0, 0)
        assert engine.pool.checkedout() == 0
        print("cancellation before commit: no rows, no checked-out connections")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    with PostgresContainer("postgres:17-alpine", driver="asyncpg") as postgres:
        asyncio.run(main(postgres.get_connection_url()))
    print("PASS: transaction scenarios")
