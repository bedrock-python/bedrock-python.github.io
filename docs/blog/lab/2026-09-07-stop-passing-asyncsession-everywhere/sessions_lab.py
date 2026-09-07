"""Who owns the session: the caller that threads it, or the unit of work that opens it.

One use case, "place an order", written four ways against PostgreSQL 17 in a container:

1. every repository opens its own session, which is what happens when a session is a parameter
   somebody forgot to pass;
2. the session is threaded through the layers and a repository commits, because it could;
3. one unit of work owns the transaction and the repositories are handed its session;
4. the same, with a savepoint around the part that is allowed to fail.

Each writes an order and an outbox row and then fails, and the lab counts what survived. Then
the same designs are put under a pool of two connections and asked how many requests they serve.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from importlib.metadata import version

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from testcontainers.postgres import PostgresContainer

from sqlalchemy_foundation_kit import (
    AsyncSessionManagerBuilder,
    AsyncSQLAlchemyUnitOfWork,
    AsyncSQLAlchemyUowTransaction,
)

POOL_SIZE = 2


@dataclass(frozen=True)
class Pool:
    """Anything with these attributes satisfies the kit's pool settings protocol."""

    kind: str = "async_adapted_queue"
    size: int = POOL_SIZE
    max_overflow: int = 0
    pre_ping: bool = True
    recycle: int = 3600
    timeout: float = 2.0


def log(msg: str) -> None:
    print(msg, flush=True)


class OrderRepository:
    """A repository that is handed a session, and one that is handed a session maker."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, order_id: int) -> None:
        await self.session.execute(
            text("INSERT INTO orders (id, state) VALUES (:id, 'placed')"), {"id": order_id}
        )


class OutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, order_id: int, *, fail: bool) -> None:
        if fail:
            raise RuntimeError("the serializer blew up on this payload")
        await self.session.execute(
            text("INSERT INTO outbox (order_id, topic) VALUES (:id, 'orders.placed')"), {"id": order_id}
        )


async def counts(session_maker: async_sessionmaker[AsyncSession]) -> tuple[int, int]:
    async with session_maker() as session:
        orders = await session.scalar(text("SELECT count(*) FROM orders"))
        outbox = await session.scalar(text("SELECT count(*) FROM outbox"))
        return orders, outbox


async def reset(session_maker: async_sessionmaker[AsyncSession]) -> None:
    async with session_maker() as session:
        await session.execute(text("TRUNCATE orders, outbox"))
        await session.commit()


# --- the four designs -------------------------------------------------------------------------


async def a_session_per_repository(session_maker, order_id: int, *, fail: bool) -> None:
    """Each repository opens its own session. Nobody wrote this on purpose."""
    async with session_maker() as session:
        await OrderRepository(session).add(order_id)
        await session.commit()
    async with session_maker() as session:
        await OutboxRepository(session).add(order_id, fail=fail)
        await session.commit()


async def b_threaded_and_committed(session_maker, order_id: int, *, fail: bool) -> None:
    """One session, passed down, and a repository that commits because it has the session."""
    async with session_maker() as session:
        await OrderRepository(session).add(order_id)
        await session.commit()  # the repository "finishes its work"
        await OutboxRepository(session).add(order_id, fail=fail)
        await session.commit()


async def c_unit_of_work(uow, order_id: int, *, fail: bool) -> None:
    """The transaction is the unit of work's; the repositories get its session."""
    async with uow.transaction() as tx:
        await OrderRepository(tx.session).add(order_id)
        await OutboxRepository(tx.session).add(order_id, fail=fail)


async def d_unit_of_work_with_savepoint(uow, order_id: int, *, fail: bool) -> None:
    """The order must be placed; the outbox row is allowed to fail and be recorded."""
    async with uow.transaction() as tx:
        await OrderRepository(tx.session).add(order_id)
        try:
            async with tx.savepoint():
                await OutboxRepository(tx.session).add(order_id, fail=fail)
        except RuntimeError as error:
            await tx.session.execute(
                text("INSERT INTO failures (order_id, reason) VALUES (:id, :reason)"),
                {"id": order_id, "reason": str(error)},
            )


async def part_atomicity(session_maker, uow) -> None:
    log("--- 1. the outbox row fails; what is left behind")
    designs = (
        ("a session per repository", lambda oid, fail: a_session_per_repository(session_maker, oid, fail=fail)),
        ("threaded, repository commits", lambda oid, fail: b_threaded_and_committed(session_maker, oid, fail=fail)),
        ("one unit of work", lambda oid, fail: c_unit_of_work(uow, oid, fail=fail)),
        ("unit of work with a savepoint", lambda oid, fail: d_unit_of_work_with_savepoint(uow, oid, fail=fail)),
    )
    for label, run in designs:
        await reset(session_maker)
        try:
            await run(1, True)
            raised = "no exception"
        except Exception as error:  # noqa: BLE001 - the lab reports whatever comes out
            raised = f"{type(error).__name__}"
        orders, outbox = await counts(session_maker)
        async with session_maker() as session:
            failures = await session.scalar(text("SELECT count(*) FROM failures"))
        log(f"    {label:<30} {raised:<16} orders={orders} outbox={outbox} failures={failures}")


