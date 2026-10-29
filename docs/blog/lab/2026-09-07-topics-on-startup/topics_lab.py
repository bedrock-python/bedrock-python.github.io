"""Topic creation, concurrent startup and rejected topology on a real broker."""

import asyncio
from pathlib import Path
import sys
from uuid import uuid4

from aiokafka.errors import InvalidReplicationFactorError
from aiokafka_foundation_kit import TopicConfig, ensure_topics_async, producer_lifecycle
from aiokafka_foundation_kit.contrib.models import BaseKafkaProducerSettings

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "2026-09-07-aiokafka-checklist"))
import kafka_flow as flow
from lab_support import infrastructure, topic_shape, wait_topic_shape


async def main(bootstrap):
    settings = BaseKafkaProducerSettings(bootstrap_servers=bootstrap)
    name = f"delivery.disabled.{uuid4().hex}"
    topic = TopicConfig(name=name, num_partitions=3, replication_factor=1)
    async with producer_lifecycle(settings, topics=[topic]):
        pass
    assert await topic_shape(bootstrap, name) is None
    async with producer_lifecycle(settings, topics=[topic], auto_create_topics=True):
        pass
    await wait_topic_shape(bootstrap, name, (3, {1}))
    print("PASS lifecycle topics: creation needs auto_create_topics=True", flush=True)

    await asyncio.gather(*(flow.provision_delivery_topic(bootstrap) for _ in range(3)))
    await wait_topic_shape(bootstrap, flow.TOPIC, (3, {1}))
    print("PASS three concurrent provisioners: one topic, partitions=3", flush=True)
    await flow.provision_delivery_topic(bootstrap, partitions=6)
    assert await topic_shape(bootstrap, flow.TOPIC) == (3, {1})
    print("PASS create-if-absent is not reconciliation: requested=6, existing=3", flush=True)

    prefix = f"delivery.partial.{uuid4().hex}"
    before, impossible, after = (f"{prefix}.{suffix}" for suffix in ("before", "rf3", "after"))
    try:
        await ensure_topics_async([
            TopicConfig(name=before, num_partitions=1, replication_factor=1),
            TopicConfig(name=impossible, num_partitions=1, replication_factor=3),
            TopicConfig(name=after, num_partitions=1, replication_factor=1),
        ], settings)
    except InvalidReplicationFactorError:
        pass
    else:
        raise AssertionError("A single broker cannot supply three replicas")
    await wait_topic_shape(bootstrap, before, (1, {1}))
    assert await topic_shape(bootstrap, impossible) is None
    assert await topic_shape(bootstrap, after) is None
    print("PASS invalid replication factor: error propagated; earlier topic exists, later topic absent", flush=True)


if __name__ == "__main__":
    with infrastructure() as (bootstrap, _):
        asyncio.run(main(bootstrap))
