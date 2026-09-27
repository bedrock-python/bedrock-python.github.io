"""Rehearse a maintenance-window migration and verify each failure mode on PostgreSQL."""
import asyncio
from datetime import UTC, datetime, timedelta
from pathlib import Path

import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine

from lab_support import database, expect_sqlstate, scanned_relations
from migration_flow import (
    cutover, finish_ranges, migration_toolkit, move_batch, prepare_keys, prepare_next_month,
    remove_empty_default, restore_references,
)

ROWS = 615
INSERT = "INSERT INTO events (created_at, kind, payload) VALUES ($1, 'live', $2) RETURNING id"


async def main(engine_url, dsn):
    connection = await asyncpg.connect(dsn)
    engine = create_async_engine(engine_url)
    try:
        async with asyncio.timeout(90):
            await connection.execute(Path(__file__).with_name("schema.sql").read_text(encoding="utf-8"))
            await connection.executemany(
                "INSERT INTO events (created_at, kind, payload) VALUES ($1, 'history', $2)",
                [(datetime(2026, month, 1, tzinfo=UTC) + timedelta(minutes=i), f"event-{month}-{i}")
                 for month in (7, 8, 9) for i in range(205)],
            )
            await connection.execute("INSERT INTO event_notes (event_id, note) SELECT id, 'review' FROM events WHERE id <= 20")
            notes = await connection.fetch("SELECT id, event_id, note FROM event_notes ORDER BY id")
            await connection.execute("SET ROLE events_app")
            before_id = await connection.fetchval(INSERT, datetime(2026, 9, 15, tzinfo=UTC), "before cutover")
            await connection.execute("RESET ROLE")
            before = await connection.fetch("SELECT * FROM events ORDER BY id, created_at")
            assert len(before) == ROWS + 1

            await expect_sqlstate(connection, "0A000", "CREATE TABLE invalid_events (LIKE events INCLUDING ALL) PARTITION BY RANGE (created_at)")
            await expect_sqlstate(connection, "2BP01", "ALTER TABLE events DROP CONSTRAINT events_pkey")
            print("PASS keys: timestamp partitioning needs a composite key; incoming FK prevents dropping the old PK", flush=True)
            await prepare_keys(connection)

            # Hold a real read transaction so the cutover must time out instead of waiting indefinitely.
            blocker = await asyncpg.connect(dsn)
            try:
                async with blocker.transaction():
                    await blocker.fetchval("SELECT id FROM events LIMIT 1")
                    try:
                        await cutover(connection)
                    except asyncpg.LockNotAvailableError as error:
                        assert error.sqlstate == "55P03"
                    else:
                        raise AssertionError("Cutover should time out behind the reader")
                assert await connection.fetchval("SELECT to_regclass('events_legacy')") is None
                assert await connection.fetchval("SELECT count(*) FROM pg_constraint WHERE conname='event_notes_event_id_fkey'") == 1
                assert await connection.fetch("SELECT * FROM events ORDER BY id, created_at") == before
            finally:
                await blocker.close()
            print("PASS cutover lock timeout: rollback preserved the original table, rows and foreign key", flush=True)

            await cutover(connection)
            assert await connection.fetch("SELECT * FROM events ORDER BY id, created_at") == before
            await connection.execute("SET ROLE events_app")
            try:
                await expect_sqlstate(connection, "42501", "SELECT * FROM events")
            finally:
                await connection.execute("RESET ROLE")
            await expect_sqlstate(connection, "23514", "CREATE TABLE premature PARTITION OF events FOR VALUES FROM ('2026-07-01') TO ('2026-08-01')")
            print("PASS cutover: old rows are in DEFAULT; new parent needs grants; overlapping range is refused", flush=True)

            toolkit, config = migration_toolkit(engine)
            result = await move_batch(toolkit, config, max_batches=1)
            assert result.rows_moved == 100 and result.batches == 1 and not result.complete
            visible = await connection.fetchval("SELECT count(*) FROM events")
            staged = await connection.fetchval("SELECT count(*) FROM events__2026_07")
            assert visible == len(before) - 100 and staged == 100
            assert not await connection.fetchval("SELECT EXISTS (SELECT FROM pg_inherits WHERE inhrelid='events__2026_07'::regclass)")
            assert await connection.fetch("SELECT * FROM events UNION ALL SELECT * FROM events__2026_07 ORDER BY id, created_at") == before
            print(f"PASS partial batch: parent sees {visible}, detached July table holds {staged}; combined rows match exactly", flush=True)

            # A new engine/toolkit proves resumption uses committed database state.
            await engine.dispose()
            toolkit, config = migration_toolkit(engine)
            expected_months = [datetime(2026, month, 1, tzinfo=UTC) for month in (7, 8, 9)]
            resumed = await finish_ranges(toolkit, config, expected_months)
            assert resumed.complete and resumed.rows_moved == len(before) - 100
            assert await connection.fetch("SELECT * FROM events ORDER BY id, created_at") == before
            assert await connection.fetchval("SELECT total FROM event_summary") == 0
            await expect_sqlstate(connection, "42830", "ALTER TABLE event_notes ADD FOREIGN KEY (event_id) REFERENCES events (id)")
            print("PASS resume: all rows restored to the parent; old view still points to the now-empty legacy table", flush=True)

            await restore_references(connection)
            assert await connection.fetchval("SELECT total FROM event_summary") == len(before)
            assert await connection.fetchval("SELECT convalidated FROM pg_constraint WHERE conname='event_notes_event_fkey'")
            assert await connection.fetch("SELECT id, event_id, note FROM event_notes ORDER BY id") == notes
            await expect_sqlstate(connection, "23502", "INSERT INTO event_notes (event_id, note) VALUES (1, 'missing time')")
            await expect_sqlstate(connection, "23503", "INSERT INTO event_notes (event_id, event_created_at, note) VALUES (1, '2026-08-01', 'wrong time')")
            await prepare_next_month(toolkit, config)
            await remove_empty_default(connection)
            assert await connection.fetchval("SELECT to_regclass('events_legacy')") is None
            await connection.execute("SET ROLE events_app")
            try:
                after_id = await connection.fetchval(INSERT, datetime(2026, 9, 16, tzinfo=UTC), "after cutover")
            finally:
                await connection.execute("RESET ROLE")
            assert after_id > before_id
            assert await connection.fetchval("SELECT count(*) FROM events") == len(before) + 1
            assert await connection.fetchval("SELECT total FROM event_summary") == len(before) + 1
            print("PASS final constraints, grants, view and sequence: same application INSERT works after DEFAULT is dropped", flush=True)

            start, end = datetime(2026, 7, 1, tzinfo=UTC), datetime(2026, 8, 1, tzinfo=UTC)
            assert await scanned_relations(connection, "SELECT * FROM events WHERE created_at >= $1 AND created_at < $2", start, end) == {"events__2026_07"}
            await expect_sqlstate(connection, "23514", "INSERT INTO events (created_at, kind, payload) VALUES ('2025-01-01', 'late', 'no partition')")
            await expect_sqlstate(connection, "23505", "INSERT INTO events (id, created_at, kind, payload) VALUES (1, '2026-07-01', 'duplicate', 'same key')")
            # Composite uniqueness is weaker than uniqueness of id alone.
            transaction = connection.transaction()
            await transaction.start()
            try:
                await connection.execute("INSERT INTO events (id, created_at, kind, payload) VALUES (1, '2026-08-01', 'duplicate-id', 'allowed')")
                assert await connection.fetchval("SELECT count(*) FROM events WHERE id=1") == 2
            finally:
                await transaction.rollback()
            print("PASS query pruning and out-of-range rejection; composite PK allows the same id at another timestamp", flush=True)
    finally:
        await engine.dispose()
        await connection.close()


if __name__ == "__main__":
    with database() as (engine_url, dsn):
        asyncio.run(main(engine_url, dsn))
