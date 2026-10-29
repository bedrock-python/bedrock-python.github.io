"""Verify UUIDv7 routing, pruning and invalid-id behavior on PostgreSQL 17."""
import asyncio
from datetime import UTC, datetime, timedelta
from pathlib import Path
import secrets
import sys
import uuid

import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine
from pg_partsmith import UUIDv7BoundaryCodec
from pg_partsmith.aio import PartitionToolkit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "2026-09-07-partition-existing-table"))
from lab_support import database, expect_sqlstate, scanned_relations
from uuid_flow import CONFIG, august_events


def sample_uuid7(at):
    # Test fixture only: construct RFC 9562 version/variant bits for a specified instant.
    value = (int(at.timestamp() * 1000) << 80) | secrets.randbits(80)
    value = (value & ~(0xF << 76)) | (7 << 76)
    value = (value & ~(3 << 62)) | (2 << 62)
    result = uuid.UUID(int=value)
    assert result.version == 7 and result.variant == uuid.RFC_4122
    return result


async def main(engine_url, dsn):
    connection = await asyncpg.connect(dsn)
    engine = create_async_engine(engine_url)
    try:
        async with asyncio.timeout(60):
            await connection.execute("CREATE TABLE uuid_events (id uuid PRIMARY KEY, created_at timestamptz NOT NULL, payload text NOT NULL) PARTITION BY RANGE (id)")
            toolkit = PartitionToolkit.from_engine(engine)
            months = [datetime(2026, month, 1, tzinfo=UTC) for month in (7, 8, 9, 10)]
            await toolkit.service.ensure_partitions(CONFIG, months)
            insert = "INSERT INTO uuid_events VALUES ($1, $2, $3)"
            for month in months:
                instant = month + timedelta(days=3)
                await connection.execute(insert, sample_uuid7(instant), instant, month.strftime("%Y-%m"))
            assert [row["payload"] for row in await august_events(connection)] == ["2026-08"]
            codec = UUIDv7BoundaryCodec()
            lower, upper = codec.encode(months[1], months[2])
            assert upper == codec.encode(months[2], months[3])[0]
            await connection.execute(insert, uuid.UUID(upper), months[2], "September boundary")
            assert await connection.fetchval("SELECT tableoid::regclass::text FROM uuid_events WHERE id=$1", uuid.UUID(upper)) == "uuid_events__2026_09"
            by_id = await scanned_relations(connection, "SELECT * FROM uuid_events WHERE id >= $1::uuid AND id < $2::uuid", lower, upper)
            by_time = await scanned_relations(connection, "SELECT * FROM uuid_events WHERE created_at >= $1 AND created_at < $2", months[1], months[2])
            assert by_id == {"uuid_events__2026_08"} and len(by_time) == 4
            print("PASS UUIDv7: one-column primary key; adjacent bounds; August id range scans one partition, timestamp range scans four", flush=True)

            for instant in (datetime(2025, 1, 1, tzinfo=UTC), datetime(2027, 1, 1, tzinfo=UTC)):
                await expect_sqlstate(connection, "23514", insert, sample_uuid7(instant), instant, "outside prepared range")
            # Range partitioning orders UUID bytes. It does not validate the UUID version.
            good = sample_uuid7(months[1] + timedelta(days=7))
            wrong_version = uuid.UUID(int=(good.int & ~(0xF << 76)) | (4 << 76))
            assert wrong_version.version == 4
            await connection.execute(insert, wrong_version, months[1], "wrong UUID version")
            assert await connection.fetchval("SELECT tableoid::regclass::text FROM uuid_events WHERE id=$1", wrong_version) == "uuid_events__2026_08"
            await connection.execute("DELETE FROM uuid_events WHERE id=$1", wrong_version)
            await connection.execute("ALTER TABLE uuid_events ADD CONSTRAINT uuid_events_v7 CHECK ((get_byte(uuid_send(id), 6) >> 4) = 7)")
            await expect_sqlstate(connection, "23514", insert, wrong_version, months[1], "rejected by CHECK")
            print("PASS mixed IDs: a crafted UUIDv4 fits the range; explicit version CHECK rejects it; old/future IDs lack a partition", flush=True)

            imported = sample_uuid7(months[2] + timedelta(days=7))
            await connection.execute(insert, imported, datetime(2020, 1, 1, tzinfo=UTC), "imported event")
            assert await connection.fetchval("SELECT tableoid::regclass::text FROM uuid_events WHERE id=$1", imported) == "uuid_events__2026_09"
            await connection.execute("ALTER TABLE uuid_events DETACH PARTITION uuid_events__2026_07")
            await expect_sqlstate(connection, "23514", insert, sample_uuid7(months[0] + timedelta(days=7)), months[0], "late July event")
            print("PASS event time differs from ID time; a late July row is refused after July is detached", flush=True)
    finally:
        await engine.dispose()
        await connection.close()


if __name__ == "__main__":
    with database() as (engine_url, dsn):
        asyncio.run(main(engine_url, dsn))
