---
date: 2026-09-07
authors:
  - alex
categories:
  - Tutorials
tags:
  - aiokafka-foundation-kit
  - aiokafka
  - kafka
  - consumers
  - producers
  - asyncio
---

# The production checklist for aiokafka

aiokafka is a good client with defaults chosen for a library, not for your service, and the gap between the two is where the incidents live. This is the list I go through before a consumer or a producer ships, with each item measured against a Kafka container rather than quoted from the documentation: what the client refuses to be built with, what the serializers do to your keys, what a replacement consumer re-reads, what auto-commit commits, and what happens to a member whose batch takes too long.

<!-- more -->

The numbers come from [the post's lab](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-aiokafka-checklist), against Kafka in a container. Versions: aiokafka-foundation-kit 0.1.3, aiokafka 0.14.0, Python 3.13.

## The producer

**Build it inside a running loop.** aiokafka's constructor wants the running loop, so a client built at import time or in module scope fails before your service starts:

```text
    built at module scope, no running loop: RuntimeError: The object should be created within an
    async function or provide loop directly.
```

That is a good failure — loud, immediate, in the first line of the traceback. It also means the producer belongs to the application's lifecycle, started and stopped with it, not to a module global.

**`acks` and idempotence are one decision, not two.** An idempotent producer requires `acks=all`, and the client refuses anything else at construction:

```text
    enable_idempotence=True (default) with acks='1': ValueError: Invalid ACKS parameter
```

`acks=all` with idempotence is the right default for anything you would be upset to lose: the broker waits for the in-sync replicas, and the producer's sequence numbers deduplicate its own retries. `acks=1` buys latency at the price of losing acknowledged messages when a leader dies before its replicas caught up. If you choose it, choose it explicitly, with `enable_idempotence=False` next to it so the reader sees the trade.

**Compression needs a library you have not installed.** `gzip` works out of the box; the others do not:

```text
    compression_type='lz4' (no cramjam installed): RuntimeError: Compression library for lz4 not found
```

That, too, fails at construction rather than at the first send, which is what you want: `aiokafka[lz4]` in the dependencies, or `gzip` in the settings, decided before the deploy.

**Keys are bytes, values are whatever your serializer says.** With a JSON value serializer installed and no key serializer, a string key is a `TypeError`:

```text
    send(key='order-1', value={...}):  TypeError: a bytes-like object is required, not 'str'
    send(key=b'order-1', value={...}): accepted
```

The key matters more than the ergonomics suggest: it decides the partition, and the partition decides ordering. Events for one aggregate need one key, encoded once, in one place.

**And the deserializer is a contract with the whole topic.** A JSON deserializer meets one message that is not JSON, and the failure happens inside the fetcher, not in your handler:

```text
    a plain-text message on a JSON topic: 0 of 4 messages read, then JSONDecodeError
```

Zero of four. The consumer could not deliver even the messages before the bad one, because the decode happens as the batch is unpacked. A topic that might carry anything else — another team's producer, an old format, a tombstone — wants a deserializer that returns the raw bytes and a handler that decides, so one poisoned message cannot stop the partition.

## The consumer

**Nothing commits unless you say so.** The kit's consumer settings default `enable_auto_commit` to `False`, and a consumer that never commits re-reads everything on restart:

```text
    no commit at all                   first run read 10, the replacement read 10 again
    await consumer.commit() per batch  first run read 10, the replacement read 0 again
```

That is the design: commit after the work, so a crash replays rather than skips. Replays are handled by making the work idempotent, which is [the jobs and consumers post](2026-09-07-idempotency-for-jobs-and-consumers.md); skips are not handled by anything.

**Auto-commit commits what was fetched, not what was done.** This is the item worth reading twice:

```text
    fetched 10, processed 3 before the crash, the replacement got 0:
    7 messages nobody processed
```

Ten messages were fetched, three were processed, the process stopped, and the replacement got nothing, because the offsets for all ten had been committed. Seven messages were silently skipped. Auto-commit is not "commit less often", it is a different guarantee: at-most-once instead of at-least-once, and the messages it drops are dropped without an error anywhere.

There is a second edge in the same measurement. That run committed on `stop()`, which is aiokafka doing what auto-commit means — a graceful shutdown flushes the offsets it holds, processed or not. So the failure does not need a crash; an ordinary rolling deploy is enough.

**Processing time is bounded by `max_poll_interval_ms`.** A member that takes longer than the interval between polls is thrown out of the group. Two consumers in one group, an interval of six seconds, and one of them taking nine:

```text
    the slow member read [0, 2, 4, 6] and then slept 9 s; its commit ->
    CommitFailedError: Commit cannot be completed since the group has already rebalanced
    and assigned the partitions to another member.
    the other member read [0, 1, 2, 3, 4, 5, 6, 7]
    messages handled twice: [0, 2, 4, 6]
```

Every part of that is worth naming. The slow member's work was *done* and its commit was refused, so those offsets were never recorded. The partitions moved to the other member, which read the same four messages again. And four messages were handled twice by two different processes, at the same time, which is the exact condition every "why did this customer get two emails" investigation ends at.

The fix is not a bigger interval, or not only. It is `max_poll_records` small enough that a batch fits comfortably inside the interval, an interval sized from the p99 of your per-batch work, and, if the work is genuinely long, moving it off the poll loop entirely so the consumer's job is to hand it over and commit.

**A consumer needs a shutdown.** The kit's lifecycle subscribes and unsubscribes; the loop between them is yours, and so is the decision to finish the current batch, commit, and leave the group when a `SIGTERM` arrives. Leaving properly is what saves the replacement from waiting out a session timeout, which is [the Kafka shutdown post](2026-09-07-graceful-kafka-consumer-shutdown.md), measured at twenty-nine seconds against a third of a second.

## Topics and health

**Topic creation is a decision with two switches.** Passing topics is not enough on its own:

```text
    producer_lifecycle(topics=[...]) without auto_create_topics=True: created nothing
    with both arguments: created
```

Auto-creation from the application is convenient in development and a decision to make deliberately in production, where the partition count is a capacity choice and often somebody else's to make. What it must not be is a silent no-op you discover later, which is why the two arguments are separate.

**A refusal aborts the rest.** Creation is per topic, an existing topic is fine, and anything else stops the sequence:

```text
    ensure_topics_async([ok, replication_factor=3 on a one-broker cluster, ok]):
    InvalidReplicationFactorError: Replication factor: 3 larger than available brokers: 1
      the topic before it: created; the topic after it: missing
```

The first topic exists, the third does not. That is the right behaviour — a broker that refuses one topic will probably refuse the next — but it means startup topic creation is not atomic, and a service that half-created its topics needs to be safe to start again. Idempotent creation makes that true.

**The health probe is a probe, not a heartbeat.** It opens a real producer connection:

```text
    a cluster that answers:  True in 0.00 s
    a paused broker, timeout_seconds=2.0: False in 2.01 s
```

Two seconds is the timeout doing its job, and it is also two seconds of a readiness check hanging. Give it a timeout shorter than the probe's own, do not call it per request, and remember that "the cluster answers" is a liveness fact about Kafka, not a promise that your consumer group is healthy — consumer lag is a separate signal and usually the more useful one.

## The list, short

1. Build clients inside the loop, own them in the application's lifecycle.
2. `acks=all` with idempotence, or an explicit decision not to.
3. Compression library installed, or `gzip`.
4. Keys encoded to bytes in one place; the key is the ordering guarantee.
5. A deserializer that cannot be poisoned by one bad message.
6. `enable_auto_commit=False`, commit after the work.
7. `max_poll_records` and `max_poll_interval_ms` sized from the p99 of a batch.
8. A shutdown that finishes the batch, commits, and leaves the group.
9. Topics created deliberately, idempotently, and safe to re-run.
10. A health check with its own timeout, plus lag as the real signal.

## The pieces

Everything above is aiokafka's own behaviour; what [aiokafka-foundation-kit](https://bedrock-python.github.io/aiokafka-foundation-kit/) adds is the settings object those knobs live in, the lifecycle that starts and stops the client, idempotent topic creation and a health probe. It deliberately does not wrap the client: once the lifecycle yields, you are holding an `AIOKafkaProducer` or an `AIOKafkaConsumer`, and every send, poll and commit above is aiokafka's API, which is why this checklist is about aiokafka and not about a wrapper.
