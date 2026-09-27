"""Reproduce the exact-batch boundary in pg-partsmith 1.5.1 and verify explicit final attachment."""
import asyncio
from datetime import UTC, datetime

import asyncpg
from pg_partsmith import PartitionGranularity, TablePartitionConfig
from pg_partsmith.aio import PartitionToolkit
from sqlalchemy.ext.asyncio import create_async_engine

from lab_support import database
from migration_flow import finish_ranges, move_batch


async def main(engine_url, dsn):
    connection = await asyncpg.connect(dsn)
    engine = create_async_engine(engine_url)
    try:
        async with asyncio.timeout(60):
            await connection.execute("""
                CREATE TABLE boundary_events (id integer, created_at timestamptz)
                    PARTITION BY RANGE (created_at);
                CREATE TABLE boundary_default PARTITION OF boundary_events DEFAULT;
                INSERT INTO boundary_events
                    SELECT generate_series(1, 100), '2026-07-01'::timestamptz;
            """)
            config = TablePartitionConfig(schema="public", table_name="boundary_events",
                partition_column="created_at", granularity=PartitionGranularity.MONTH)
            toolkit = PartitionToolkit.from_engine(engine)
            before = await connection.fetch("SELECT * FROM boundary_events ORDER BY id")
            first = await move_batch(toolkit, config, max_batches=1)
            assert first.rows_moved == 100 and not first.complete
            second = await move_batch(toolkit, config, max_batches=1)
            assert second.complete and second.rows_moved == 0
            assert await connection.fetchval("SELECT count(*) FROM boundary_events") == 0
            assert await connection.fetchval("SELECT count(*) FROM boundary_events__2026_07") == 100
            print("PASS reproduced 1.5.1 boundary: complete=True, parent=0, unattached table=100", flush=True)
            await finish_ranges(toolkit, config, [datetime(2026, 7, 1, tzinfo=UTC)])
            assert await connection.fetch("SELECT * FROM boundary_events ORDER BY id") == before
            assert await connection.fetchval("SELECT EXISTS (SELECT FROM pg_inherits WHERE inhparent='boundary_events'::regclass AND inhrelid='boundary_events__2026_07'::regclass)")
            print("PASS recovery: ensure_partitions attached the expected month; all 100 rows are visible", flush=True)
    finally:
        await engine.dispose()
        await connection.close()


if __name__ == "__main__":
    with database() as (engine_url, dsn):
        asyncio.run(main(engine_url, dsn))
