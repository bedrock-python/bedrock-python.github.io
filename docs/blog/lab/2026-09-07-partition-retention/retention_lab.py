"""Retention on a partitioned table: what a DROP by name does, and what a plan does instead.

PostgreSQL 17 in a container, `events` partitioned by month with fourteen months of data, one
partition somebody else attached by hand, and one still referenced by another table. Then:

1. the retention job everybody writes first: DROP TABLE by name pattern;
2. the same retention as a plan, printed before anything runs;
3. detach and drop as two steps, with a grace period between them;
4. an archive hook that runs before the drop, and what a failing hook does;
5. a partition whose rows another table still references.
"""

from __future__ import annotations

import asyncio
import re
from datetime import UTC, datetime, timedelta
from importlib.metadata import version

import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer

from pg_partsmith import (
    AllOf,
    CreateAhead,
    DropAfter,
    DropNever,
    ExpireIf,
    KeepNewest,
    LifecyclePolicy,
    PartitionEvent,
    PartitionGranularity,
    TablePartitionConfig,
    Unreferenced,
)
from pg_partsmith.aio import BasePartitionLifecycleHooks, PartitionToolkit

MONTHS = 14
KEEP = 12


def log(msg: str) -> None:
    print(msg, flush=True)


def month_start(offset: int) -> datetime:
    now = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    year, month = divmod((now.year * 12 + now.month - 1) - offset, 12)
    return datetime(year, month + 1, 1, tzinfo=UTC)


async def setup(conn: asyncpg.Connection) -> None:
    """A partitioned table, fourteen monthly partitions, one hand-made partition, one referenced."""
    await conn.execute(
        """
        CREATE TABLE events (
            id          BIGSERIAL,
            created_at  TIMESTAMPTZ NOT NULL,
            payload     TEXT NOT NULL,
            PRIMARY KEY (id, created_at)
        ) PARTITION BY RANGE (created_at);
        CREATE TABLE receipts (
            id          BIGSERIAL PRIMARY KEY,
            event_id    BIGINT NOT NULL,
            event_at    TIMESTAMPTZ NOT NULL,
            FOREIGN KEY (event_id, event_at) REFERENCES events (id, created_at)
        );
        """
    )
    for offset in range(MONTHS, -1, -1):
        start, end = month_start(offset), month_start(offset - 1)
        name = f"events__{start:%Y_%m}"
        await conn.execute(
            f'CREATE TABLE "{name}" PARTITION OF events FOR VALUES FROM (\'{start:%Y-%m-%d}\') TO (\'{end:%Y-%m-%d}\')'
        )
        await conn.execute(
            "INSERT INTO events (created_at, payload) "
            "SELECT $1::timestamptz + make_interval(hours => g), 'e' FROM generate_series(1, 20) g",
            start,
        )
    # A partition somebody attached by hand, on a boundary the scheme does not use.
    odd_start, odd_end = month_start(MONTHS + 2), month_start(MONTHS)
    await conn.execute(
        f'CREATE TABLE events_archive_old PARTITION OF events FOR VALUES FROM (\'{odd_start:%Y-%m-%d}\') TO (\'{odd_end:%Y-%m-%d}\')'
    )
    await conn.execute("INSERT INTO events (created_at, payload) VALUES ($1, 'hand-made')", odd_start)
    # One old partition is still referenced by receipts.
    referenced_month = month_start(KEEP + 1)
    row = await conn.fetchrow(
        "SELECT id, created_at FROM events WHERE created_at >= $1 AND created_at < $2 LIMIT 1",
        referenced_month,
        month_start(KEEP),
    )
    await conn.execute(
        "INSERT INTO receipts (event_id, event_at) VALUES ($1, $2)", row["id"], row["created_at"]
    )


