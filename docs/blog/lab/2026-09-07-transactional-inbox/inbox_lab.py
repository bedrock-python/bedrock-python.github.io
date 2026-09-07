"""The inbox side: what each ack strategy does when the handler fails, and what a redelivery does afterwards."""

import asyncio
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from sqlalchemy import Column, Integer, String, Table, func, select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from testcontainers.kafka import KafkaContainer
from testcontainers.postgres import PostgresContainer

from omni_box import AckStrategy, InboxConsumerRunner, InboxEvent, InboxEventRepository
from omni_box.core.protocols.transaction import InboxTransactionProviderProtocol
from omni_box.infra.brokers.kafka import KafkaEventConsumer
from omni_box.infra.storage.postgres import InboxEventDBBase, PostgresInboxRepository


class Base(DeclarativeBase):
    pass


class InboxEventDB(Base, InboxEventDBBase):
    pass


invoices = Table("invoices", Base.metadata, Column("id", Integer, primary_key=True), Column("order_id", String), Column("group", String))


async def main(db_url: str, bootstrap: str) -> None:
    engine = create_async_engine(db_url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    class TxProvider(InboxTransactionProviderProtocol):
        @asynccontextmanager
        async def transaction(self) -> AsyncIterator[InboxEventRepository]:
            async with session_factory() as session, session.begin():
                yield PostgresInboxRepository(session, model_class=InboxEventDB)

    producer = AIOKafkaProducer(bootstrap_servers=bootstrap)
    await producer.start()

    async def consumer_for(topic: str, group: str) -> KafkaEventConsumer:
        return KafkaEventConsumer(AIOKafkaConsumer(topic, bootstrap_servers=bootstrap, group_id=group, auto_offset_reset="earliest", enable_auto_commit=False))

    async def invoices_for(group: str) -> int:
        async with session_factory() as s:
            return (await s.execute(select(func.count()).select_from(invoices).where(invoices.c.group == group))).scalar_one()

    strategies = {
        "AT_MOST_ONCE": dict(ack_strategy=AckStrategy.AT_MOST_ONCE),
        "AT_LEAST_ONCE, commit ON_PERSIST": dict(ack_strategy=AckStrategy.AT_LEAST_ONCE),
        "AT_LEAST_ONCE, commit ON_SUCCESS": dict(ack_strategy=AckStrategy.AT_LEAST_ONCE, commit_offset_policy="on_success"),
        "EXACTLY_ONCE_INBOX (default)": dict(ack_strategy=AckStrategy.EXACTLY_ONCE_INBOX),
    }
    print("--- one message, a handler that fails on its first run; then a fresh consumer of the same group ---")
    for label, kwargs in strategies.items():
        group = f"billing-{uuid.uuid4().hex[:6]}"
        topic = f"orders.{group}"
        message_id = str(uuid.uuid4())
        await producer.send_and_wait(topic, key=b"o1", value=b'{"order_id": "o1"}', headers=[("message_id", message_id.encode()), ("event_type", b"order.created")])
        runs = 0

        async def create_invoice(event: InboxEvent, repo: InboxEventRepository, _group=group) -> None:
            nonlocal runs
            runs += 1
            await repo.session.execute(invoices.insert().values(order_id=event.payload["order_id"], group=_group))
            if runs == 1:
                raise RuntimeError("billing provider timed out")   # after the write, in the same transaction

        outcomes = []
        for attempt in (1, 2):
            runner = InboxConsumerRunner(consumer=await consumer_for(topic, group), transaction_provider=TxProvider(), handler=create_invoice,
                                         worker_id="billing-1", consumer_group=group, **kwargs)
            await runner.start()
            try:
                try:
                    r = await asyncio.wait_for(runner.process_one(), timeout=8.0)
                    outcomes.append(f"processed={r.processed} duplicate={r.duplicate} committed={r.committed}")
                except asyncio.TimeoutError:
                    outcomes.append("nothing delivered")
            finally:
                await runner.stop()
        print(f"  {label:<36} first: {outcomes[0]:<48} second consumer: {outcomes[1]:<48} handler ran={runs} invoices={await invoices_for(group)}")
    await producer.stop()
    await engine.dispose()


with PostgresContainer("postgres:17-alpine") as pg, KafkaContainer() as kafka:
    asyncio.run(main(pg.get_connection_url().replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1), kafka.get_bootstrap_server()))
