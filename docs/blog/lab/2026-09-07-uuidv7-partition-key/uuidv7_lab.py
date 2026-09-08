"""A table keyed by UUIDv7 and partitioned by that key, and the three ways it goes wrong.

PostgreSQL 17 in a container. `events` has one column in its primary key, `id UUID`, and is
RANGE-partitioned on it; the window boundaries are the smallest UUIDv7 of each month. The lab
prints the generated bounds, routes rows written now and two months ago, compares what the planner
prunes for an id range against a timestamp column, and then tries the three ids that do not fit:
one from before the oldest partition, one from beyond the newest, and one a client generated with
a skewed clock.
"""

from __future__ import annotations

import asyncio
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from importlib.metadata import version

import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer

from pg_partsmith import (
    CreateAhead,
    DropAfter,
    KeepNewest,
    LifecyclePolicy,
    PartitionGranularity,
    RangePartitioning,
    TablePartitionConfig,
    TimeBoundaries,
    UUIDv7BoundaryCodec,
)
from pg_partsmith.aio import PartitionToolkit


def log(msg: str) -> None:
    print(msg, flush=True)


def uuid7(at: datetime) -> uuid.UUID:
    """RFC 9562 UUIDv7: 48 bits of Unix milliseconds, then version, variant and randomness."""
    ms = int(at.timestamp() * 1000)
    raw = ms.to_bytes(6, "big") + secrets.token_bytes(10)
    as_int = int.from_bytes(raw, "big")
    as_int &= ~(0xF << 76)          # clear version nibble
    as_int |= 0x7 << 76             # version 7
    as_int &= ~(0x3 << 62)          # clear variant bits
    as_int |= 0x2 << 62             # variant 10
    return uuid.UUID(int=as_int)


def month_start(offset: int) -> datetime:
    now = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    year, month = divmod((now.year * 12 + now.month - 1) - offset, 12)
    return datetime(year, month + 1, 1, tzinfo=UTC)


CONFIG = TablePartitionConfig(
    schema="public",
    table_name="events",
    scheme=RangePartitioning(
        key="id",
        boundaries=TimeBoundaries(granularity=PartitionGranularity.MONTH, codec=UUIDv7BoundaryCodec()),
    ),
    lifecycle=LifecyclePolicy(
        creation=CreateAhead(count=1),      # this month and the next
        retention=KeepNewest(count=2),      # this month and the one before it
        drop=DropAfter(grace=timedelta(0)),
    ),
)


async def partitions(conn: asyncpg.Connection) -> list[tuple[str, str, int]]:
    rows = await conn.fetch(
        """
        SELECT c.relname, pg_get_expr(c.relpartbound, c.oid) AS bound
        FROM pg_inherits h JOIN pg_class c ON c.oid = h.inhrelid
        WHERE h.inhparent = 'public.events'::regclass ORDER BY c.relname
        """
    )
    out = []
    for row in rows:
        n = await conn.fetchval(f'SELECT count(*) FROM ONLY "{row["relname"]}"')
        out.append((row["relname"], row["bound"], n))
    return out


async def insert(conn: asyncpg.Connection, at: datetime, label: str) -> str:
    try:
        await conn.execute(
            "INSERT INTO events (id, created_at, payload) VALUES ($1, $2, $3)", uuid7(at), at, label
        )
        return "inserted"
    except asyncpg.PostgresError as error:
        return f"{type(error).__name__}: {str(error).splitlines()[0][:100]}"


async def plan_for(conn: asyncpg.Connection, sql: str, *args) -> str:
    rows = await conn.fetch(f"EXPLAIN (COSTS OFF) {sql}", *args)
    text = "\n".join(r["QUERY PLAN"] for r in rows)
    names = {line.split(" on ")[-1].split(" ")[0] for line in text.splitlines() if " on events" in line}
    scanned = sorted(n for n in names if not n.endswith("_pkey"))
    return f"{len(scanned)} partition(s): {', '.join(scanned) if scanned else 'none'}"


