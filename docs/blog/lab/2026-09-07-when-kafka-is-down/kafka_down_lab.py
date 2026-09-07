"""What happens to an outbox when Kafka is gone for a while, and what happens when it comes back."""

import asyncio
import time
import uuid

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from testcontainers.kafka import KafkaContainer
from testcontainers.postgres import PostgresContainer

from omni_box import OmniBoxDomainService, OutboxPublisher
from omni_box.core.converters import EnvelopeEventConverter
from omni_box.infra.brokers.kafka import KafkaEventPublisher
from omni_box.infra.storage.postgres import OutboxEventDBBase, PostgresOutboxRepository

EVENTS = 20
TOPIC = "orders.events"


class Base(DeclarativeBase):
    pass


class OutboxEventDB(Base, OutboxEventDBBase):
    pass


async def statuses(session_factory) -> dict:
    async with session_factory() as s:
        rows = (await s.execute(text("SELECT status, attempts_made, count(*) FROM outbox_events GROUP BY 1, 2 ORDER BY 1, 2"))).all()
    return {f"{status}/attempts={attempts}": n for status, attempts, n in rows}


async def on_topic(bootstrap: str) -> int:
    consumer = AIOKafkaConsumer(TOPIC, bootstrap_servers=bootstrap, group_id=f"audit-{uuid.uuid4().hex[:6]}", auto_offset_reset="earliest", enable_auto_commit=False)
    await consumer.start()
    try:
        return sum(len(r) for r in (await consumer.getmany(timeout_ms=3000)).values())
    finally:
        await consumer.stop()


async def main(db_url: str, bootstrap: str, kafka_wrapped) -> None:
    engine = create_async_engine(db_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    domain = OmniBoxDomainService(max_attempts=6)   # the default budget
    async with session_factory() as session, session.begin():
        repo = PostgresOutboxRepository(session, model_class=OutboxEventDB)
        for i in range(EVENTS):
            order_id = uuid.uuid4()
            await repo.create(domain.create_outbox_event(aggregate_type="order", aggregate_id=order_id, event_type="order.created",
                                                         topic=TOPIC, partition_key=str(order_id), payload={"n": i}))
    print(f"--- {EVENTS} events in the outbox, Kafka reachable ---")
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap, request_timeout_ms=2000)  # fail in seconds, not the 40 s default
    await producer.start()
    broker = KafkaEventPublisher(producer=producer, converter=EnvelopeEventConverter(), max_infra_retries=1)

    async def relay_cycle(batch_size: int = 100) -> None:
        async with session_factory() as session, session.begin():
            await OutboxPublisher(PostgresOutboxRepository(session, model_class=OutboxEventDB), broker, publish_timeout=5.0).publish_batch(worker_id="relay-1", batch_size=batch_size)

    kafka_wrapped.pause()
    print("\n--- Kafka paused; the relay keeps ticking every cycle ---")
    t0 = time.perf_counter()
    for cycle in range(1, 8):
        await relay_cycle()
        print(f"  cycle {cycle} at {time.perf_counter() - t0:5.1f} s: {await statuses(session_factory)}")
    kafka_wrapped.unpause()
    await asyncio.sleep(1.0)
    print("\n--- Kafka is back ---")
    await relay_cycle()
    print(f"  next relay cycle: {await statuses(session_factory)}; messages on the topic: {await on_topic(bootstrap)}")
    async with session_factory() as session, session.begin():
        repo = PostgresOutboxRepository(session, model_class=OutboxEventDB)
        failed = (await session.execute(text("SELECT id FROM outbox_events WHERE status = 'failed'"))).scalars().all()
        for event_id in failed:
            await repo.requeue_failed(event_id)
    await relay_cycle()
    print(f"  after requeue_failed on every failed row and one more cycle: {await statuses(session_factory)}; messages on the topic: {await on_topic(bootstrap)}")
    await producer.stop()
    await engine.dispose()


with PostgresContainer("postgres:17-alpine") as pg, KafkaContainer() as kafka:
    asyncio.run(main(pg.get_connection_url().replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1), kafka.get_bootstrap_server(), kafka.get_wrapped_container()))
