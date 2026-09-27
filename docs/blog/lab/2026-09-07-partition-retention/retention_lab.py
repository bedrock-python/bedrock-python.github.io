"""Real PostgreSQL checks: plans, FK protection, grace, verified archive and locks."""
import asyncio
from datetime import UTC, datetime, timedelta
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import asyncpg
from pg_partsmith import MaintenancePlan, OperationKind
from pg_partsmith.aio import BasePartitionLifecycleHooks, PartitionToolkit
from pg_partsmith.exceptions import PlanConfigMismatchError
from sqlalchemy.ext.asyncio import create_async_engine

from lab_support import database, expect_sqlstate, relations
from maintenance_flow import JsonArchive, apply_reviewed, events_config, maintenance_tick, preview

NOW = datetime(2026, 9, 15, tzinfo=UTC)


async def setup(connection):
    await connection.execute("""
        CREATE TABLE events (
            id bigint NOT NULL, created_at timestamptz NOT NULL, payload text NOT NULL,
            PRIMARY KEY (id, created_at)
        ) PARTITION BY RANGE (created_at);
        CREATE TABLE receipts (
            event_id bigint NOT NULL, event_at timestamptz NOT NULL,
            FOREIGN KEY (event_id, event_at) REFERENCES events (id, created_at)
        );
        CREATE TABLE events__2026_03 PARTITION OF events
            FOR VALUES FROM ('2026-02-01') TO ('2026-04-01');
        INSERT INTO events VALUES (31, '2026-03-12', 'irregular range');
        CREATE TABLE events__2025_01 (LIKE events INCLUDING ALL);
        INSERT INTO events__2025_01 VALUES (1, '2025-01-01', 'unmarked standalone table');
    """)
    for month in range(4, 10):
        name = "events_may_manual" if month == 5 else f"events__2026_{month:02}"
        await connection.execute(
            f"CREATE TABLE {name} PARTITION OF events "
            f"FOR VALUES FROM ('2026-{month:02}-01') TO ('2026-{month + 1:02}-01')"
        )
        await connection.executemany(
            "INSERT INTO events VALUES ($1, $2, $3)",
            [(month * 10 + n, datetime(2026, month, n, tzinfo=UTC), f"event-{month}-{n}") for n in (1, 2)],
        )
    await connection.execute("INSERT INTO receipts VALUES (51, '2026-05-01')")


class UnavailableArchive(BasePartitionLifecycleHooks):
    async def before_drop(self, event):
        raise RuntimeError("archive storage unavailable")


async def expect_runtime(awaitable, message):
    try:
        await awaitable
    except RuntimeError as error:
        assert message in str(error), error
    else:
        raise AssertionError(f"Expected failure: {message}")