async def main() -> None:
    with PostgresContainer("postgres:17-alpine") as pg:
        dsn = pg.get_connection_url().replace("postgresql+psycopg2://", "postgresql://")
        conn = await asyncpg.connect(dsn)
        log(f"pg-partsmith {version('pg-partsmith')}, PostgreSQL {await conn.fetchval('SHOW server_version')}")

        log("--- 1. the table: one column in the primary key, and it is the partition key")
        await conn.execute(
            """
            CREATE TABLE events (
                id          UUID PRIMARY KEY,
                created_at  TIMESTAMPTZ NOT NULL,
                payload     TEXT NOT NULL
            ) PARTITION BY RANGE (id);
            """
        )
        log("    CREATE TABLE events (id UUID PRIMARY KEY, ...) PARTITION BY RANGE (id): accepted")
        try:
            await conn.execute(
                """
                CREATE TABLE by_time (
                    id UUID PRIMARY KEY,
                    created_at TIMESTAMPTZ NOT NULL
                ) PARTITION BY RANGE (created_at)
                """
            )
            log("    the same table partitioned by created_at with PRIMARY KEY (id): accepted")
        except asyncpg.PostgresError as error:
            log(f"    the same table partitioned by created_at with PRIMARY KEY (id): "
                f"{type(error).__name__}: {str(error).splitlines()[0][:90]}")

        engine = create_async_engine(dsn.replace("postgresql://", "postgresql+asyncpg://"))
        toolkit = PartitionToolkit.from_engine(engine)
        try:
            log("--- 2. the windows the codec computes")
            await toolkit.service.ensure_partitions(
                CONFIG, [month_start(2), month_start(1), month_start(0), month_start(-1)]
            )
            for name, bound, _ in await partitions(conn):
                log(f"    {name:<22} {bound}")

            log("--- 3. rows written now, and rows written two months ago")
            for offset, label in ((0, "this month"), (1, "last month"), (2, "two months ago")):
                at = month_start(offset) + timedelta(days=3)
                log(f"    an id generated {label:<15} -> {await insert(conn, at, label)}")
            for name, _, n in await partitions(conn):
                log(f"    {name:<22} {n} row(s)")

            log("--- 4. what the planner prunes")
            codec = UUIDv7BoundaryCodec()
            low, high = codec.encode(month_start(1), month_start(0))
            log("    WHERE id >= <first uuid7 of last month> AND id < <first uuid7 of this month>:")
            log(f"      {await plan_for(conn, 'SELECT * FROM events WHERE id >= $1::uuid AND id < $2::uuid', low, high)}")
            log("    WHERE created_at >= <last month> AND created_at < <this month>:")
            log(f"      {await plan_for(conn, 'SELECT * FROM events WHERE created_at >= $1 AND created_at < $2', month_start(1), month_start(0))}")
            log("    WHERE id = <one id>:")
            one = await conn.fetchval("SELECT id FROM events LIMIT 1")
            log(f"      {await plan_for(conn, 'SELECT * FROM events WHERE id = $1::uuid', one)}")

            log("--- 5. the ids that do not fit")
            log(f"    an id from a year ago (imported history): {await insert(conn, month_start(12), 'history')}")
            log(f"    an id from three months ahead (a clock that is wrong): "
                f"{await insert(conn, month_start(-3), 'skewed')}")
            log(f"    a uuid4 from a client that did not get the memo: "
                f"{await insert_uuid4(conn)}")

            log("--- 6. after the retention tick")
            result = await toolkit.maintainer.run_maintenance_safe(CONFIG)
            log(f"    created={result.created_count} detached={result.detached_count} "
                f"dropped={result.dropped_count} issues={len(result.issues)}")
            for name, _, n in await partitions(conn):
                log(f"    {name:<22} {n} row(s)")
            still_there = {name for name, _, _ in await partitions(conn)}
            retired = [offset for offset in (2, 3) if f"events__{month_start(offset):%Y_%m}" not in still_there]
            if retired:
                offset = retired[0]
                log(f"    an id for {month_start(offset):%Y-%m}, the month retention just retired: "
                    f"{await insert(conn, month_start(offset) + timedelta(days=3), 'late')}")
        finally:
            await engine.dispose()
            await conn.close()


async def insert_uuid4(conn: asyncpg.Connection) -> str:
    try:
        await conn.execute(
            "INSERT INTO events (id, created_at, payload) VALUES ($1, $2, $3)",
            uuid.uuid4(), datetime.now(UTC), "uuid4",
        )
        return "inserted"
    except asyncpg.PostgresError as error:
        return f"{type(error).__name__}: {str(error).splitlines()[0][:100]}"


if __name__ == "__main__":
    asyncio.run(main())
