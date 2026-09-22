"""Prove the producer failure windows and deduplicate two real Kafka records."""

import asyncio
from uuid import uuid4

from aiokafka import AIOKafkaProducer
from sqlalchemy import select

import event_flow as flow
from lab_support import (
    ProcessCrash, count, create_topics, database, infrastructure, invoice_count,
    process, records,
)
from models import InboxEventDB, Order, OutboxEventDB


async def main(db_url, bootstrap):
    await create_topics(bootstrap, "orders.commit-first", "orders.publish-first", "orders.created")
    async with database(db_url) as sessions:
        async with AIOKafkaProducer(bootstrap_servers=bootstrap) as producer:
            order_id = uuid4()
            async with sessions.begin() as session:
                session.add(Order(id=order_id))
            try:
                raise ProcessCrash("after order commit, before publish")
                # The send is never reached.
            except ProcessCrash:
                pass
            assert await count(sessions, Order, Order.id == order_id) == 1
            assert await records(bootstrap, "orders.commit-first") == []
            print("PASS commit before publish: orders=1, Kafka records=0")

            order_id = uuid4()
            await producer.send_and_wait(
                "orders.publish-first", value=b'{"event_type":"order.created"}',
            )
            try:
                async with sessions.begin() as session:
                    session.add(Order(id=order_id))
                    await session.flush()
                    raise ProcessCrash("publish succeeded, order transaction failed")
            except ProcessCrash:
                pass
            assert await count(sessions, Order, Order.id == order_id) == 0
            assert len(await records(bootstrap, "orders.publish-first")) == 1
            print("PASS publish before commit: orders=0, Kafka records=1")

        order_id = uuid4()
        try:
            async with sessions.begin() as session:
                await flow.record_order(session, order_id)
                raise ProcessCrash("before order + outbox commit")
        except ProcessCrash:
            pass
        assert await count(sessions, Order, Order.id == order_id) == 0
        assert await count(sessions, OutboxEventDB) == 0
        print("PASS shared transaction rollback: orders=0, outbox=0")

        event_id = await flow.place_order(sessions, order_id)
        assert await count(sessions, Order, Order.id == order_id) == 1
        assert await count(sessions, OutboxEventDB) == 1

        async with flow.kafka_publisher(bootstrap) as broker:
            try:
                async with sessions.begin() as session:
                    result = await flow.relay_batch(session, broker)
                    assert result.processed_event_ids == [event_id]
                    raise ProcessCrash("Kafka acknowledged, outbox commit did not happen")
            except ProcessCrash:
                pass
            async with sessions() as session:
                status = await session.scalar(select(OutboxEventDB.status))
            assert status == "pending", status
            assert len(await records(bootstrap, "orders.created")) == 1

            result = await flow.relay_once(sessions, broker)
            assert result.processed_event_ids == [event_id]

        copies = await records(bootstrap, "orders.created")
        assert len(copies) == 2, copies
        assert {dict(record.headers)["event_id"] for record in copies} == {
            str(event_id).encode()
        }
        assert len({record.offset for record in copies}) == 2
        async with sessions() as session:
            assert await session.scalar(select(OutboxEventDB.status)) == "completed"
        print("PASS relay restart: Kafka records=2, distinct event_id=1, outbox=completed")

        first, second = await process(flow.billing_runner(sessions, bootstrap), 2)
        assert first.processed and first.committed and not first.duplicate, first
        assert second.duplicate and second.committed and not second.processed, second
        assert await invoice_count(sessions, order_id) == 1
        assert await count(sessions, InboxEventDB) == 1
        print("PASS Inbox: deliveries=2, invoices=1, inbox rows=1")


if __name__ == "__main__":
    with infrastructure() as (db_url, bootstrap, _):
        asyncio.run(main(db_url, bootstrap))
