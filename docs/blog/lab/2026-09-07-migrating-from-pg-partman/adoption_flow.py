"""The article's explicit policy choice and per-table handover."""
from pg_partsmith import (
    CreateAhead, DropNever, KeepNewest, LifecyclePolicy,
    PartitionGranularity, TablePartitionConfig,
)


# snippet:adoption
def adopted_config(settings):
    return TablePartitionConfig(
        schema="public",
        table_name="events",
        partition_column=settings["control"],
        granularity=PartitionGranularity.MONTH,
        lifecycle=LifecyclePolicy(
            creation=CreateAhead(count=3),  # Current month and two future months.
            # An explicit NEW retention rule, not a conversion of an interval.
            retention=KeepNewest(count=3),
            drop=DropNever(),
        ),
    )


async def unregister_partman(connection):
    # First stop and drain jobs that explicitly pass this parent table.
    await connection.execute(
        "DELETE FROM partman.part_config WHERE parent_table = 'public.events'",
    )
# /snippet:adoption
