"""Verified handover from pg_partman 5.5.0, with no concurrent maintainers."""
import asyncio
from datetime import datetime
from pathlib import Path
import sys

import asyncpg
from pg_partsmith.aio import PartitionToolkit
from sqlalchemy.ext.asyncio import create_async_engine

from adoption_flow import adopted_config, unregister_partman

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "2026-09-07-partition-retention"))
from lab_support import database, relations


def month_at(current, offset):
    year, month = divmod(current.year * 12 + current.month - 1 + offset, 12)
    return datetime(year, month + 1, 1, tzinfo=current.tzinfo)


async def children(connection):
    return await connection.fetch("""
        SELECT c.oid, c.relname, pg_get_expr(c.relpartbound, c.oid) AS bounds
        FROM pg_inherits i JOIN pg_class c ON c.oid = i.inhrelid
        WHERE i.inhparent = 'public.events'::regclass ORDER BY c.relname
    """)


async def main(engine_url, dsn):
    connection = await asyncpg.connect(dsn)
    engine = create_async_engine(engine_url)
    toolkit = PartitionToolkit.from_engine(engine)
    try:
        await connection.execute("CREATE SCHEMA partman; CREATE EXTENSION pg_partman WITH SCHEMA partman")
        version = await connection.fetchval("SELECT extversion FROM pg_extension WHERE extname = 'pg_partman'")
        assert version == "5.5.0", version
        current = await connection.fetchval("SELECT date_trunc('month', CURRENT_TIMESTAMP)")
        await connection.execute("""
            CREATE TABLE events (
                id bigint NOT NULL, created_at timestamptz NOT NULL, payload text NOT NULL,
                PRIMARY KEY (id, created_at)
            ) PARTITION BY RANGE (created_at)
        """)
        await connection.fetchval("""
            SELECT partman.create_partition(
                p_parent_table := 'public.events', p_control := 'created_at',
                p_interval := '1 month', p_premake := 2, p_start_partition := $1
            )
        """, month_at(current, -5).isoformat())
        await connection.executemany("INSERT INTO events VALUES ($1, $2, $3)", [
            (offset + 10, month_at(current, offset), f"event-{offset}") for offset in range(-5, 1)
        ])
        await connection.execute("""
            UPDATE partman.part_config
            SET retention = '3 months', retention_keep_table = true, infinite_time_partitions = true
            WHERE parent_table = 'public.events'
        """)
        await connection.execute("SELECT partman.run_maintenance('public.events')")
        before_off = await children(connection)
        assert len(before_off) == 7, before_off  # Current month, three before it, two ahead, DEFAULT.
        await connection.execute("""
            UPDATE partman.part_config SET automatic_maintenance = 'off', premake = 3
            WHERE parent_table = 'public.events'
        """)
        await connection.execute("SELECT partman.run_maintenance()")
        assert await children(connection) == before_off
        # Still before handover: a targeted call ignores automatic_maintenance='off'.
        await connection.execute("SELECT partman.run_maintenance('public.events')")
        assert len(await children(connection)) == len(before_off) + 1
        print("PASS pg_partman 5.5.0: automatic_maintenance=off skips general maintenance but not a targeted call")

        settings = dict(await connection.fetchrow("SELECT * FROM partman.part_config WHERE parent_table = 'public.events'"))
        assert settings["control"] == "created_at" and settings["partition_interval"] == "1 mon"
        assert settings["premake"] == 3 and settings["retention"] == "3 months" and settings["retention_keep_table"]
        config = adopted_config(settings)
        snapshot = await relations(connection)
        before_children = await children(connection)
        before_rows = await connection.fetch("SELECT * FROM events ORDER BY id")
        inspected = await toolkit.service.inspect(config)
        assert len(inspected.root.children) == len(before_children)
        assert not inspected.orphans  # pg_partman's detached tables have no pg-partsmith marker.
        plan = await toolkit.service.plan(config, now=current)
        print(plan.describe())
        assert await relations(connection) == snapshot
        assert not plan.operations, plan.describe()
        print("PASS adoption: CreateAhead(premake + 1) and KeepNewest(4) match pg_partman's set; the first plan is empty")

        # No background worker is installed; the lab owns all calls and has stopped calling pg_partman.
        await unregister_partman(connection)
        assert await connection.fetchval("SELECT count(*) FROM partman.part_config WHERE parent_table = 'public.events'") == 0
        await connection.execute("SELECT partman.run_maintenance('public.events')")
        assert await children(connection) == before_children
        print("PASS handover: after unregistering, even a targeted pg_partman call changes nothing")

        next_month = month_at(current, 1)
        step = await toolkit.service.plan(config, now=next_month)
        print(step.describe())
        assert len(step.creates) == 1 and len(step.detaches) == 1 and not step.drops
        detached = step.detaches[0]
        assert detached.target.startswith("public.events_p")
        result = await toolkit.service.apply(config, step)
        assert not result.error and not result.issues and result.dropped_count == 0, result
        remaining = {row["oid"] for row in await children(connection)}
        assert {row["oid"] for row in before_children} - {detached.oid} <= remaining
        after_rows = await connection.fetch(f"SELECT * FROM events UNION ALL SELECT * FROM {detached.target} ORDER BY id")
        assert after_rows == before_rows
        assert not (await toolkit.service.plan(config, now=next_month)).operations
        assert await connection.fetchval("SELECT count(*) FROM events_default") == 0
        print("PASS next month: one partition created, the oldest detached and kept; old OIDs and all rows preserved")
    finally:
        await engine.dispose()
        await connection.close()


if __name__ == "__main__":
    with database("pg-partman-lab:17") as (engine_url, dsn):
        async def run():
            async with asyncio.timeout(120):
                await main(engine_url, dsn)
        asyncio.run(run())
