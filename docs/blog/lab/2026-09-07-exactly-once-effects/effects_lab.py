"""Every failure window between a database commit and a Kafka publish, and what closes each one."""

import asyncio
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from sqlalchemy import Column, String, Table, func, select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from testcontainers.kafka import KafkaContainer
from testcontainers.postgres import PostgresContainer

from omni_box import InboxConsumerRunner, InboxEvent, InboxEventRepository, OmniBoxDomainService, OutboxPublisher
from omni_box.core.converters import EnvelopeEventConverter
from omni_box.core.protocols.transaction import InboxTransactionProviderProtocol
from omni_box.infra.brokers.kafka import KafkaEventConsumer, KafkaEventPublisher
from omni_box.infra.storage.postgres import InboxEventDBBase, OutboxEventDBBase, PostgresInboxRepository, PostgresOutboxRepository


class Base(DeclarativeBase):
    pass


class OutboxEventDB(Base, OutboxEventDBBase):
    pass


class InboxEventDB(Base, InboxEventDBBase):
    pass


orders = Table("orders", Base.metadata, Column("id", String, primary_key=True), Column("scene", String))
invoices = Table("invoices", Base.metadata, Column("order_id", String, primary_key=True))


class ProcessCrash(Exception):
    """The worker died here."""


async def count_messages(bootstrap: str, topic: str) -> int:
    consumer = AIOKafkaConsumer(topic, bootstrap_servers=bootstrap, group_id=f"audit-{uuid.uuid4().hex[:6]}",
                                auto_offset_reset="earliest", enable_auto_commit=False)
    await consumer.start()
    try:
        batches = await consumer.getmany(timeout_ms=3000)
        return sum(len(records) for records in batches.values())
    finally:
        await consumer.stop()


async def count_rows(session_factory, table, scene: str | None = None) -> int:
    async with session_factory() as session:
        query = select(func.count()).select_from(table)
        if scene is not None:
            query = query.where(table.c.scene == scene)
        return (await session.execute(query)).scalar_one()


async def main(db_url: str, bootstrap: str) -> None:
    engine = create_async_engine(db_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap)
    await producer.start()
    domain = OmniBoxDomainService()

    print("--- dual write, the two orders ---")
    # 1. commit, then publish; the process dies between the two
    order_id = str(uuid.uuid4())
    async with session_factory() as session, session.begin():
        await session.execute(orders.insert().values(id=order_id, scene="commit-then-publish"))
    try:
        raise ProcessCrash()  # ...before producer.send_and_wait("orders.commit-then-publish", ...)
    except ProcessCrash:
        pass
    print(f"  commit, then publish, crash between:  orders={await count_rows(session_factory, orders, 'commit-then-publish')} "
          f"messages={await count_messages(bootstrap, 'orders.commit-then-publish')}")

    # 2. publish, then commit; the commit fails
    order_id = str(uuid.uuid4())
    await producer.send_and_wait("orders.publish-then-commit", key=order_id.encode(), value=b'{"event":"order.created"}')
    try:
        async with session_factory() as session, session.begin():
            await session.execute(orders.insert().values(id=order_id, scene="publish-then-commit"))
            raise ProcessCrash()  # the transaction rolls back
    except ProcessCrash:
        pass
    print(f"  publish, then commit, commit fails:   orders={await count_rows(session_factory, orders, 'publish-then-commit')} "
          f"messages={await count_messages(bootstrap, 'orders.publish-then-commit')}")

    print("\n--- outbox: the row and the event commit together; the relay publishes at least once ---")
    order_id = str(uuid.uuid4())
    async with session_factory() as session, session.begin():
        await session.execute(orders.insert().values(id=order_id, scene="outbox"))
        await PostgresOutboxRepository(session, model_class=OutboxEventDB).create(
            domain.create_outbox_event(
                aggregate_type="order", aggregate_id=uuid.UUID(order_id), event_type="order.created",
                topic="orders.outbox", partition_key=order_id, payload={"order_id": order_id},
                idempotency_key=f"order.created:{order_id}",
            )
        )
    broker = KafkaEventPublisher(producer=producer, converter=EnvelopeEventConverter())

    async def relay_cycle(crash_after_send: bool) -> None:
        async with session_factory() as session, session.begin():
            repo = PostgresOutboxRepository(session, model_class=OutboxEventDB)
            result = await OutboxPublisher(repo, broker).publish_batch(worker_id="relay-1", batch_size=100)
            if crash_after_send and result.processed_event_ids:
                raise ProcessCrash()  # sent to Kafka, died before the commit that marks the row completed

    try:
        await relay_cycle(crash_after_send=True)
    except ProcessCrash:
        pass
    async with session_factory() as session:
        status = (await session.execute(text("SELECT status, attempts_made FROM outbox_events"))).all()
    print(f"  relay cycle 1, crash after the send:  outbox rows {status}  messages={await count_messages(bootstrap, 'orders.outbox')}")
    await relay_cycle(crash_after_send=False)
    async with session_factory() as session:
        status = (await session.execute(text("SELECT status, attempts_made FROM outbox_events"))).all()
    print(f"  relay cycle 2, normal:                outbox rows {status}  messages={await count_messages(bootstrap, 'orders.outbox')}")

    print("\n--- inbox: both copies arrive; the invoice is written once ---")

    class InboxTxProvider(InboxTransactionProviderProtocol):
        session = None  # TEMPORARY until omni-box exposes repo.session: the handler needs the transaction it runs in

        @asynccontextmanager
        async def transaction(self) -> AsyncIterator[InboxEventRepository]:
            async with session_factory() as session, session.begin():
                self.session = session
                yield PostgresInboxRepository(session, model_class=InboxEventDB)

    provider = InboxTxProvider()

    async def create_invoice(event: InboxEvent, repo: InboxEventRepository) -> None:
        await provider.session.execute(invoices.insert().values(order_id=event.payload["order_id"]))  # same transaction as the inbox row

    kafka_consumer = AIOKafkaConsumer("orders.outbox", bootstrap_servers=bootstrap, group_id="billing",
                                      auto_offset_reset="earliest", enable_auto_commit=False)
    runner = InboxConsumerRunner(consumer=KafkaEventConsumer(kafka_consumer), transaction_provider=provider,
                                 handler=create_invoice, worker_id="billing-1", consumer_group="billing")
    await runner.start()
    try:
        for n in (1, 2):
            r = await runner.process_one()
            print(f"  delivery {n}: processed={r.processed} duplicate={r.duplicate} committed={r.committed}  "
                  f"invoices={await count_rows(session_factory, invoices)}")
    finally:
        await runner.stop()
    await producer.stop()
    await engine.dispose()


with PostgresContainer("postgres:17-alpine") as pg, KafkaContainer() as kafka:
    asyncio.run(main(pg.get_connection_url().replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1), kafka.get_bootstrap_server()))
