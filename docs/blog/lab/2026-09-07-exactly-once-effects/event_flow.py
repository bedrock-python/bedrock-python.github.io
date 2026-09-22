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


async def place_order(sessions: async_sessionmaker, order_id: UUID) -> UUID:
    async with sessions.begin() as session:
        return await record_order(session, order_id)
# /snippet:outbox


# snippet:producer
from contextlib import asynccontextmanager

from aiokafka import AIOKafkaProducer

from omni_box.core.converters import EnvelopeEventConverter
from omni_box.infra.brokers.kafka import KafkaEventPublisher


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
# /snippet:producer


# snippet:relay
from omni_box import OutboxPublisher


async def relay_batch(session: AsyncSession, broker: KafkaEventPublisher):
    repo = PostgresOutboxRepository(session, model_class=OutboxEventDB)
    return await OutboxPublisher(repo, broker, publish_timeout=2).publish_batch(
        worker_id="relay-1", batch_size=20,
    )


async def relay_once(sessions: async_sessionmaker, broker: KafkaEventPublisher):
    async with sessions.begin() as session:
        return await relay_batch(session, broker)
# /snippet:relay


# snippet:transaction
from omni_box.infra.storage.postgres import PostgresInboxRepository

from models import InboxEventDB


class InboxTransaction:
    def __init__(self, sessions: async_sessionmaker):
        self.sessions = sessions

    @asynccontextmanager
    async def transaction(self):
        async with self.sessions.begin() as session:
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


def billing_runner(sessions, bootstrap, *, topic="orders.created",
                   group="billing", handler=create_invoice):
    consumer = AIOKafkaConsumer(
        topic, bootstrap_servers=bootstrap, group_id=group,
        auto_offset_reset="earliest", enable_auto_commit=False,
    )
    return InboxConsumerRunner(
        consumer=KafkaEventConsumer(consumer),
        transaction_provider=InboxTransaction(sessions),
        handler=handler,
        worker_id="billing-1", consumer_group=group,
        ack_strategy=AckStrategy.EXACTLY_ONCE_INBOX,
        exactly_once_commit_on_failed=False,
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
