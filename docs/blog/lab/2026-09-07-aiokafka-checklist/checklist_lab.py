"""Verify serialization, processing, offsets and redelivery against real Kafka."""

import asyncio
from importlib.metadata import version

from aiokafka import TopicPartition
from aiokafka_foundation_kit import check_kafka_health_async, consumer_lifecycle
from aiokafka_foundation_kit.contrib.models import BaseKafkaProducerSettings

import kafka_flow as flow
from lab_support import committed_offset, fetch_count, infrastructure, seed
from topic_probe import check_topic_creation


async def wait_assignment(consumer):
    async with asyncio.timeout(20):
        while not consumer.assignment():
            await asyncio.sleep(0.05)


async def main(bootstrap):
    print(f"aiokafka-foundation-kit={version('aiokafka-foundation-kit')}, "
          f"aiokafka={version('aiokafka')}", flush=True)
    await check_topic_creation(bootstrap)
    await flow.provision_delivery_topic(bootstrap, partitions=1)
    await seed(bootstrap, count=5)
    tp = TopicPartition(flow.TOPIC, 0)

    async with consumer_lifecycle(flow.tracking_settings(bootstrap, "inspect"),
                                  topics=(flow.TOPIC,)) as consumer:
        records = await fetch_count(consumer, 5)
        assert [record.value["revision"] for record in records] == list(range(5))
        assert {record.key for record in records} == {b"delivery-42"}
        assert {record.partition for record in records} == {0}
        # Establish the group's initial recovery point without acknowledging work.
        await consumer.commit({tp: 0})
        lag = await flow.read_lag(consumer)
        assert lag[tp] == {"position_lag": 0, "committed_lag": 5}, lag
        print("PASS JSON + byte key: revisions=0..4; position lag=0, committed lag=5", flush=True)

    view = flow.TrackingView()
    calls = []

    async def fail_on_third(message):
        if message.value["revision"] == 2:
            raise RuntimeError("tracking store unavailable")
        calls.append(message.offset)
        await view.process(message)

    group = "handler-failure"
    try:
        async with consumer_lifecycle(flow.tracking_settings(bootstrap, group),
                                      topics=(flow.TOPIC,)) as consumer:
            async with asyncio.timeout(25):
                await flow.consume_batches(consumer, fail_on_third, asyncio.Event())
    except RuntimeError as error:
        assert str(error) == "tracking store unavailable", error
    else:
        raise AssertionError("The handler failure must leave the loop")
    assert calls == [0, 1], calls
    assert await committed_offset(bootstrap, group) is None

    async with consumer_lifecycle(flow.tracking_settings(bootstrap, group),
                                  topics=(flow.TOPIC,)) as consumer:
        replay = await fetch_count(consumer, 5)
        assert [record.offset for record in replay] == list(range(5))
        for record in replay:
            await view.process(record)
        await view.process(replay[0])
    assert view.deliveries["delivery-42"]["revision"] == 4
    print("PASS handler failure: processed=2, no commit; restart replays offsets 0..4", flush=True)
    print("PASS tracking view: repeated or older revisions do not overwrite revision 4", flush=True)

    group, stop = "manual-commit", asyncio.Event()

    async def finish(message):
        if message.offset == 4:
            stop.set()

    async with consumer_lifecycle(flow.tracking_settings(bootstrap, group),
                                  topics=(flow.TOPIC,)) as consumer:
        async with asyncio.timeout(25):
            await flow.consume_batches(consumer, finish, stop)
    assert await committed_offset(bootstrap, group) == 5
    async with consumer_lifecycle(flow.tracking_settings(bootstrap, group),
                                  topics=(flow.TOPIC,)) as consumer:
        await wait_assignment(consumer)
        assert await consumer.position(tp) == 5
    print("PASS manual commit: completed offsets 0..4, stored offset=5, restart position=5", flush=True)

    group = "auto-commit"
    settings = flow.tracking_settings(bootstrap, group).model_copy(
        update={"enable_auto_commit": True},
    )
    async with consumer_lifecycle(settings, topics=(flow.TOPIC,)) as consumer:
        fetched = await fetch_count(consumer, 5)
        partial_view = flow.TrackingView()
        processed = []
        for record in fetched[:2]:
            await partial_view.process(record)
            processed.append(record.offset)
        # Wait for the real periodic commit while this consumer remains open.
        async with asyncio.timeout(12):
            while await consumer.committed(tp) != 5:
                await asyncio.sleep(0.1)
        assert processed == [0, 1]
        assert partial_view.deliveries["delivery-42"]["revision"] == 1
    async with consumer_lifecycle(settings, topics=(flow.TOPIC,)) as consumer:
        await wait_assignment(consumer)
        assert await consumer.position(tp) == 5
    print("PASS auto-commit: fetched=5, processed=2, stored offset=5; 3 records skipped on restart", flush=True)

    settings = BaseKafkaProducerSettings(bootstrap_servers=bootstrap)
    assert await check_kafka_health_async(settings, timeout_seconds=2)
    print("PASS connection probe: a running broker answers (no topic-write guarantee asserted)", flush=True)


if __name__ == "__main__":
    with infrastructure() as (bootstrap, _):
        asyncio.run(main(bootstrap))