# --- 2. what a session costs the pool ---------------------------------------------------------


async def part_pool(session_maker, uow) -> None:
    log(f"--- 2. the same designs against a pool of {POOL_SIZE} connections, 6 concurrent requests")

    async def one_request_two_sessions(order_id: int) -> None:
        # Two sessions held at once: the outer one is still open while the inner starts.
        async with session_maker() as outer:
            await OrderRepository(outer).add(order_id)
            async with session_maker() as inner:
                await OutboxRepository(inner).add(order_id, fail=False)
                await inner.commit()
            await outer.commit()

    async def one_request_one_session(order_id: int) -> None:
        async with uow.transaction() as tx:
            await OrderRepository(tx.session).add(order_id)
            await OutboxRepository(tx.session).add(order_id, fail=False)

    for label, run in (
        ("two sessions per request", one_request_two_sessions),
        ("one session per request", one_request_one_session),
    ):
        await reset(session_maker)
        started = time.perf_counter()
        results = await asyncio.gather(*(run(i) for i in range(1, 7)), return_exceptions=True)
        elapsed = time.perf_counter() - started
        failures = [type(r).__name__ for r in results if isinstance(r, BaseException)]
        orders, outbox = await counts(session_maker)
        log(f"    {label:<26} {elapsed:.2f} s, orders={orders} outbox={outbox}, "
            f"failures: {failures or 'none'}")


# --- 3. one session, two tasks ----------------------------------------------------------------


async def part_concurrency(uow) -> None:
    log("--- 3. sharing one session between two tasks")
    try:
        async with uow.transaction() as tx:
            await asyncio.gather(
                tx.session.execute(text("SELECT pg_sleep(0.2)")),
                tx.session.execute(text("SELECT pg_sleep(0.2)")),
            )
        result = "both statements ran"
    except Exception as error:  # noqa: BLE001 - the lab reports whatever comes out
        result = f"{type(error).__name__}: {str(error).splitlines()[0][:110]}"
    log(f"    asyncio.gather on one session: {result}")

    started = time.perf_counter()
    async def in_its_own_transaction() -> None:
        async with uow.transaction() as tx:
            await tx.session.execute(text("SELECT pg_sleep(0.2)"))

    await asyncio.gather(in_its_own_transaction(), in_its_own_transaction())
    log(f"    a transaction per task:        both ran in {time.perf_counter() - started:.2f} s")


# --- 4. what a repository can still do to the caller ------------------------------------------


async def part_lifetime(uow, session_maker) -> None:
    log("--- 4. what leaves the block")
    async with uow.transaction() as tx:
        await OrderRepository(tx.session).add(99)
        escaped = tx
    try:
        await escaped.session.execute(text("SELECT 1"))
        result = "the session still works"
    except Exception as error:  # noqa: BLE001
        result = f"{type(error).__name__}: {str(error).splitlines()[0][:90]}"
    log(f"    a transaction used after its block: {result}")
    log("      (and it holds a pooled connection until somebody closes it)")
    await escaped.session.close()

    async with uow.query() as qx:
        await qx.session.execute(text("INSERT INTO orders (id, state) VALUES (1000, 'placed')"))
    async with session_maker() as session:
        left = await session.scalar(text("SELECT count(*) FROM orders WHERE id = 1000"))
    log(f"    an INSERT issued inside query():    {left} rows survived")


async def main() -> None:
    log(f"sqlalchemy-foundation-kit {version('sqlalchemy-foundation-kit')}, "
        f"sqlalchemy {version('sqlalchemy')}, asyncpg {version('asyncpg')}")
    with PostgresContainer("postgres:17-alpine") as pg:
        dsn = pg.get_connection_url().replace("postgresql+psycopg2://", "postgresql+asyncpg://")
        manager = (
            AsyncSessionManagerBuilder(dsn)
            .with_pool("async_adapted_queue", Pool())
            .build()
        )
        session_maker = manager.session_maker
        async with session_maker() as session:
            await session.execute(text("CREATE TABLE orders (id BIGINT PRIMARY KEY, state TEXT NOT NULL)"))
            await session.execute(
                text("CREATE TABLE outbox (id BIGSERIAL PRIMARY KEY, order_id BIGINT NOT NULL, topic TEXT NOT NULL)")
            )
            await session.execute(
                text("CREATE TABLE failures (id BIGSERIAL PRIMARY KEY, order_id BIGINT NOT NULL, reason TEXT NOT NULL)")
            )
            await session.commit()

        uow = AsyncSQLAlchemyUnitOfWork(session_maker, transaction_factory=AsyncSQLAlchemyUowTransaction)
        try:
            await part_atomicity(session_maker, uow)
            await part_pool(session_maker, uow)
            await part_concurrency(uow)
            await part_lifetime(uow, session_maker)
        finally:
            await manager.aclose()


if __name__ == "__main__":
    asyncio.run(main())
