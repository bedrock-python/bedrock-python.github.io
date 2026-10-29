"""Check the published topic-creation API without replacing library functions."""

import asyncio
from uuid import uuid4

from aiokafka_foundation_kit import TopicConfig, ensure_topics_async
from aiokafka_foundation_kit.contrib.models import BaseKafkaProducerSettings

from lab_support import infrastructure, wait_topic_shape


async def check_topic_creation(bootstrap):
    name = f"delivery.probe.{uuid4().hex}"
    settings = BaseKafkaProducerSettings(bootstrap_servers=bootstrap)
    await ensure_topics_async([
        TopicConfig(name=name, num_partitions=3, replication_factor=1),
    ], settings)
    await wait_topic_shape(bootstrap, name, (3, {1}))
    print("PASS published ensure_topics_async: partitions=3, replicas=1; no monkeypatch", flush=True)


if __name__ == "__main__":
    with infrastructure() as (bootstrap, _):
        asyncio.run(check_topic_creation(bootstrap))
