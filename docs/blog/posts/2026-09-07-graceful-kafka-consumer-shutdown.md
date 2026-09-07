---
date: 2026-09-07
authors:
  - alex
categories:
  - Tutorials
tags:
  - aiokafka-foundation-kit
  - servicewright
  - kafka
  - graceful-shutdown
  - kubernetes
  - workers
---

# Graceful Kafka consumer shutdown in Kubernetes

A Kafka consumer under Kubernetes is redeployed several times a day, and every redeploy sends it `SIGTERM` in the middle of a batch. What it does in the next second decides two things: whether the messages it was holding get processed twice, and how long its replacement waits before it can process anything. I built the consumer most codebases run, a loop with a commit at the end of each batch and a signal handler that exits, and measured a rollout against it. The replacement waited thirty seconds for its first message, and three messages were handled twice. Then the same loop under a lifecycle that finishes the batch, commits and leaves the group: zero duplicates, and the replacement was working within a third of a second.

<!-- more -->

The numbers come from [the post's lab](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-kafka-consumer-shutdown), with Kafka in a container and a driver that plays the rollout. Versions: aiokafka-foundation-kit 0.1.2, aiokafka 0.14.0, servicewright 0.10.0, Python 3.13.

## What the group does when a member disappears

A consumer group's partitions are assigned to its members, and reassignment, the rebalance, happens when a member joins or leaves. A member that *leaves* tells the coordinator so and the rebalance starts at once. A member that *dies* tells nobody; the coordinator notices when the member's heartbeats stop, after the session timeout, and only then rebalances. Until it does, the dead member's partitions belong to a process that no longer exists, and the replacement that joined the group a second after the rollout sits with no partitions, receiving nothing.

That is the first cost of a bad shutdown, and it is paid by the new pod, which is why it shows up as "the deploy went fine but the queue lag spiked for half a minute".

The second cost is the offsets. A consumer that commits after each batch and dies in the middle of one has processed messages it has not committed. The replacement starts from the last committed offset and processes them again. For a handler that is idempotent that is a waste; for one that is not, it is a duplicate effect, which is the subject of [the inbox post](2026-09-07-transactional-inbox.md) and [the jobs post](2026-09-07-idempotency-for-jobs-and-consumers.md).

## Measured: the consumer that exits

The loop fetches up to five messages, processes each for two hundred milliseconds, and commits after the batch. `SIGTERM` is handled the way it usually is, by exiting:

```python
signal.signal(signal.SIGTERM, lambda *_: (log("SIGTERM: exiting now"), os._exit(143)))

async with consumer_lifecycle(settings(), topics=(TOPIC,)) as consumer:
    while True:
        batches = await consumer.getmany(timeout_ms=500, max_records=5)
        for records in batches.values():
            for message in records:
                await process(message)
        if batches:
            await consumer.commit()
```

The driver sends `SIGTERM` after the eighth message, then starts a replacement in the same group:

```text
   1.20 s  committed
   1.40 s  processed 5
   1.60 s  processed 6
   1.80 s  processed 7
   1.80 s  SIGTERM: exiting now
   first instance:  processed 8 messages, exited with 143 0.00 s after the signal
   second instance: first message 29.61 s after start, processed 22; processed twice: [5, 6, 7]
```

The exit was instant, which looks like the point of a signal handler and is the opposite. The process left without telling the group, so the group waited the session timeout for heartbeats that were never coming before it gave the partitions to the replacement: twenty-nine seconds during which the new pod was up, healthy and idle. And the batch in flight, messages five to seven, had been processed and not committed, so the replacement processed them again.

## The protocol

The four steps are the same as for [an HTTP server](2026-09-07-graceful-shutdown-is-a-protocol.md), with different verbs. Stop taking new work: do not fetch another batch. Finish the work in hand: the batch that was fetched is processed to the end, because abandoning it means reprocessing it. Commit what was finished, so the replacement starts after it. Leave the group cleanly, so the rebalance happens now and not at the session timeout. Then close the producer and the pools, and exit zero, all of it inside `terminationGracePeriodSeconds`.

The loop that does that is the same loop with the signal turned into an event, checked between batches and not inside one:

```python
async def consume(scope, stop: asyncio.Event) -> None:
    async with consumer_lifecycle(settings(), topics=(TOPIC,)) as consumer:   # stop() on exit: the group is left cleanly
        while not stop.is_set():
            batches = await consumer.getmany(timeout_ms=500, max_records=5)
            for records in batches.values():
                for message in records:                                       # the batch in flight is finished, stop or not
                    await process(message)
            if batches:
                await consumer.commit()
        log("stop seen between batches: leaving")
```

The signal handler is the runtime's, the event is what it sets, and the consumer's `stop()` runs when the lifecycle block exits, which is what sends the leave-group request. The same rollout:

```text
   1.84 s  processed 8
   2.04 s  processed 9
   2.05 s  committed
   2.05 s  stop seen between batches: leaving
   first instance:  processed 10 messages, exited with 0 0.45 s after the signal
   second instance: first message 0.31 s after start, processed 20; processed twice: []
```

The signal arrived during the batch that held messages six to ten; the batch finished, the commit landed, the loop saw the event, the consumer left the group, and the process exited zero within half a second. The replacement joined a group that already knew the old member was gone and had its first message three tenths of a second after starting. Ten plus twenty is thirty, the size of the topic, and nothing was processed twice.

## The numbers to set

The batch bounds the shutdown: five messages at two hundred milliseconds is one second of work the shutdown has to wait for, and the grace budget has to cover it. `max_records` times the slowest message is the drain time; `drain_grace_seconds` has to exceed it; `terminationGracePeriodSeconds` has to exceed that plus the cleanup, which is the arithmetic from the shutdown post with the batch as the in-flight request.

The session timeout is the other side of the same number. It is how long the group tolerates a silent member before rebalancing, and it is why a consumer that dies costs the group that long. It cannot be made small without making the group rebalance on every garbage-collection pause, so the answer is not a short session timeout; it is leaving properly.

And `enable_auto_commit` stays off. Auto-commit commits on a timer, regardless of whether the messages were processed, which turns a crash into skipped messages rather than replayed ones; committing after the batch is what makes a crash replay, and replaying is the failure mode the inbox exists to handle.

## The pieces

The consumer is a plain `AIOKafkaConsumer` built from a settings object by [aiokafka-foundation-kit](https://bedrock-python.github.io/aiokafka-foundation-kit/), whose `consumer_lifecycle` owns the start and the stop and nothing in between; the loop is yours. The stop event, the drain budget and the signal handling belong to [servicewright](https://bedrock-python.github.io/servicewright/), where the consumer is one daemon entrypoint among whatever else the service runs, and gets the same drain ordering an HTTP server does.

The point was the two second-instance lines. Twenty-nine seconds and three duplicates, or a third of a second and none.
