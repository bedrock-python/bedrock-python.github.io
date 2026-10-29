"""The article's executable policy, plan, archive and scheduler examples."""
from datetime import timedelta
import json
from pathlib import Path

from pg_partsmith import (
    AllOf, CreateAhead, DropAfter, ExpireIf, KeepNewest,
    LifecyclePolicy, LockAcquisitionError, PartitionEvent, PartitionGranularity,
    TablePartitionConfig, Unreferenced,
)
from pg_partsmith.aio import BasePartitionLifecycleHooks


# snippet:policy
def events_config(*, protect_references=True):
    retention = KeepNewest(count=3)
    if protect_references:
        retention = ExpireIf(
            when=AllOf(members=(retention, Unreferenced())),
        )
    return TablePartitionConfig(
        schema="public",
        table_name="events",
        partition_column="created_at",
        granularity=PartitionGranularity.MONTH,
        lifecycle=LifecyclePolicy(
            creation=CreateAhead(count=3),
            retention=retention,
            drop=DropAfter(grace=timedelta(days=7)),
        ),
    )
# /snippet:policy


# snippet:plan
async def preview(toolkit, config, *, now=None):
    plan = await toolkit.service.plan(config, now=now)
    print(plan.describe())
    return plan


async def apply_reviewed(toolkit, config, plan):
    result = await toolkit.service.apply(config, plan)
    if result.error or result.issues:
        raise RuntimeError(f"Maintenance needs attention: {result}")
    return result
# /snippet:plan


# snippet:archive
class JsonArchive(BasePartitionLifecycleHooks):
    def __init__(self, connection, directory: Path):
        self.connection = connection
        self.directory = directory

    async def before_drop(self, event: PartitionEvent):
        oid = await self.connection.fetchval("SELECT to_regclass($1)::oid", event.partition.name)
        if oid != event.operation.oid:
            raise RuntimeError(f"{event.partition.name} is not the planned table")
        schema, name = event.partition.name.split(".", 1)
        quoted = ".".join('"' + part.replace('"', '""') + '"' for part in (schema, name))
        rows = await self.connection.fetch(
            f"SELECT id, created_at, payload FROM {quoted} ORDER BY id, created_at",
        )
        data = [[row["id"], row["created_at"].isoformat(), row["payload"]] for row in rows]
        document = {"table": event.partition.name, "rows": data}
        path = self.directory / f"{oid}.json"
        if not path.exists():
            temporary = path.with_suffix(".tmp")
            temporary.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
            temporary.replace(path)
        if json.loads(path.read_text(encoding="utf-8")) != document:
            raise RuntimeError(f"Archive verification failed: {path.name}")
# /snippet:archive


# snippet:tick
async def maintenance_tick(toolkit, config):
    try:
        result = await toolkit.maintainer.run_maintenance(config)
    except LockAcquisitionError:
        print({"skipped": "another worker holds the maintenance lock"})
        return None
    print({
        "created": result.created_count,
        "detached": result.detached_count,
        "dropped": result.dropped_count,
        "duration_ms": result.duration_ms,
        "issues": [issue.model_dump() for issue in result.issues],
    })
    if result.issues:
        raise RuntimeError("Partition maintenance finished with issues")
    return result
# /snippet:tick
