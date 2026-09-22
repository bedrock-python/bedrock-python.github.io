"""Real PgBouncer checks: prepared statements, commits/rollbacks, and transaction-local state."""
import asyncio

import asyncpg
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy_foundation_kit import create_async_session_manager
from sqlalchemy_foundation_kit.contrib.settings import QuerySettings

from lab_support import DatabaseLab, seed
from pool_flow import effective_settings, get_order, slow_query_with_limit


async def workload(config, label):
    config = config.model_copy(update={"pool": config.pool.model_copy(update={"timeout": 3})})
    async with create_async_session_manager(config) as manager:
        async def worker(number):
            for repeat in range(2):
                for query in range(5):
                    async with manager.get_transaction() as session:
                        value = (await session.execute(
                            text(f"SELECT CAST(:value AS integer) + {query}"),
                            {"value": number},
                        )).scalar_one()
                        assert value == number + query
        async with asyncio.TaskGroup() as group:
            for number in range(4):
                group.create_task(worker(number))
        assert await get_order(manager, 42) == {"id": 42, "total": 1999}
        try:
            async with manager.get_transaction() as session:
                await session.execute(text("INSERT INTO orders VALUES (99, 500)"))
                raise RuntimeError("Roll back this order")
        except RuntimeError:
            pass
        async with manager.get_transaction() as session:
            assert (await session.execute(text("SELECT count(*) FROM orders WHERE id = 99"))).scalar_one() == 0
        assert (await effective_settings(manager))["search_path"] == "app"
    print(f"PASS {label}: 40 parameterized statements, lookup, rollback and schema")


async def prepared_switch(bouncer, tracked):
    a = await asyncpg.connect(bouncer.dsn, statement_cache_size=0)
    b = await asyncpg.connect(bouncer.dsn, statement_cache_size=0)
    try:
        async with a.transaction():
            first_pid = await a.fetchval("SELECT pg_backend_pid()")
            prepared = await a.prepare("SELECT $1::integer", name="order_lookup")
            assert await prepared.fetchval(42) == 42
        async with b.transaction():
            # With LIFO reuse, B takes the server A just released and keeps it busy.
            assert await b.fetchval("SELECT pg_backend_pid()") == first_pid
            try:
                async with a.transaction():
                    next_pid = await a.fetchval("SELECT pg_backend_pid()")
                    assert next_pid != first_pid
                    value = await prepared.fetchval(42)
            except asyncpg.InvalidSQLStatementNameError as error:
                assert not tracked and error.sqlstate == "26000"
            else:
                assert tracked and value == 42
    finally:
        await a.close()
        await b.close()
    print(f"PASS backend changed: tracked={tracked}, result={'42' if tracked else 'SQLSTATE 26000'}")


async def settings_and_timeout(bouncer):
    async with create_async_session_manager(bouncer.config()) as manager:
        before = await effective_settings(manager)
        assert before["search_path"] == "app"
        assert before["application_name"] == "orders-api"
        try:
            await slow_query_with_limit(manager)
        except DBAPIError as error:
            assert error.orig.sqlstate == "57014", error
        else:
            raise AssertionError("PostgreSQL should cancel pg_sleep under statement_timeout")
        assert await get_order(manager, 42) == {"id": 42, "total": 1999}
        async with manager.get_transaction() as session:
            assert (await session.execute(text("SHOW statement_timeout"))).scalar_one() == "0"
    raw = await asyncpg.connect(bouncer.dsn, statement_cache_size=0)
    try:
        async with raw.transaction():
            assert await raw.fetchval("SHOW search_path") != "app"
    finally:
        await raw.close()
    print("PASS SET LOCAL: schema does not leak; query cancellation rolls back; next transaction works")


async def main(lab, tracked, untracked):
    async with asyncio.timeout(45):
        async with create_async_session_manager(lab.direct_config()) as manager:
            await seed(manager)
        await workload(lab.direct_config(), "PostgreSQL directly, caches=100")
        await workload(tracked.config(), "PgBouncer tracking=200, caches=100")
        await prepared_switch(tracked, True)
        await prepared_switch(untracked, False)
        conservative = untracked.config().model_copy(update={
            "query": QuerySettings(statement_cache_size=0, prepared_statement_cache_size=0),
        })
        await workload(conservative, "PgBouncer tracking=0, kit unique names and caches=0")
        await settings_and_timeout(tracked)


if __name__ == "__main__":
    with DatabaseLab() as lab:
        tracked = lab.bouncer()
        untracked = lab.bouncer(max_prepared_statements=0)
        assert tracked.admin("SHOW VERSION")[0]["version"] == "PgBouncer 1.25.2"
        config = {row["key"]: row["value"] for row in tracked.admin("SHOW CONFIG")}
        assert config["pool_mode"] == "transaction" and config["max_prepared_statements"] == "200"
        asyncio.run(main(lab, tracked, untracked))
