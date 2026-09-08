"""Who creates the topic: the broker, the application, or a person.

One Kafka container. The lab asks what happens when a producer writes to a topic that does not
exist, when a consumer subscribes to one, when the application creates topics at startup, when it
asks for a different shape the second time, and when three replicas start at the same time.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from importlib.metadata import version

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient
from testcontainers.kafka import KafkaContainer

from aiokafka_foundation_kit import TopicConfig, ensure_topics_async
from aiokafka_foundation_kit.contrib.models import BaseKafkaProducerSettings
from aiokafka_foundation_kit.utils.config import build_kafka_common_config


def log(msg: str) -> None:
    print(msg, flush=True)


async def describe(settings, name: str) -> str:
    admin = AIOKafkaAdminClient(**build_kafka_common_config(settings))
    await admin.start()
    try:
        if name not in await admin.list_topics():
            return "does not exist"
        described = await admin.describe_topics([name])
        partitions = len(described[0]["partitions"])
        return f"exists with {partitions} partition(s)"
    finally:
        await admin.close()


async def main() -> None:
    with KafkaContainer() as kafka:
        bootstrap = kafka.get_bootstrap_server()
        settings = BaseKafkaProducerSettings(bootstrap_servers=bootstrap)
        log(f"aiokafka-foundation-kit {version('aiokafka-foundation-kit')}, aiokafka {version('aiokafka')}")

        log("--- 1. nobody created it: a producer writes to a topic that does not exist")
        typo = f"ordrs.events-{uuid.uuid4().hex[:6]}"          # the topic name with a typo in it
        producer = AIOKafkaProducer(bootstrap_servers=bootstrap)
        await producer.start()
        await producer.send_and_wait(typo, value=json.dumps({"id": 1}).encode())
        await producer.stop()
        log(f"    send to {typo}: accepted; the topic now {await describe(settings, typo)}")

        log("--- 2. a consumer subscribes to a topic that does not exist")
        ghost = f"orders.events-{uuid.uuid4().hex[:6]}"
        consumer = AIOKafkaConsumer(ghost, bootstrap_servers=bootstrap, group_id=f"g-{uuid.uuid4().hex[:6]}")
        await consumer.start()
        await consumer.getmany(timeout_ms=1000)
        await consumer.stop()
        log(f"    subscribe to {ghost}: no error; the topic now {await describe(settings, ghost)}")

        log("--- 3. the application creates its topics at startup")
        name = f"orders.events-{uuid.uuid4().hex[:6]}"
        await ensure_topics_async([TopicConfig(name=name, num_partitions=6, replication_factor=1)], settings)
        log(f"    ensure_topics_async(num_partitions=6): {await describe(settings, name)}")

        log("--- 4. the next deploy asks for a different shape")
        await ensure_topics_async([TopicConfig(name=name, num_partitions=12, replication_factor=1)], settings)
        log(f"    ensure_topics_async(num_partitions=12) on the same topic: {await describe(settings, name)}")

        log("--- 5. three replicas start at the same moment")
        raced = f"orders.raced-{uuid.uuid4().hex[:6]}"
        topic = TopicConfig(name=raced, num_partitions=3, replication_factor=1)

        async def replica(n: int) -> str:
            try:
                await ensure_topics_async([topic], settings)
                return f"replica {n}: started"
            except Exception as error:  # noqa: BLE001 - the lab reports whatever comes out
                return f"replica {n}: {type(error).__name__}: {str(error)[:70]}"

        for line in await asyncio.gather(*(replica(n) for n in (1, 2, 3))):
            log(f"    {line}")
        log(f"    the topic {await describe(settings, raced)}")

        log("--- 6. a shape the cluster cannot honour")
        impossible = f"orders.rf3-{uuid.uuid4().hex[:6]}"
        try:
            await ensure_topics_async(
                [TopicConfig(name=impossible, num_partitions=1, replication_factor=3)], settings
            )
            log("    replication_factor=3 on a one-broker cluster: accepted")
        except Exception as error:  # noqa: BLE001
            log(f"    replication_factor=3 on a one-broker cluster: {type(error).__name__}: {str(error)[:90]}")
        log(f"    the topic {await describe(settings, impossible)}")


if __name__ == "__main__":
    asyncio.run(main())
