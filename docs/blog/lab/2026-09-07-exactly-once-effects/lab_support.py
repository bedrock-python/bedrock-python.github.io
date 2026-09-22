"""Container lifecycle and bounded Kafka reads, shared by the three labs."""

import asyncio
from contextlib import asynccontextmanager, contextmanager

from aiokafka import AIOKafkaConsumer, TopicPartition
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from testcontainers.community.kafka import KafkaContainer
from testcontainers.community.postgres import PostgresContainer

from models import Base, Invoice


class ProcessCrash(RuntimeError):
    """An injected exception at a specific transaction boundary."""


@contextmanager
def infrastructure():
    # A single broker is sufficient for these failure windows, not replication tests.
    with PostgresContainer("postgres:17-alpine", driver="asyncpg") as pg:
        kafka = KafkaContainer("confluentinc/cp-kafka:7.6.0").with_kraft()
        try:
            kafka.start(timeout=120)
            yield pg.get_connection_url(), kafka.get_bootstrap_server(), kafka
        finally:
            kafka.stop()


@asynccontextmanager
async def database(url):
    engine = create_async_engine(url)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield async_sessionmaker(engine, expire_on_commit=False)
    finally:
        await engine.dispose()


async def create_topics(bootstrap, *topics):
    admin = AIOKafkaAdminClient(bootstrap_servers=bootstrap)
    try:
        await admin.start()
        await admin.create_topics([
            NewTopic(topic, num_partitions=1, replication_factor=1) for topic in topics
        ])
    finally:
        await admin.close()


async def records(bootstrap, topic):
    """Read to a captured end offset; do not mistake assignment delay for an empty topic."""
    consumer = AIOKafkaConsumer(bootstrap_servers=bootstrap, enable_auto_commit=False)
    try:
        await consumer.start()
        tp = TopicPartition(topic, 0)
        consumer.assign([tp])
        await consumer.seek_to_beginning(tp)
        end = (await consumer.end_offsets([tp]))[tp]
        found = []
        async with asyncio.timeout(20):
            while await consumer.position(tp) < end:
                batches = await consumer.getmany(tp, timeout_ms=1000)
                found.extend(record for record in batches.get(tp, []) if record.offset < end)
        return found
    finally:
        await consumer.stop()


async def count(sessions, model, *conditions):
    async with sessions() as session:
        return await session.scalar(select(func.count()).select_from(model).where(*conditions))


async def invoice_count(sessions, order_id):
    return await count(sessions, Invoice, Invoice.order_id == order_id)


async def process(runner, how_many=1):
    try:
        await runner.start()
        async with asyncio.timeout(30):
            return [await runner.process_one() for _ in range(how_many)]
    finally:
        await runner.stop()


async def committed_offset(bootstrap, topic, group):
    consumer = AIOKafkaConsumer(bootstrap_servers=bootstrap, group_id=group,
                               enable_auto_commit=False)
    try:
        await consumer.start()
        return await consumer.committed(TopicPartition(topic, 0))
    finally:
        await consumer.stop()
