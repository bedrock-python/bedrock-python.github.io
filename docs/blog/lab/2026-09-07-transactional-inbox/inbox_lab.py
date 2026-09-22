"""Real Kafka offsets, PostgreSQL rollback, and the limits of Inbox deduplication."""

import asyncio
import json
from pathlib import Path
import sys
from uuid import uuid4

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from sqlalchemy import delete

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "2026-09-07-exactly-once-effects"))
import event_flow as flow
from lab_support import (
    ProcessCrash, committed_offset, count, create_topics, database, infrastructure,
    invoice_count, process,
)
from models import InboxEventDB


async def send_order(producer, topic, order_id, event_id=None):
    headers = [("event_type", b"order.created")]
    if event_id is not None:
        headers.append(("event_id", str(event_id).encode()))
    await producer.send_and_wait(
        topic, value=json.dumps({"order_id": str(order_id)}).encode(), headers=headers,
    )


async def main(db_url, bootstrap):
    await create_topics(bootstrap, "inbox.rollback", "inbox.ack", "inbox.no-id")
    async with database(db_url) as sessions:
        async with AIOKafkaProducer(bootstrap_servers=bootstrap) as producer:
            first_order, next_order = uuid4(), uuid4()
            await send_order(producer, "inbox.rollback", first_order, uuid4())
            await send_order(producer, "inbox.rollback", next_order, uuid4())

            async def fail_after_insert(event, repo):
                await flow.create_invoice(event, repo)
                raise ProcessCrash("after invoice INSERT, before database commit")

            group = "billing-rollback"
            runner = flow.billing_runner(
                sessions, bootstrap, topic="inbox.rollback", group=group,
                handler=fail_after_insert,
            )
            try:
                async with asyncio.timeout(30):
                    await flow.run_billing(runner)
            except RuntimeError as error:
                assert "Retry message" in str(error), error
            else:
                raise AssertionError("The worker must stop on an uncommitted result")
            assert await invoice_count(sessions, first_order) == 0
            assert await invoice_count(sessions, next_order) == 0
            assert await count(sessions, InboxEventDB) == 0
            assert await committed_offset(bootstrap, "inbox.rollback", group) is None
            print("PASS handler failure: invoices=0, inbox=0, offset uncommitted; worker stopped")

            results = await process(flow.billing_runner(
                sessions, bootstrap, topic="inbox.rollback", group=group,
            ), 2)
            assert all(result.processed and result.committed for result in results)
            assert await invoice_count(sessions, first_order) == 1
            assert await invoice_count(sessions, next_order) == 1
            assert await committed_offset(bootstrap, "inbox.rollback", group) == 2
            print("PASS restart: failed record retried before the next record, invoices=2")

            order_id, event_id = uuid4(), uuid4()
            topic, group = "inbox.ack", "billing-ack"
            await send_order(producer, topic, order_id, event_id)

            class FailOffsetCommit(AIOKafkaConsumer):
                async def commit(self, offsets=None):
                    # This runs at the real adapter's acknowledgement boundary.
                    assert await invoice_count(sessions, order_id) == 1
                    assert await count(
                        sessions, InboxEventDB, InboxEventDB.consumer_group == group,
                        InboxEventDB.status == "completed",
                    ) == 1
                    raise ProcessCrash("database committed, Kafka offset not committed")

            runner = flow.InboxConsumerRunner(
                consumer=flow.KafkaEventConsumer(FailOffsetCommit(
                    topic, bootstrap_servers=bootstrap, group_id=group,
                    auto_offset_reset="earliest", enable_auto_commit=False,
                )),
                transaction_provider=flow.InboxTransaction(sessions),
                handler=flow.create_invoice, worker_id="billing-1", consumer_group=group,
                ack_strategy=flow.AckStrategy.EXACTLY_ONCE_INBOX,
                exactly_once_commit_on_failed=False,
            )
            try:
                await process(runner)
            except ProcessCrash:
                pass
            else:
                raise AssertionError("Injected offset failure was not reached")
            assert await committed_offset(bootstrap, topic, group) is None
            replay, = await process(flow.billing_runner(
                sessions, bootstrap, topic=topic, group=group,
            ))
            assert replay.duplicate and replay.committed and not replay.processed, replay
            assert await invoice_count(sessions, order_id) == 1
            assert await committed_offset(bootstrap, topic, group) == 1
            print("PASS failure after DB commit: replay=duplicate, invoices=1, offset=1")

            independent, = await process(flow.billing_runner(
                sessions, bootstrap, topic=topic, group="another-recipient",
            ))
            assert independent.processed and not independent.duplicate, independent
            assert await invoice_count(sessions, order_id) == 2
            print("PASS another consumer group: separate Inbox identity, handler runs again")

            async with sessions.begin() as session:
                await session.execute(delete(InboxEventDB).where(
                    InboxEventDB.consumer_group == group,
                    InboxEventDB.message_id == str(event_id),
                ))
            await send_order(producer, topic, order_id, event_id)
            after_cleanup, = await process(flow.billing_runner(
                sessions, bootstrap, topic=topic, group=group,
            ))
            assert after_cleanup.processed and not after_cleanup.duplicate, after_cleanup
            assert await invoice_count(sessions, order_id) == 3
            print("PASS Inbox cleanup + replay: old event executes again")

            order_id = uuid4()
            await send_order(producer, "inbox.no-id", order_id)
            await send_order(producer, "inbox.no-id", order_id)
            copies = await process(flow.billing_runner(
                sessions, bootstrap, topic="inbox.no-id", group="billing-no-id",
            ), 2)
            assert all(result.processed and not result.duplicate for result in copies)
            assert copies[0].message_id != copies[1].message_id
            assert await invoice_count(sessions, order_id) == 2
            print("PASS missing event_id: different Kafka offsets are different Inbox messages")


if __name__ == "__main__":
    with infrastructure() as (db_url, bootstrap, _):
        asyncio.run(main(db_url, bootstrap))
