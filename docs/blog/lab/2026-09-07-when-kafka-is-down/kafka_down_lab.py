"""Pause a real Kafka broker, retain pending events, then drain the backlog."""

import asyncio
from pathlib import Path
import sys
from uuid import uuid4

from sqlalchemy import select, text

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "2026-09-07-exactly-once-effects"))
import event_flow as flow
from lab_support import count, create_topics, database, infrastructure, records
from models import Order, OutboxEventDB


BACKLOG_SQL = """
SELECT status, count(*) AS events, max(attempts_made) AS attempts
FROM outbox_events
WHERE status <> 'completed'
GROUP BY status;
""".strip()


async def main(db_url, bootstrap, kafka):
    await create_topics(bootstrap, "orders.created")
    async with database(db_url) as sessions:
        async with flow.kafka_publisher(bootstrap) as broker:
            # Publish once so that topic metadata and the producer connection are ready.
            warmup_id = await flow.place_order(sessions, uuid4())
            sent = await flow.relay_once(sessions, broker)
            assert sent.processed_event_ids == [warmup_id]

            container = kafka.get_wrapped_container()
            await asyncio.to_thread(container.pause)
            try:
                event_ids = {await flow.place_order(sessions, uuid4()) for _ in range(3)}
                assert await count(sessions, Order) == 4
                for cycle in range(3):
                    result = await flow.relay_once(sessions, broker)
                    assert not result.processed_event_ids, result
                    async with sessions() as session:
                        rows = (await session.execute(text(BACKLOG_SQL))).all()
                    assert rows == [("pending", 3, 0)], rows
                    print(f"PASS paused cycle {cycle + 1}: orders=4, pending=3, attempts=0")
                    await asyncio.sleep(1.1)
            finally:
                # Unpause before the producer's shutdown waits for outstanding sends.
                await asyncio.to_thread(container.unpause)

            async with asyncio.timeout(45):
                while True:
                    await flow.relay_once(sessions, broker)
                    pending = await count(
                        sessions, OutboxEventDB, OutboxEventDB.status != "completed",
                    )
                    if pending == 0:
                        break
                    await asyncio.sleep(1)

            async with sessions() as session:
                rows = (await session.execute(select(
                    OutboxEventDB.id, OutboxEventDB.status, OutboxEventDB.attempts_made,
                ))).all()
            assert len(rows) == 4
            assert all(row.status == "completed" and row.attempts_made == 0 for row in rows)
            # A timed-out send may still reach Kafka. Assert no missing event IDs,
            # not an exact record count; Inbox handles any repeated publication.
            published_ids = {
                dict(record.headers)["event_id"].decode()
                for record in await records(bootstrap, "orders.created")
            }
            assert published_ids == {str(event_id) for event_id in event_ids | {warmup_id}}
            print("PASS recovery: all 4 event IDs delivered, pending=0, attempts=0")


if __name__ == "__main__":
    with infrastructure() as (db_url, bootstrap, kafka):
        asyncio.run(main(db_url, bootstrap, kafka))
