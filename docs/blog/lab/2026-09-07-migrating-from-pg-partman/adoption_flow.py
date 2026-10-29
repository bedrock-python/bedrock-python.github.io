"""pg_partman's settings expressed as a pg-partsmith policy, and the per-table handover."""
from pg_partsmith import (
    CreateAhead, DropNever, KeepNewest, LifecyclePolicy,
    PartitionGranularity, TablePartitionConfig,
)


# snippet:adoption
def adopted_config(settings):
    # Monthly table: premake counts future tables, CreateAhead also counts the current month.
    # retention='3 months' keeps the current month and three before it; retention_keep_table=true
    # leaves detached tables in place.
    return TablePartitionConfig(
        schema="public",
        table_name="events",
        partition_column=settings["control"],
        granularity=PartitionGranularity.MONTH,
        lifecycle=LifecyclePolicy(
            creation=CreateAhead(count=settings["premake"] + 1),
            retention=KeepNewest(count=4),
            drop=DropNever(),
        ),
    )


async def unregister_partman(connection):
    # First stop and drain jobs that explicitly pass this parent table.
    await connection.execute(
        "DELETE FROM partman.part_config WHERE parent_table = 'public.events'",
    )
# /snippet:adoption