async def tree(conn: asyncpg.Connection, *, label: str) -> None:
    rows = await conn.fetch(
        """
        SELECT c.relname FROM pg_inherits h JOIN pg_class c ON c.oid = h.inhrelid
        WHERE h.inhparent = 'public.events'::regclass ORDER BY c.relname
        """
    )
    detached = await conn.fetch(
        """
        SELECT c.relname FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND c.relkind = 'r' AND c.relname LIKE 'events\\_%'
          AND NOT EXISTS (SELECT 1 FROM pg_inherits h WHERE h.inhrelid = c.oid)
        ORDER BY c.relname
        """
    )
    total = await conn.fetchval("SELECT count(*) FROM events")
    log(f"    {label}: {len(rows)} attached, {len(detached)} detached, {total} rows through the parent")
    if detached:
        log(f"      detached: {', '.join(r['relname'] for r in detached)}")


# --- 1. the retention job everybody writes first ----------------------------------------------


async def fk_count(conn: asyncpg.Connection) -> int:
    return await conn.fetchval(
        "SELECT count(*) FROM pg_constraint WHERE conrelid = 'public.receipts'::regclass AND contype = 'f'"
    )


async def part_naive(conn: asyncpg.Connection) -> None:
    log("--- 1. the retention job everybody writes first: DROP TABLE by name pattern, keeping 12 months")
    names = [r["relname"] for r in await conn.fetch(
        """
        SELECT c.relname FROM pg_inherits h JOIN pg_class c ON c.oid = h.inhrelid
        WHERE h.inhparent = 'public.events'::regclass ORDER BY c.relname
        """
    )]
    # The job's idea of "old": everything but the newest KEEP names that look like a month.
    monthly = [n for n in names if re.fullmatch(r"events__\d{4}_\d{2}", n)]
    others = [n for n in names if n not in monthly]
    doomed = sorted(monthly)[:-KEEP] + others          # the "old" ones, plus whatever else is attached
    log(f"    the job's list: {doomed}")
    log(f"    foreign keys on receipts before the job: {await fk_count(conn)}")
    for name in doomed:
        try:
            await conn.execute(f'DROP TABLE "{name}"')
            log(f"    DROP TABLE {name}: dropped")
        except asyncpg.PostgresError as error:
            log(f"    DROP TABLE {name}: {type(error).__name__}: {str(error).splitlines()[0][:100]}")
            try:
                await conn.execute(f'DROP TABLE "{name}" CASCADE')   # what the job does next
                log(f"    DROP TABLE {name} CASCADE: dropped")
            except asyncpg.PostgresError as second:
                log(f"    DROP TABLE {name} CASCADE: {type(second).__name__}: {str(second)[:90]}")
    log(f"    foreign keys on receipts after the job:  {await fk_count(conn)}")
    await tree(conn, label="after the job")


# --- 2 to 5. the same retention, planned ------------------------------------------------------


class ArchiveHooks(BasePartitionLifecycleHooks):
    """Copy the partition somewhere cold before it is dropped; refuse the drop if that fails."""

    def __init__(self, *, fail: bool = False) -> None:
        self.archived: list[str] = []
        self.fail = fail

    async def before_drop(self, event: PartitionEvent) -> None:
        if self.fail:
            raise RuntimeError("the archive bucket is not reachable")
        self.archived.append(event.partition.name)

    async def after_drop(self, event: PartitionEvent) -> None:
        return None


def config(*, grace: timedelta | None, unreferenced: bool) -> TablePartitionConfig:
    retention = KeepNewest(count=KEEP)
    if unreferenced:
        retention = ExpireIf(when=AllOf(members=(KeepNewest(count=KEEP), Unreferenced())))
    return TablePartitionConfig(
        schema="public",
        table_name="events",
        partition_column="created_at",
        granularity=PartitionGranularity.MONTH,
        lifecycle=LifecyclePolicy(
            creation=CreateAhead(count=1),
            retention=retention,
            drop=DropNever() if grace is None else DropAfter(grace=grace),
        ),
    )


async def part_plan(conn: asyncpg.Connection, toolkit: PartitionToolkit) -> None:
    log("--- 2. the same retention as a plan, printed before anything runs")
    plan = await toolkit.service.plan(config(grace=timedelta(0), unreferenced=False))
    for line in plan.describe().splitlines():
        log(f"    {line}")
    for finding in plan.findings:
        log(f"    finding: {finding.reason} {finding.partition_name or ''} — {finding.detail}")
    log(f"    destructive operations: {[op.target for op in plan.operations if op.is_destructive]}")
    await tree(conn, label="nothing has run yet")


