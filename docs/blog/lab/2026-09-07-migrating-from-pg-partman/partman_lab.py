"""Verified handover from pg_partman 5.5.0, with no concurrent maintainers."""
import asyncio
from datetime import datetime
from pathlib import Path
import sys

import asyncpg
from pg_partsmith import CreateAhead
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
        assert len(before_off) >= 7, before_off  # pg_partman's exact future horizon can extend beyond premake.
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
        assert settings["retention"] == "3 months" and settings["retention_keep_table"]
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
        assert not plan.creates and not plan.drops
        assert len(plan.detaches) == 1
        assert plan.detaches[0].target.startswith("public.events_p")
        print("PASS adoption: existing names/bounds recognised; interval retention differs from KeepNewest(3); no writes during planning")

        # No background worker is installed; the lab owns all calls and has stopped calling pg_partman.
        await unregister_partman(connection)
        assert await connection.fetchval("SELECT count(*) FROM partman.part_config WHERE parent_table = 'public.events'") == 0
        result = await toolkit.service.apply(config, plan)
        assert not result.error and not result.issues and result.detached_count == 1 and result.dropped_count == 0, result
        remaining = {row["oid"] for row in await children(connection)}
        assert remaining == {row["oid"] for row in before_children} - {plan.detaches[0].oid}
        after_rows = await connection.fetch(
            f"SELECT * FROM events UNION ALL SELECT * FROM {plan.detaches[0].target} ORDER BY id"
        )
        assert after_rows == before_rows
        assert {row["oid"] for row in await relations(connection)} == {row["oid"] for row in snapshot}
        tree = await toolkit.service.inspect(config)
        assert len(tree.orphans) == 1 and tree.orphans[0].name == plan.detaches[0].target
        print("PASS handover: registration removed, old table OIDs and all data preserved, detached table kept by DropNever")

        next_start = max(datetime.fromisoformat(child.bounds.to_value) for child in tree.root.children if not child.is_default)
        horizon = (next_start.year - current.year) * 12 + next_start.month - current.month + 1
        wider = config.model_copy(update={"lifecycle": config.lifecycle.model_copy(update={"creation": CreateAhead(count=horizon)})})
        growth = await toolkit.service.plan(wider, now=current)
        assert len(growth.creates) == 1 and not growth.detaches and not growth.drops
        result = await toolkit.service.apply(wider, growth)
        assert result.created_count == 1 and not result.issues, result
        assert not (await toolkit.service.plan(wider, now=current)).operations
        assert await connection.fetchval("SELECT count(*) FROM events_default") == 0
        print("PASS new maintainer: one additional future month created, next plan is empty, DEFAULT is empty")
    finally:
        await engine.dispose()
        await connection.close()


if __name__ == "__main__":
    with database("pg-partman-lab:17") as (engine_url, dsn):
        async def run():
            async with asyncio.timeout(120):
                await main(engine_url, dsn)
        asyncio.run(run())
