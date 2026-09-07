"""Every item of the aiokafka production checklist, measured against one Kafka container.

Each section prints what a setting does when it is wrong, and what it does when it is right:
what the producer refuses to be built with, what a consumer redelivers, what auto-commit loses,
what happens when processing outlives max_poll_interval_ms, what a health probe costs and what
topic creation does with a replication factor the cluster cannot honour.
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
import time
import uuid
from importlib.metadata import version

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import CommitFailedError, KafkaError
from testcontainers.kafka import KafkaContainer

from aiokafka_foundation_kit import (
    TopicConfig,
    check_kafka_health_async,
    consumer_lifecycle,
    create_async_kafka_consumer,
    create_async_kafka_producer,
    ensure_topics_async,
    producer_lifecycle,
)
from aiokafka_foundation_kit.contrib.models import (
    BaseKafkaConsumerSettings,
    BaseKafkaProducerSettings,
)

MESSAGES = 10


def log(msg: str) -> None:
    print(msg, flush=True)


def outcome(fn, *args, **kwargs) -> str:
    """Run something that is expected to refuse, and report how it refused."""
    try:
        fn(*args, **kwargs)
    except Exception as error:  # noqa: BLE001 - the lab reports whatever comes out
        return f"{type(error).__name__}: {error}"
    return "accepted"


async def aoutcome(coro) -> str:
    try:
        await coro
    except Exception as error:  # noqa: BLE001 - the lab reports whatever comes out
        return f"{type(error).__name__}: {error}"
    return "accepted"


def consumer_settings(bootstrap: str, group: str, **kw) -> BaseKafkaConsumerSettings:
    return BaseKafkaConsumerSettings(bootstrap_servers=bootstrap, group_id=group, **kw)


async def seed(bootstrap: str, topic: str, n: int = MESSAGES) -> None:
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap)
    await producer.start()
    try:
        for i in range(n):
            await producer.send_and_wait(topic, value=json.dumps({"n": i}).encode())
    finally:
        await producer.stop()


async def drain(consumer: AIOKafkaConsumer, expected: int, timeout: float = 8.0) -> list[int]:
    """Read up to `expected` messages, or until the topic goes quiet."""
    seen: list[int] = []
    deadline = time.monotonic() + timeout
    while len(seen) < expected and time.monotonic() < deadline:
        batch = await consumer.getmany(timeout_ms=500, max_records=expected - len(seen))
        for records in batch.values():
            seen += [r.value["n"] for r in records]
    return seen


# --- 1. what the producer refuses to be built with -------------------------------------------


async def section_construction(bootstrap: str) -> None:
    log("--- 1. settings the client refuses at construction, not at the first send")
    base = dict(bootstrap_servers=bootstrap)
    log(f"    enable_idempotence=True (default) with acks='1': "
        f"{outcome(lambda: create_async_kafka_producer(BaseKafkaProducerSettings(**base, acks='1')))}")
    log(f"    enable_idempotence=False with acks='1':          "
        f"{outcome(lambda: create_async_kafka_producer(BaseKafkaProducerSettings(**base, acks='1', enable_idempotence=False)))}")
    log(f"    compression_type='lz4' (no cramjam installed):    "
        f"{outcome(lambda: create_async_kafka_producer(BaseKafkaProducerSettings(**base, compression_type='lz4')))}")
    log(f"    compression_type='gzip':                         "
        f"{outcome(lambda: create_async_kafka_producer(BaseKafkaProducerSettings(**base, compression_type='gzip')))}")

    script = (
        "from aiokafka_foundation_kit import create_async_kafka_producer\n"
        "from aiokafka_foundation_kit.contrib.models import BaseKafkaProducerSettings\n"
        f"create_async_kafka_producer(BaseKafkaProducerSettings(bootstrap_servers='{bootstrap}'))\n"
    )
    proc = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True)
    last = proc.stderr.strip().splitlines()[-1] if proc.stderr.strip() else "accepted"
    log(f"    built at module scope, no running loop:          {last}")


# --- 2. what the producer does with a key and a value ----------------------------------------


async def section_serialization(bootstrap: str) -> None:
    log("--- 2. values are JSON, keys are bytes")
    topic = f"ser-{uuid.uuid4().hex[:6]}"
    settings = BaseKafkaProducerSettings(bootstrap_servers=bootstrap)
    async with producer_lifecycle(settings) as producer:
        log(f"    send(value={{'id': 42}}):            {await aoutcome(producer.send_and_wait(topic, {'id': 42}))}")
        log(f"    send(key='order-1', value={{...}}):  "
            f"{await aoutcome(producer.send_and_wait(topic, {'id': 42}, key='order-1'))}")
        log(f"    send(key=b'order-1', value={{...}}): "
            f"{await aoutcome(producer.send_and_wait(topic, {'id': 42}, key=b'order-1'))}")

    raw = AIOKafkaProducer(bootstrap_servers=bootstrap)
    await raw.start()
    await raw.send_and_wait(topic, value=b"not json at all")
    await raw.stop()

    consumer = create_async_kafka_consumer(
        consumer_settings(bootstrap, f"ser-{uuid.uuid4().hex[:6]}", auto_offset_reset="earliest"), (topic,)
    )
    await consumer.start()
    try:
        seen, error = 0, "none"
        try:
            deadline = time.monotonic() + 6
            while seen < 4 and time.monotonic() < deadline:
                batch = await consumer.getmany(timeout_ms=500)
                seen += sum(len(v) for v in batch.values())
        except Exception as exc:  # noqa: BLE001 - the lab reports whatever comes out
            error = f"{type(exc).__name__}: {exc}"
        log(f"    a plain-text message on a JSON topic: {seen} of 4 messages read, then {error}")
    finally:
        await consumer.stop()


# --- 3. commits ------------------------------------------------------------------------------


async def section_commits(bootstrap: str) -> None:
    log(f"--- 3. commits: {MESSAGES} messages, a consumer that stops, and its replacement")
    for label, commit, auto in (
        ("no commit at all", False, False),
        ("await consumer.commit() per batch", True, False),
        ("enable_auto_commit=True", False, True),
    ):
        group = f"orders-{uuid.uuid4().hex[:6]}"
        topic = f"orders-{group}"
        await seed(bootstrap, topic)
        settings = consumer_settings(bootstrap, group, auto_offset_reset="earliest", enable_auto_commit=auto)
        async with consumer_lifecycle(settings, topics=(topic,)) as consumer:
            first = await drain(consumer, MESSAGES)
            if commit:
                await consumer.commit()
        async with consumer_lifecycle(settings, topics=(topic,)) as consumer:
            second = await drain(consumer, MESSAGES, timeout=5.0)
        log(f"    {label:<38} first run read {len(first)}, the replacement read {len(second)} again")


async def section_autocommit_loss(bootstrap: str) -> None:
    log("--- 4. what auto-commit commits: offsets that were fetched, not work that was done")
    log("    (BaseKafkaConsumerSettings has no auto_commit_interval_ms field, so it is aiokafka's 5 s default)")
    group = f"loss-{uuid.uuid4().hex[:6]}"
    topic = f"loss-{group}"
    await seed(bootstrap, topic)
    settings = consumer_settings(bootstrap, group, auto_offset_reset="earliest", enable_auto_commit=True)
    processed: list[int] = []
    async with consumer_lifecycle(settings, topics=(topic,)) as consumer:
        batch = await consumer.getmany(timeout_ms=3000, max_records=MESSAGES)
        fetched = sum(len(v) for v in batch.values())
        for records in batch.values():
            for record in records[:3]:  # the process crashes after three of them
                await asyncio.sleep(0.3)
                processed.append(record.value["n"])
    async with consumer_lifecycle(settings, topics=(topic,)) as consumer:
        after = await drain(consumer, MESSAGES, timeout=5.0)
    log(f"    fetched {fetched}, processed {len(processed)} before the crash, "
        f"the replacement got {len(after)}: {MESSAGES - len(processed) - len(after)} messages nobody processed")


async def section_poll_interval(bootstrap: str) -> None:
    log("--- 5. work that outlives max_poll_interval_ms, in a group with a second member")
    group = f"slow-{uuid.uuid4().hex[:6]}"
    topic = f"slow-{group}"
    settings_producer = BaseKafkaProducerSettings(bootstrap_servers=bootstrap)
    await ensure_topics_async([TopicConfig(name=topic, num_partitions=2, replication_factor=1)], settings_producer)
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap)
    await producer.start()
    for i in range(8):
        await producer.send_and_wait(topic, value=json.dumps({"n": i}).encode(), partition=i % 2)
    await producer.stop()

    settings = consumer_settings(
        bootstrap, group, auto_offset_reset="earliest",
        max_poll_interval_ms=6000, session_timeout_ms=6000, heartbeat_interval_ms=1000,
    )
    slow_read: list[int] = []
    fast_read: list[int] = []
    commit_result = {"value": "not attempted"}

    async def slow_member() -> None:
        async with consumer_lifecycle(settings, topics=(topic,)) as consumer:
            batch = await consumer.getmany(timeout_ms=6000, max_records=4)
            for records in batch.values():
                slow_read.extend(r.value["n"] for r in records)
            await asyncio.sleep(9)  # 9 s of "work" on a 6 s poll interval
            try:
                await consumer.commit()
                commit_result["value"] = "committed"
            except CommitFailedError as error:
                commit_result["value"] = f"CommitFailedError: {str(error).splitlines()[0]}"
            except KafkaError as error:
                commit_result["value"] = f"{type(error).__name__}: {error}"

    async def fast_member() -> None:
        deadline = time.monotonic() + 20
        async with consumer_lifecycle(settings, topics=(topic,)) as consumer:
            while time.monotonic() < deadline:
                batch = await consumer.getmany(timeout_ms=1000, max_records=4)
                for records in batch.values():
                    fast_read.extend(r.value["n"] for r in records)
                    await consumer.commit()

    await asyncio.gather(slow_member(), fast_member())
    log(f"    the slow member read {sorted(slow_read)} and then slept 9 s; its commit -> {commit_result['value']}")
    log(f"    the other member read {sorted(fast_read)}")
    log(f"    messages handled twice: {sorted(set(slow_read) & set(fast_read))}")


# --- 6. topics and health --------------------------------------------------------------------


async def section_topics(bootstrap: str) -> None:
    log("--- 6. creating topics")
    settings = BaseKafkaProducerSettings(bootstrap_servers=bootstrap)
    name = f"topics-{uuid.uuid4().hex[:6]}"
    async with producer_lifecycle(settings, topics=[TopicConfig(name=name, num_partitions=3, replication_factor=1)]) as p:
        pass
    log(f"    producer_lifecycle(topics=[...]) without auto_create_topics=True: "
        f"{'created' if await topic_exists(bootstrap, name) else 'created nothing'}")
    name2 = f"topics-{uuid.uuid4().hex[:6]}"
    async with producer_lifecycle(
        settings, topics=[TopicConfig(name=name2, num_partitions=3, replication_factor=1)], auto_create_topics=True
    ) as p:
        pass
    log(f"    with both arguments: {'created' if await topic_exists(bootstrap, name2) else 'created nothing'}")

    good = TopicConfig(name=f"ok-{uuid.uuid4().hex[:6]}", num_partitions=1, replication_factor=1)
    bad = TopicConfig(name=f"rf3-{uuid.uuid4().hex[:6]}", num_partitions=1, replication_factor=3)
    after = TopicConfig(name=f"after-{uuid.uuid4().hex[:6]}", num_partitions=1, replication_factor=1)
    result = await aoutcome(ensure_topics_async([good, bad, after], settings))
    log(f"    ensure_topics_async([ok, replication_factor=3 on a one-broker cluster, ok]): {result}")
    log(f"      the topic before it: {'created' if await topic_exists(bootstrap, good.name) else 'missing'}; "
        f"the topic after it: {'created' if await topic_exists(bootstrap, after.name) else 'missing'}")


async def topic_exists(bootstrap: str, name: str) -> bool:
    consumer = AIOKafkaConsumer(bootstrap_servers=bootstrap)
    await consumer.start()
    try:
        return name in await consumer.topics()
    finally:
        await consumer.stop()


async def section_health(bootstrap: str, container) -> None:
    log("--- 7. the health probe")
    settings = BaseKafkaProducerSettings(bootstrap_servers=bootstrap)
    started = time.perf_counter()
    ok = await check_kafka_health_async(settings, timeout_seconds=2.0)
    log(f"    a cluster that answers:  {ok} in {time.perf_counter() - started:.2f} s")

    subprocess.run(["docker", "pause", container.get_wrapped_container().id], capture_output=True)
    try:
        started = time.perf_counter()
        ok = await check_kafka_health_async(settings, timeout_seconds=2.0)
        log(f"    a paused broker, timeout_seconds=2.0: {ok} in {time.perf_counter() - started:.2f} s")
    finally:
        subprocess.run(["docker", "unpause", container.get_wrapped_container().id], capture_output=True)
    await asyncio.sleep(3)


async def main() -> None:
    log(f"aiokafka-foundation-kit {version('aiokafka-foundation-kit')}, aiokafka {version('aiokafka')}")
    with KafkaContainer() as kafka:
        bootstrap = kafka.get_bootstrap_server()
        await section_construction(bootstrap)
        await section_serialization(bootstrap)
        await section_commits(bootstrap)
        await section_autocommit_loss(bootstrap)
        await section_poll_interval(bootstrap)
        await section_topics(bootstrap)
        await section_health(bootstrap, kafka)


if __name__ == "__main__":
    asyncio.run(main())