async def part_detach_then_drop(conn: asyncpg.Connection, engine) -> None:
    log("--- 3. detach now, drop after a grace period")
    hooks = ArchiveHooks()
    toolkit = PartitionToolkit.from_engine(engine, hooks=[hooks])
    result = await toolkit.maintainer.run_maintenance_safe(config(grace=timedelta(days=7), unreferenced=False))
    log(f"    detached={result.detached_count} dropped={result.dropped_count} issues={len(result.issues)} "
        f"error={result.error!r}")
    for issue in result.issues:
        log(f"    issue: {issue.step} {issue.partition_name}: {issue.error}")
    await tree(conn, label="after the tick with a 7-day grace")
    log(f"    the archive hook ran for: {hooks.archived or 'nothing'}")

    log("--- 4. the same partition once the grace has passed, with an archive hook that fails")
    failing = ArchiveHooks(fail=True)
    toolkit = PartitionToolkit.from_engine(engine, hooks=[failing])
    result = await toolkit.maintainer.run_maintenance_safe(config(grace=timedelta(0), unreferenced=False))
    log(f"    detached={result.detached_count} dropped={result.dropped_count} issues={len(result.issues)} "
        f"error={str(result.error)[:80]!r}")
    await tree(conn, label="after the tick whose hook raised")

    working = ArchiveHooks()
    toolkit = PartitionToolkit.from_engine(engine, hooks=[working])
    result = await toolkit.maintainer.run_maintenance_safe(config(grace=timedelta(0), unreferenced=False))
    log(f"    the next tick, hook working: dropped={result.dropped_count}, archived={working.archived}")
    await tree(conn, label="after the next tick")


async def part_referenced(conn: asyncpg.Connection, engine) -> None:
    log("--- 5. a partition another table still references")
    toolkit = PartitionToolkit.from_engine(engine)
    result = await toolkit.maintainer.run_maintenance_safe(config(grace=timedelta(0), unreferenced=False))
    log(f"    plain KeepNewest: detached={result.detached_count} dropped={result.dropped_count} "
        f"issues={len(result.issues)}")
    for issue in result.issues:
        log(f"    issue: {issue.step} {issue.partition_name}: {str(issue.error)[:120]}")

    plan = await toolkit.service.plan(config(grace=timedelta(0), unreferenced=True))
    log(f"    with Unreferenced() in the policy, the plan is: "
        f"{[op.target for op in plan.operations] or 'nothing to do'}")

    await conn.execute("DELETE FROM receipts")
    result = await toolkit.maintainer.run_maintenance_safe(config(grace=timedelta(0), unreferenced=True))
    log(f"    after the referencing row is gone: detached={result.detached_count} dropped={result.dropped_count}")
    await tree(conn, label="at the end")


async def main() -> None:
    with PostgresContainer("postgres:17-alpine") as pg:
        dsn = pg.get_connection_url().replace("postgresql+psycopg2://", "postgresql://")
        conn = await asyncpg.connect(dsn)
        log(f"pg-partsmith {version('pg-partsmith')}, PostgreSQL {await conn.fetchval('SHOW server_version')}")
        await setup(conn)
        await tree(conn, label=f"{MONTHS + 1} monthly partitions plus one attached by hand")
        await part_naive(conn)

        log("")
        log("=== the same table again, this time with a plan in front of the retention ===")
        await conn.execute("DROP TABLE receipts; DROP TABLE events; DROP TABLE IF EXISTS events_archive_old")
        await setup(conn)
        await tree(conn, label="rebuilt")

        engine = create_async_engine(dsn.replace("postgresql://", "postgresql+asyncpg://"))
        toolkit = PartitionToolkit.from_engine(engine)
        try:
            await part_plan(conn, toolkit)
            await part_detach_then_drop(conn, engine)
            await part_referenced(conn, engine)
        finally:
            await engine.dispose()
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