async def main(engine_url, dsn, archive_directory):
    connection = await asyncpg.connect(dsn)
    engine = create_async_engine(engine_url)
    second_engine = create_async_engine(engine_url)
    toolkit = PartitionToolkit.from_engine(engine)
    config = events_config()
    try:
        await setup(connection)
        before = await relations(connection)
        plan = await preview(toolkit, config, now=NOW)
        assert await relations(connection) == before
        assert {op.target for op in plan.creates} == {"public.events__2026_10", "public.events__2026_11"}
        assert {op.target for op in plan.detaches} == {"public.events__2026_04", "public.events__2026_06"}
        assert not plan.drops
        assert any(f.partition_name == "public.events__2026_03" for f in plan.findings)
        assert all(op.target != "public.events__2025_01" for op in plan.operations)
        plan = MaintenancePlan.model_validate_json(plan.model_dump_json())
        try:
            await toolkit.service.apply(events_config(protect_references=False), plan)
        except PlanConfigMismatchError:
            pass
        else:
            raise AssertionError("A plan must not accept a different policy")
        assert await relations(connection) == before
        await expect_sqlstate(connection, "23514", "INSERT INTO events VALUES (100, '2026-10-01', 'future')")
        result = await apply_reviewed(toolkit, config, plan)
        assert (result.created_count, result.detached_count, result.dropped_count) == (2, 2, 0), result
        await connection.execute("INSERT INTO events VALUES (100, '2026-10-01', 'future')")
        assert await connection.fetchval("SELECT count(*) FROM events") == 10
        await expect_sqlstate(connection, "23514", "INSERT INTO events VALUES (999, '2026-04-10', 'late')")
        print("PASS plan: read-only, JSON round-trip, config drift refused; created October/November, detached April/June")

        # Bypass only the planning predicate: PostgreSQL still protects the referenced rows.
        plain = events_config(protect_references=False)
        refused_plan = await toolkit.service.plan(plain, now=NOW)
        assert {op.target for op in refused_plan.detaches} == {"public.events_may_manual"}
        refused = await toolkit.service.apply(plain, refused_plan)
        assert refused.success and refused.issues and refused.detached_count == 0, refused
        assert any(issue.partition_name == "public.events_may_manual" for issue in refused.issues)
        assert await connection.fetchval("SELECT count(*) FROM receipts") == 1
        print("PASS foreign key: success=True can include an issue; referenced May and its receipt survive")

        state = await relations(connection)
        second = PartitionToolkit.from_engine(second_engine)
        async with toolkit.locks.acquire_lock(config.qualified_name):
            await expect_runtime(maintenance_tick(second, config), "did not finish cleanly")
        assert await relations(connection) == state
        # A fresh attempt can acquire the same key after the first worker releases it.
        async with second.locks.acquire_lock(config.qualified_name):
            pass
        print("PASS scheduling: second toolkit on another engine cannot maintain the locked table; release permits retry")

        tree = await toolkit.service.inspect(config)
        assert len(tree.orphans) == 2 and all(orphan.detached_at for orphan in tree.orphans)
        earliest = min(orphan.detached_at for orphan in tree.orphans)
        latest = max(orphan.detached_at for orphan in tree.orphans)
        early = await toolkit.service.plan(config, now=earliest + timedelta(days=7) - timedelta(microseconds=1))
        assert not early.drops
        # Simulate a later planning instant; do not shorten the policy's seven-day grace.
        due = await toolkit.service.plan(config, now=latest + timedelta(days=7))
        due = due.only(OperationKind.DROP)
        assert len(due.drops) == 2
        originals = {}
        for op in due.drops:
            rows = await connection.fetch(f'SELECT id, created_at, payload FROM {op.target} ORDER BY id, created_at')
            originals[op.target] = [tuple(row) for row in rows]
        failing = PartitionToolkit.from_engine(engine, hooks=[UnavailableArchive()])
        await expect_runtime(failing.service.apply(config, due), "archive storage unavailable")
        assert all([await connection.fetchval("SELECT to_regclass($1) IS NOT NULL", op.target) for op in due.drops])

        archive = JsonArchive(connection, archive_directory)
        archiving = PartitionToolkit.from_engine(engine, hooks=[archive])
        corrupt = archive_directory / f"{due.drops[0].oid}.json"
        corrupt.write_text('{"rows": []}', encoding="utf-8")
        await expect_runtime(archiving.service.apply(config, due), "Archive verification failed")
        assert await connection.fetchval("SELECT to_regclass($1) IS NOT NULL", due.drops[0].target)
        corrupt.unlink()  # Lab fixture: an operator removes the deliberately invalid archive.
        deleted = await apply_reviewed(archiving, config, due)
        assert deleted.dropped_count == 2, deleted
        await connection.execute("CREATE TEMP TABLE restored (LIKE events INCLUDING ALL)")
        for op in due.drops:
            assert await connection.fetchval("SELECT to_regclass($1)", op.target) is None
            document = json.loads((archive_directory / f"{op.oid}.json").read_text(encoding="utf-8"))
            assert document["table"] == op.target
            rows = [(row[0], datetime.fromisoformat(row[1]), row[2]) for row in document["rows"]]
            assert rows == originals[op.target]
            await connection.executemany("INSERT INTO restored VALUES ($1, $2, $3)", rows)
        restored = await connection.fetch("SELECT id, created_at, payload FROM restored ORDER BY id, created_at")
        assert [tuple(row) for row in restored] == sorted(row for rows in originals.values() for row in rows)
        assert not (await toolkit.service.plan(config, now=latest + timedelta(days=7))).drops
        print("PASS archive: seven-day threshold, storage failure, corrupt archive refusal, retry and full restoration of four rows")

        await connection.execute("DELETE FROM receipts")
        released = await toolkit.service.plan(config, now=NOW)
        assert {op.target for op in released.detaches} == {"public.events_may_manual"}
        result = await apply_reviewed(toolkit, config, released)
        assert result.detached_count == 1 and result.dropped_count == 0
        assert await connection.fetchval("SELECT count(*) FROM events__2026_03") == 1
        assert await connection.fetchval("SELECT count(*) FROM events__2025_01") == 1
        print("PASS ownership: manual monthly partition becomes eligible after references disappear; irregular and unmarked tables survive")
    finally:
        await second_engine.dispose()
        await engine.dispose()
        await connection.close()


if __name__ == "__main__":
    with database() as (engine_url, dsn), TemporaryDirectory(prefix="partition-archive-") as directory:
        async def run():
            async with asyncio.timeout(120):
                await main(engine_url, dsn, Path(directory))
        asyncio.run(run())
