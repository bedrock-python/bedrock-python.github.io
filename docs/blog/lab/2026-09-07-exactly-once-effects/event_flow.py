"""The executable Python snippets from the Outbox/Inbox article."""

# snippet:outbox
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from omni_box import OmniBoxDomainService
from omni_box.infra.storage.postgres import PostgresOutboxRepository

from models import Order, OutboxEventDB


async def record_order(session: AsyncSession, order_id: UUID) -> UUID:
    session.add(Order(id=order_id))
    event = OmniBoxDomainService().create_outbox_event(
        aggregate_type="order",
        aggregate_id=order_id,
        event_type="order.created",
        topic="orders.created",
        partition_key=str(order_id),
        payload={"order_id": str(order_id)},
    )
    repo = PostgresOutboxRepository(session, model_class=OutboxEventDB)
    await repo.create(event)
    return event.id


async def place_order(session_factory: async_sessionmaker, order_id: UUID) -> UUID:
    async with session_factory.begin() as session:
        return await record_order(session, order_id)
# /snippet:outbox


# snippet:relay
from omni_box import OutboxPublisher
from omni_box.infra.brokers.kafka import KafkaEventPublisher


async def relay_batch(session: AsyncSession, broker: KafkaEventPublisher):
    repo = PostgresOutboxRepository(session, model_class=OutboxEventDB)
    return await OutboxPublisher(repo, broker, publish_timeout=2).publish_batch(
        worker_id="relay-1", batch_size=20,
    )


async def relay_once(session_factory: async_sessionmaker, broker: KafkaEventPublisher):
    async with session_factory.begin() as session:
        return await relay_batch(session, broker)
# /snippet:relay


# snippet:transaction
from contextlib import asynccontextmanager

from omni_box.infra.storage.postgres import PostgresInboxRepository

from models import InboxEventDB


class InboxTransaction:
    def __init__(self, session_factory: async_sessionmaker):
        self.session_factory = session_factory

    @asynccontextmanager
    async def transaction(self):
        async with self.session_factory.begin() as session:
            yield PostgresInboxRepository(session, model_class=InboxEventDB)
# /snippet:transaction


# snippet:handler
from sqlalchemy import insert

from omni_box import InboxEvent

from models import Invoice


async def create_invoice(event: InboxEvent, repo: PostgresInboxRepository):
    await repo.session.execute(
        insert(Invoice).values(order_id=UUID(str(event.payload["order_id"])))
    )
# /snippet:handler


# snippet:consumer
from aiokafka import AIOKafkaConsumer

from omni_box import AckStrategy, InboxConsumerRunner
from omni_box.infra.brokers.kafka import KafkaEventConsumer


def billing_runner(session_factory, bootstrap, *, topic="orders.created",
                   group="billing", handler=create_invoice):
    consumer = AIOKafkaConsumer(
        topic, bootstrap_servers=bootstrap, group_id=group,
        auto_offset_reset="earliest", enable_auto_commit=False,
    )
    return InboxConsumerRunner(
        consumer=KafkaEventConsumer(consumer),
        transaction_provider=InboxTransaction(session_factory),
        handler=handler,
        worker_id="billing-1", consumer_group=group,
        ack_strategy=AckStrategy.EXACTLY_ONCE_INBOX,
    )
# /snippet:consumer


# snippet:worker
async def run_billing(runner: InboxConsumerRunner):
    try:
        await runner.start()
        while True:
            result = await runner.process_one()
            if not result.committed:
                raise RuntimeError(f"Retry message {result.message_id}")
    finally:
        await runner.stop()
# /snippet:worker


# The relay's producer setup; the labs use it, the article does not print it.
from aiokafka import AIOKafkaProducer

from omni_box.core.converters import EnvelopeEventConverter


@asynccontextmanager
async def kafka_publisher(bootstrap: str):
    producer = AIOKafkaProducer(
        bootstrap_servers=bootstrap, enable_idempotence=True, acks="all",
    )
    try:
        await producer.start()
        yield KafkaEventPublisher(producer, EnvelopeEventConverter())
    finally:
        await producer.stop()
