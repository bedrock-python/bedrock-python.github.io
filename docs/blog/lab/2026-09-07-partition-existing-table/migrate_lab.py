"""Partition a live table, step by step, with a writer and a reader hitting it the whole time.

Starts PostgreSQL 17 in a container, fills a plain ``events`` table with ROWS rows spread over
the last year plus an ``event_notes`` table that references it, then walks the migration:

1. the primary key has to include the partition column (and the foreign key is in the way);
2. the swap: rename, create the partitioned parent, attach the old table as DEFAULT;
3. the first maintenance tick, which creates this month and moves this month's rows;
4. the drain, ``partition_data`` in batches, oldest month first;
5. the foreign key comes back, composite;
6. the empty DEFAULT is detached and dropped.

A writer inserts through ``events`` every few milliseconds with one statement that never
changes, and a reader counts the oldest month through ``events`` every few milliseconds.
Every step prints how long it took, and what the writer and the reader saw while it ran.
"""

from __future__ import annotations

import asyncio
import contextlib
import statistics
import sys
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from importlib.metadata import version

import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine
try:
    from testcontainers.community.postgres import PostgresContainer
except ImportError:  # testcontainers < 4.15
    from testcontainers.postgres import PostgresContainer

from pg_partsmith import PartitionGranularity, TablePartitionConfig
from pg_partsmith.aio import PartitionToolkit

ROWS = 2_000_000
NOTES = 50_000
BATCH_ROWS = 50_000
STALL_MS = 100.0


def log(msg: str) -> None:
    print(msg, flush=True)


@dataclass
class PhaseStats:
    name: str
    inserts: list[float] = field(default_factory=list)
    reads: list[float] = field(default_factory=list)
    visible: list[int] = field(default_factory=list)
    writer_errors: list[str] = field(default_factory=list)

    def report(self, full_window: int) -> None:
        if self.inserts:
            p50 = statistics.median(self.inserts)
            worst = max(self.inserts)
            stalls = sum(1 for x in self.inserts if x > STALL_MS)
            log(
                f"    writer: {len(self.inserts)} inserts, p50 {p50:.1f} ms, "
                f"longest {worst:.0f} ms, {stalls} over {STALL_MS:.0f} ms"
                + (f", {len(self.writer_errors)} errors: {self.writer_errors[0]}" if self.writer_errors else "")
            )
        if self.reads:
            low = min(self.visible)
            below = sum(1 for v in self.visible if v < full_window)
            log(
                f"    reader: {len(self.reads)} counts of the oldest month, longest {max(self.reads):.0f} ms, "
                f"lowest count {low} of {full_window}"
                + (f", below full in {below} of {len(self.visible)} samples" if below else ", never below full")
            )


class Load:
    """A writer and a reader that never stop, and per-phase statistics."""

    def __init__(self, dsn: str, window: tuple[datetime, datetime]) -> None:
        self.dsn = dsn
        self.window = window
        self.phase: PhaseStats | None = None
        self.inserted = 0
        self.full_window = 0
        self._tasks: list[asyncio.Task[None]] = []

    async def start(self) -> None:
        self._w = await asyncpg.connect(self.dsn)
        self._r = await asyncpg.connect(self.dsn)
        self.full_window = await self._count()
        self._tasks = [asyncio.create_task(self._writer()), asyncio.create_task(self._reader())]

    async def stop(self) -> None:
        for t in self._tasks:
            t.cancel()
        for t in self._tasks:
            with contextlib.suppress(asyncio.CancelledError):
                await t
        await self._w.close()
        await self._r.close()

    async def _count(self) -> int:
        return await self._r.fetchval(
            "SELECT count(*) FROM events WHERE created_at >= $1 AND created_at < $2", *self.window
        )

    async def _writer(self) -> None:
        sql = "INSERT INTO events (created_at, kind, payload) VALUES (now(), 'live', $1)"
        while True:
            t0 = time.perf_counter()
            try:
                await self._w.execute(sql, f"live row {self.inserted}")
                self.inserted += 1
                if self.phase:
                    self.phase.inserts.append((time.perf_counter() - t0) * 1000)
            except asyncpg.PostgresError as exc:
                if self.phase:
                    self.phase.writer_errors.append(f"{type(exc).__name__}: {exc}")
            await asyncio.sleep(0.005)

    async def _reader(self) -> None:
        while True:
            t0 = time.perf_counter()
            n = await self._count()
            if self.phase:
                self.phase.reads.append((time.perf_counter() - t0) * 1000)
                self.phase.visible.append(n)
            await asyncio.sleep(0.02)

    @contextlib.asynccontextmanager
    async def measure(self, name: str) -> AsyncIterator[PhaseStats]:
        log(f"--- {name}")
        self.phase = PhaseStats(name)
        t0 = time.perf_counter()
        try:
            yield self.phase
        finally:
            elapsed = time.perf_counter() - t0
            phase, self.phase = self.phase, None
            log(f"    step took {elapsed:.2f} s")
            phase.report(self.full_window)


