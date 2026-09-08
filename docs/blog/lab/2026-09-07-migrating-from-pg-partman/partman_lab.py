"""Adopting a pg_partman-managed table, without recreating a single partition.

The container runs PostgreSQL 17 with pg_partman installed. The lab lets pg_partman create and
maintain a monthly table, reads its configuration out of `part_config`, maps it onto a
pg-partsmith configuration, and then asks pg-partsmith what it sees: whether the partitions
pg_partman made are recognised as its own, what its plan says while both are still configured,
and what happens after pg_partman is switched off.
"""

from __future__ import annotations

import asyncio
from datetime import timedelta
from importlib.metadata import version

import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

from pg_partsmith import (
    CreateAhead,
    DropAfter,
    KeepNewest,
    LifecyclePolicy,
    PartitionGranularity,
    TablePartitionConfig,
)
from pg_partsmith.aio import PartitionToolkit

IMAGE = "pg-partman-lab:17"


def log(msg: str) -> None:
    print(msg, flush=True)


async def partitions(conn: asyncpg.Connection) -> list[tuple[str, str]]:
    return [
        (r["relname"], r["bound"])
        for r in await conn.fetch(
            """
            SELECT c.relname, pg_get_expr(c.relpartbound, c.oid) AS bound
            FROM pg_inherits h JOIN pg_class c ON c.oid = h.inhrelid
            WHERE h.inhparent = 'public.events'::regclass ORDER BY c.relname
            """
        )
    ]


async def main() -> None:
    container = (
        DockerContainer(IMAGE)
        .with_env("POSTGRES_PASSWORD", "postgres")
        .with_env("POSTGRES_DB", "lab")
        .with_exposed_ports(5432)
        .with_command("postgres -c shared_preload_libraries=pg_partman_bgw")
    )
    container.start()
    try:
        wait_for_logs(container, "database system is ready to accept connections", timeout=60)
        await asyncio.sleep(2)
        dsn = (
            f"postgresql://postgres:postgres@{container.get_container_host_ip()}:"
            f"{container.get_exposed_port(5432)}/lab"
        )
        conn = await asyncpg.connect(dsn)
        log(f"pg-partsmith {version('pg-partsmith')}, "
            f"PostgreSQL {await conn.fetchval('SHOW server_version')}")

        log("--- 1. pg_partman creates and maintains the table")
        await conn.execute("CREATE SCHEMA partman; CREATE EXTENSION pg_partman WITH SCHEMA partman;")
        partman_version = await conn.fetchval(
            "SELECT extversion FROM pg_extension WHERE extname = 'pg_partman'"
        )
        log(f"    pg_partman {partman_version}")
        await conn.execute(
            """
            CREATE TABLE public.events (
                id          BIGSERIAL,
                created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
                payload     TEXT NOT NULL,
                PRIMARY KEY (id, created_at)
            ) PARTITION BY RANGE (created_at);
            """
        )
        await conn.execute(
            """
            SELECT partman.create_parent(
                p_parent_table := 'public.events',
                p_control := 'created_at',
                p_interval := '1 month',
                p_premake := 2
            );
            """
        )
        await conn.execute("UPDATE partman.part_config SET retention = '3 months', retention_keep_table = true "
                           "WHERE parent_table = 'public.events'")
        await conn.execute("SELECT partman.run_maintenance('public.events')")
        for name, bound in await partitions(conn):
            log(f"    {name:<24} {bound}")

        log("--- 2. what pg_partman's configuration says")
        row = await conn.fetchrow(
            "SELECT control, partition_interval, premake, retention, retention_keep_table "
            "FROM partman.part_config WHERE parent_table = 'public.events'"
        )
        for key in row.keys():
            log(f"    {key:<22} {row[key]}")
        log("    the same thing as a pg-partsmith configuration:")
        log("      partition_column='created_at', granularity=MONTH,")
        log("      creation=CreateAhead(count=premake + 1), retention=KeepNewest(count=3),")
        log("      drop=DropNever() while retention_keep_table is true")

        config = TablePartitionConfig(
            schema="public",
            table_name="events",
            partition_column="created_at",
            granularity=PartitionGranularity.MONTH,
            lifecycle=LifecyclePolicy(
                creation=CreateAhead(count=row["premake"] + 1),
                retention=KeepNewest(count=3),
                drop=DropAfter(grace=timedelta(days=7)),
            ),
        )

        engine = create_async_engine(dsn.replace("postgresql://", "postgresql+asyncpg://"))
        toolkit = PartitionToolkit.from_engine(engine)
        try:
            log("--- 3. what pg-partsmith sees in a tree it did not build")
            tree = await toolkit.service.inspect(config)
            children = tree.root.children if hasattr(tree.root, "children") else ()
            log(f"    inspect: the root has {len(children)} children, "
                f"{len(tree.orphans)} detached partition(s) known to the library")
            plan = await toolkit.service.plan(config)
            for line in plan.describe().splitlines():
                log(f"    {line}")

            log("--- 4. one tick of pg-partsmith on the same table")
            result = await toolkit.maintainer.run_maintenance_safe(config)
            log(f"    created={result.created_count} detached={result.detached_count} "
                f"dropped={result.dropped_count} issues={len(result.issues)} error={result.error!r}")
            for name, _ in await partitions(conn):
                log(f"    {name}")

            log("--- 5. and one more run of pg_partman, after pg-partsmith's tick")
            await conn.execute("SELECT partman.run_maintenance('public.events')")
            after = [name for name, _ in await partitions(conn)]
            log(f"    {len(after)} partitions: {', '.join(after)}")

            log("--- 6. pg_partman switched off, and a policy that differs from its own")
            await conn.execute("DELETE FROM partman.part_config WHERE parent_table = 'public.events'")
            wider = TablePartitionConfig(
                schema="public",
                table_name="events",
                partition_column="created_at",
                granularity=PartitionGranularity.MONTH,
                lifecycle=LifecyclePolicy(
                    creation=CreateAhead(count=4),      # one month further ahead than pg_partman built
                    retention=KeepNewest(count=2),      # one month less history than pg_partman kept
                    drop=DropAfter(grace=timedelta(days=7)),
                ),
            )
            plan = await toolkit.service.plan(wider)
            for line in plan.describe().splitlines():
                log(f"    {line}")
            result = await toolkit.maintainer.run_maintenance_safe(wider)
            log(f"    created={result.created_count} detached={result.detached_count} "
                f"dropped={result.dropped_count} issues={len(result.issues)}")
            for issue in result.issues:
                log(f"    issue: {issue.step} {issue.partition_name}: {str(issue.error)[:100]}")
            for name, _ in await partitions(conn):
                log(f"    {name}")
            detached = await conn.fetch(
                """
                SELECT c.relname, obj_description(c.oid, 'pg_class') AS marker
                FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = 'public' AND c.relkind = 'r' AND c.relname LIKE 'events\\_p%'
                  AND NOT EXISTS (SELECT 1 FROM pg_inherits h WHERE h.inhrelid = c.oid)
                """
            )
            for row in detached:
                log(f"    detached: {row['relname']} marker={str(row['marker'])[:60]!r}")
        finally:
            await engine.dispose()
            await conn.close()
    finally:
        container.stop()


if __name__ == "__main__":
    asyncio.run(main())
