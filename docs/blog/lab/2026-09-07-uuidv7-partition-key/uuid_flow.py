"""UUIDv7 range configuration and the query shown in the article."""
from datetime import UTC, datetime

# snippet:uuid_config
from pg_partsmith import (
    PartitionGranularity, RangePartitioning, TablePartitionConfig,
    TimeBoundaries, UUIDv7BoundaryCodec,
)


CONFIG = TablePartitionConfig(
    schema="public",
    table_name="uuid_events",
    scheme=RangePartitioning(
        key="id",
        boundaries=TimeBoundaries(
            granularity=PartitionGranularity.MONTH,
            codec=UUIDv7BoundaryCodec(),
        ),
    ),
)
# /snippet:uuid_config


# snippet:uuid_query
async def august_events(connection):
    start = datetime(2026, 8, 1, tzinfo=UTC)
    end = datetime(2026, 9, 1, tzinfo=UTC)
    lower, upper = UUIDv7BoundaryCodec().encode(start, end)
    return await connection.fetch(
        "SELECT payload FROM uuid_events WHERE id >= $1::uuid AND id < $2::uuid",
        lower, upper,
    )
# /snippet:uuid_query