async def timed(conn: asyncpg.Connection, label: str, sql: str) -> float:
    t0 = time.perf_counter()
    await conn.execute(sql)
    ms = (time.perf_counter() - t0) * 1000
    log(f"    {label}: {ms:.0f} ms")
    return ms


async def expect_error(conn: asyncpg.Connection, label: str, sql: str) -> None:
    try:
        await conn.execute(sql)
    except asyncpg.PostgresError as exc:
        detail = f" ({exc.detail})" if getattr(exc, "detail", None) else ""
        log(f"    {label}: {type(exc).__name__}: {exc}{detail}")
    else:
        log(f"    {label}: unexpectedly succeeded")


async def tree(conn: asyncpg.Connection) -> None:
    rows = await conn.fetch(
        """
        SELECT c.relname, pg_get_expr(c.relpartbound, c.oid) AS bound,
               (SELECT count(*) FROM pg_index i WHERE i.indrelid = c.oid) AS indexes
        FROM pg_inherits h JOIN pg_class c ON c.oid = h.inhrelid
        WHERE h.inhparent = 'public.events'::regclass
        ORDER BY c.relname
        """
    )
    for r in rows:
        n = await conn.fetchval(f'SELECT count(*) FROM ONLY "{r["relname"]}"')
        log(f"    {r['relname']:<22} {n:>9} rows  {r['indexes']} indexes  {r['bound']}")


