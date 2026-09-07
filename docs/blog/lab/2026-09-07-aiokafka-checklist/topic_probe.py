"""Can aiokafka-foundation-kit create a topic at all? And does the one-line change fix it?"""

import asyncio
import uuid
from importlib.metadata import version

from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from testcontainers.kafka import KafkaContainer

from aiokafka_foundation_kit import TopicConfig, ensure_topics_async, producer_lifecycle
from aiokafka_foundation_kit.contrib.models import BaseKafkaProducerSettings
from aiokafka_foundation_kit.topics import management
from aiokafka_foundation_kit.utils.config import build_kafka_common_config


async def exists(settings, name: str) -> bool:
    admin = AIOKafkaAdminClient(**build_kafka_common_config(settings))
    await admin.start()
    try:
        return name in await admin.list_topics()
    finally:
        await admin.close()


async def try_it(settings, label: str) -> None:
    name = f"probe-{uuid.uuid4().hex[:6]}"
    topic = TopicConfig(name=name, num_partitions=3, replication_factor=1)
    try:
        await ensure_topics_async([topic], settings)
        result = "no exception"
    except Exception as error:  # noqa: BLE001
        result = f"{type(error).__name__}: {error}"
    print(f"    {label:<44} {result}; topic {'exists' if await exists(settings, name) else 'was not created'}", flush=True)


async def main() -> None:
    print(f"aiokafka-foundation-kit {version('aiokafka-foundation-kit')}, aiokafka {version('aiokafka')}")
    with KafkaContainer() as kafka:
        settings = BaseKafkaProducerSettings(bootstrap_servers=kafka.get_bootstrap_server())
        print("--- ensure_topics_async with a plain TopicConfig")
        await try_it(settings, "as published")

        # The only difference: replica_assignments stays None when no assignment was given.
        def patched(topic):
            return NewTopic(
                name=topic.name,
                num_partitions=topic.num_partitions,
                replication_factor=topic.replication_factor,
                replica_assignments=topic.replica_assignment or None,
                topic_configs=topic.topic_configs or {},
            )

        management._to_new_topic = patched
        await try_it(settings, "with replica_assignments=None when unset")

        print("--- and the documented producer_lifecycle path")
        name = f"probe-{uuid.uuid4().hex[:6]}"
        management._to_new_topic = patched
        async with producer_lifecycle(
            settings, topics=[TopicConfig(name=name, num_partitions=6, replication_factor=1)], auto_create_topics=True
        ) as producer:
            await producer.send_and_wait(name, {"id": 1})
        print(f"    patched: topic {'exists' if await exists(settings, name) else 'was not created'}", flush=True)


asyncio.run(main())
