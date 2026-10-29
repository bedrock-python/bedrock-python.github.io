"""One real Kafka broker and bounded reads for the three Kafka labs."""

import asyncio
from contextlib import asynccontextmanager, contextmanager

from aiokafka import AIOKafkaConsumer, TopicPartition
from aiokafka.admin import AIOKafkaAdminClient
from testcontainers.community.kafka import KafkaContainer

import kafka_flow as flow


@contextmanager
def infrastructure():
    kafka = KafkaContainer("confluentinc/cp-kafka:7.6.0").with_kraft()
    kafka.with_env("KAFKA_AUTO_CREATE_TOPICS_ENABLE", "false")
    try:
        kafka.start(timeout=120)
        yield kafka.get_bootstrap_server(), kafka
    finally:
        kafka.stop()


@asynccontextmanager
async def admin_client(bootstrap):
    admin = AIOKafkaAdminClient(bootstrap_servers=bootstrap)
    try:
        await admin.start()
        yield admin
    finally:
        await admin.close()


async def topic_shape(bootstrap, topic):
    async with admin_client(bootstrap) as admin:
        if topic not in await admin.list_topics():
            return None
        description, = await admin.describe_topics([topic])
        assert description["error_code"] == 0, description
        partitions = description["partitions"]
        return len(partitions), {len(partition["replicas"]) for partition in partitions}


async def fetch_count(consumer, count):
    found = []
    async with asyncio.timeout(20):
        while len(found) < count:
            batches = await consumer.getmany(timeout_ms=500, max_records=count - len(found))
            for records in batches.values():
                found.extend(records)
    return found


async def wait_topic_shape(bootstrap, topic, expected):
    # CreateTopics acknowledgement can precede the next client's metadata update.
    observed = None
    try:
        async with asyncio.timeout(20):
            while True:
                observed = await topic_shape(bootstrap, topic)
                if observed == expected:
                    return
                await asyncio.sleep(0.1)
    except TimeoutError as error:
        raise AssertionError(f"{topic}: expected {expected}, last metadata {observed}") from error


async def committed_offset(bootstrap, group, topic=flow.TOPIC):
    consumer = AIOKafkaConsumer(bootstrap_servers=bootstrap, group_id=group,
                               enable_auto_commit=False)
    try:
        await consumer.start()
        return await consumer.committed(TopicPartition(topic, 0))
    finally:
        await consumer.stop()


async def seed(bootstrap, count=10):
    async with flow.delivery_producer(bootstrap) as producer:
        for revision in range(count):
            await flow.publish_status(producer, "delivery-42", "in_transit", revision)