async def main() -> None:
    with PostgresContainer("postgres:17-alpine") as pg:
        dsn = pg.get_connection_url().replace("postgresql+psycopg2://", "postgresql://")
        admin = await asyncpg.connect(dsn)
        log(
            f"pg-partsmith {version('pg-partsmith')}, sqlalchemy {version('sqlalchemy')}, "
            f"asyncpg {version('asyncpg')}, PostgreSQL {await admin.fetchval('SHOW server_version')}"
        )

        log(f"--- setup: {ROWS:,} events over the last year, {NOTES:,} notes referencing them")
        await admin.execute(
            """
            CREATE TABLE events (
                id          BIGSERIAL PRIMARY KEY,
                created_at  TIMESTAMPTZ NOT NULL,
                kind        TEXT NOT NULL,
                payload     TEXT NOT NULL
            );
            CREATE INDEX events_created_at_idx ON events (created_at);
            CREATE TABLE event_notes (
                id        BIGSERIAL PRIMARY KEY,
                event_id  BIGINT NOT NULL REFERENCES events (id),
                note      TEXT NOT NULL
            );
            CREATE INDEX event_notes_event_id_idx ON event_notes (event_id);
            """
        )
        t0 = time.perf_counter()
        await admin.execute(
            f"""
            INSERT INTO events (created_at, kind, payload)
            SELECT now() - interval '365 days' * random(),
                   (ARRAY['click', 'view', 'buy'])[1 + floor(random() * 3)::int],
                   md5(g::text)
            FROM generate_series(1, {ROWS}) g;
            INSERT INTO event_notes (event_id, note)
            SELECT 1 + floor(random() * {ROWS})::bigint, 'note ' || g FROM generate_series(1, {NOTES}) g;
            """
        )
        await admin.execute("VACUUM ANALYZE events")
        size = await admin.fetchval("SELECT pg_size_pretty(pg_total_relation_size('events'))")
        log(f"    loaded in {time.perf_counter() - t0:.1f} s, events is {size} with indexes")

        oldest = await admin.fetchval("SELECT date_trunc('month', min(created_at)) FROM events")
        window = (oldest, datetime(oldest.year + (oldest.month == 12), oldest.month % 12 + 1, 1, tzinfo=UTC))
        load = Load(dsn, window)
        await load.start()
        log(f"    writer and reader running; the oldest month is {oldest:%Y-%m} with {load.full_window} rows")

        # 1. The key.
        async with load.measure("1a. a partitioned copy with the old primary key"):
            await expect_error(
                admin,
                "CREATE TABLE ... (LIKE events INCLUDING ALL) PARTITION BY RANGE (created_at)",
                "CREATE TABLE events_p (LIKE events INCLUDING ALL) PARTITION BY RANGE (created_at)",
            )
        async with load.measure("1b. change the key on the live table: the foreign key is in the way"):
            await expect_error(
                admin,
                "ALTER TABLE events DROP CONSTRAINT events_pkey",
                "ALTER TABLE events DROP CONSTRAINT events_pkey",
            )
        async with load.measure("1c. ALTER TABLE ... ADD PRIMARY KEY (id, created_at) in one statement"):
            await timed(admin, "DROP the foreign key", "ALTER TABLE event_notes DROP CONSTRAINT event_notes_event_id_fkey")
            await timed(
                admin,
                "DROP CONSTRAINT, ADD PRIMARY KEY (id, created_at)",
                "ALTER TABLE events DROP CONSTRAINT events_pkey, ADD PRIMARY KEY (id, created_at)",
            )
        # Put the old key back, so the concurrent route starts from the same place.
        await admin.execute("ALTER TABLE events DROP CONSTRAINT events_pkey, ADD PRIMARY KEY (id)")
        async with load.measure("1d. the same key change with CREATE UNIQUE INDEX CONCURRENTLY first"):
            await timed(
                admin,
                "CREATE UNIQUE INDEX CONCURRENTLY events_id_created_at_key ON events (id, created_at)",
                "CREATE UNIQUE INDEX CONCURRENTLY events_id_created_at_key ON events (id, created_at)",
            )
            await timed(
                admin,
                "DROP CONSTRAINT, ADD PRIMARY KEY USING INDEX",
                """
                BEGIN;
                SET LOCAL lock_timeout = '2s';
                ALTER TABLE events DROP CONSTRAINT events_pkey,
                                   ADD CONSTRAINT events_pkey PRIMARY KEY USING INDEX events_id_created_at_key;
                COMMIT;
                """,
            )

        # 2. The swap.
        async with load.measure("2. the swap: rename, create the parent, attach the old table as DEFAULT"):
            await timed(
                admin,
                "one transaction",
                """
                BEGIN;
                SET LOCAL lock_timeout = '2s';
                ALTER TABLE events RENAME TO events_legacy;
                ALTER INDEX events_created_at_idx RENAME TO events_legacy_created_at_idx;
                ALTER TABLE events_legacy RENAME CONSTRAINT events_pkey TO events_legacy_pkey;
                CREATE TABLE events (LIKE events_legacy INCLUDING ALL) PARTITION BY RANGE (created_at);
                ALTER TABLE events ATTACH PARTITION events_legacy DEFAULT;
                COMMIT;
                """,
            )
            in_legacy = await admin.fetchval("SELECT count(*) FROM ONLY events_legacy WHERE kind = 'live'")
            log(f"    live rows written so far: {load.inserted}, in the DEFAULT partition: {in_legacy}")

        # 3. The first tick.
        engine = create_async_engine(dsn.replace("postgresql://", "postgresql+asyncpg://"))
        toolkit = PartitionToolkit.from_engine(engine)
        config = TablePartitionConfig(
            schema="public",
            table_name="events",
            partition_column="created_at",
            granularity=PartitionGranularity.MONTH,
            create_ahead_count=3,
            retention_count=24,
        )
        plan = await toolkit.service.plan(config)
        log("--- 3. the plan for the first tick")
        for line in plan.describe().splitlines():
            log(f"    {line}")
        async with load.measure("3. the first tick: this month and two ahead, this month's rows move out of DEFAULT"):
            result = await toolkit.maintainer.run_maintenance_safe(config)
            log(
                f"    created {result.created_count}, issues {len(result.issues)}, error {result.error!r}, "
                f"{result.duration_ms:.0f} ms"
            )
            this_month = await admin.fetchval(
                f"SELECT count(*) FROM ONLY events__{datetime.now(UTC):%Y_%m} WHERE kind = 'live'"
            )
            in_legacy = await admin.fetchval("SELECT count(*) FROM ONLY events_legacy WHERE kind = 'live'")
            log(f"    live rows: {this_month} in this month's partition, {in_legacy} left in DEFAULT")

        # 4. The drain.
        async with load.measure(f"4. the drain: partition_data in batches of {BATCH_ROWS:,}, oldest month first") as st:
            calls = 0
            moved = 0
            batches = 0
            partitions: list[str] = []
            t0 = time.perf_counter()
            while True:
                r = await toolkit.service.partition_data(config, batch_rows=BATCH_ROWS, max_batches=10)
                calls += 1
                moved += r.rows_moved
                batches += r.batches
                partitions += [p for p in r.partitions if p not in partitions]
                for issue in r.issues:
                    log(f"    issue: {issue.step} {issue.partition_name}: {issue.error}")
                if r.complete:
                    break
            log(
                f"    {calls} calls, {batches} batches, {moved:,} rows moved into {len(partitions)} partitions "
                f"in {time.perf_counter() - t0:.1f} s"
            )
            below = [v for v in st.visible if v < load.full_window]
            if below:
                # how long the oldest month was partly invisible: samples are ~20 ms apart plus the query
                first = next(i for i, v in enumerate(st.visible) if v < load.full_window)
                last = max(i for i, v in enumerate(st.visible) if v < load.full_window)
                span = sum(st.reads[first : last + 1]) / 1000 + (last - first) * 0.02
                log(f"    the oldest month was below its full count for about {span:.1f} s")

        # 5. The foreign key comes back.
        async with load.measure("5. the foreign key comes back"):
            await expect_error(
                admin,
                "ADD FOREIGN KEY (event_id) REFERENCES events (id)",
                "ALTER TABLE event_notes ADD FOREIGN KEY (event_id) REFERENCES events (id)",
            )
            await timed(admin, "ADD COLUMN event_created_at", "ALTER TABLE event_notes ADD COLUMN event_created_at TIMESTAMPTZ")
            await timed(
                admin,
                f"backfill it from events ({NOTES:,} notes)",
                "UPDATE event_notes n SET event_created_at = e.created_at FROM events e WHERE e.id = n.event_id",
            )
            await timed(
                admin,
                "ADD FOREIGN KEY (event_id, event_created_at) ... NOT VALID",
                """
                ALTER TABLE event_notes
                    ADD CONSTRAINT event_notes_event_fkey
                    FOREIGN KEY (event_id, event_created_at) REFERENCES events (id, created_at) NOT VALID
                """,
            )
            await timed(admin, "VALIDATE CONSTRAINT", "ALTER TABLE event_notes VALIDATE CONSTRAINT event_notes_event_fkey")

        # 6. The empty DEFAULT.
        async with load.measure("6. detach and drop the empty DEFAULT"):
            left = await admin.fetchval("SELECT count(*) FROM ONLY events_legacy")
            log(f"    rows left in events_legacy: {left}")
            await timed(
                admin,
                "DETACH PARTITION events_legacy; DROP TABLE events_legacy",
                """
                BEGIN;
                SET LOCAL lock_timeout = '2s';
                ALTER TABLE events DETACH PARTITION events_legacy;
                DROP TABLE events_legacy;
                COMMIT;
                """,
            )

        await load.stop()
        await engine.dispose()

        log("--- the tree afterwards")
        await tree(admin)
        total = await admin.fetchval("SELECT count(*) FROM events")
        live = await admin.fetchval("SELECT count(*) FROM events WHERE kind = 'live'")
        log(f"    {total:,} rows through the parent; the writer inserted {load.inserted}, {live} are there")
        log("    the writer's statement never changed: INSERT INTO events (created_at, kind, payload) VALUES (now(), 'live', $1)")
        await admin.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
