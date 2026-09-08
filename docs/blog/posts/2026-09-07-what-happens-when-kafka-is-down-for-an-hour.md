---
date: 2026-09-07
authors:
  - alex
categories:
  - Design
tags:
  - omni-box
  - kafka
  - outbox
  - postgresql
  - reliability
  - asyncio
---

# What happens when Kafka is down for an hour?

<div class="bdr-post__hero" data-bdr-post="2026-09-07-what-happens-when-kafka-is-down-for-an-hour" role="img" aria-label="An hour of outage: the direct path loses events, the durable one does not" markdown="0"></div>

Not "is down for a second, and the retry catches it". An hour: a broker rolling badly, a disk full on every node, a network partition between availability zones. Every service that publishes events has an answer to this, and most of them are "we lose them and nobody notices until a customer asks where their order went". I paused a Kafka container and put twenty events through two designs. The request path was told three times that a send had failed, and one of those three was delivered anyway. The outbox lost nothing and spent no retries.

<!-- more -->

The numbers come from [the post's lab](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-when-kafka-is-down), with PostgreSQL 17 and Kafka in containers and the outage played by pausing the broker's container, so it neither answers nor refuses. Versions: omni-box 0.2.1, aiokafka 0.14.0, Python 3.13.

## Publishing from the request path

The default design is a `send_and_wait` where the event happens. Here it is against a broker that is gone, with a producer that was connected before the outage started:

```text
  request 1: RequestTimedOutError: [Error 7] RequestTimedOutError after 2.0 s
  request 2: NodeNotReadyError: Attempt to send a request to node which is not ready after 4.0 s
  request 3: NodeNotReadyError: Attempt to send a request to node which is not ready after 4.0 s
```

Three things went wrong there, and only one of them is obvious.

**The caller waited.** Two to four seconds per request, on a request timeout of two seconds, which is already aggressive; the default is forty. An outage in the broker became latency in the API, and if the handler holds a database transaction across that send, it became a database problem too.

**The events are gone.** The handler has a choice of bad options: fail the request, so the customer's order does not exist because the notification could not be sent; or swallow the error and return success, so the order exists and nothing downstream will ever hear about it.

**And one of them was not gone.** After the broker came back:

```text
  messages on the topic: 22 (1 of them from the request path)
```

Twenty from the outbox, one warm-up message, and one of the three sends the caller was told had *failed*. The producer had it buffered and delivered it when the connection came back. So the request path's error is not an answer: some of the events it reported as failed arrive, and some do not, and the handler has no way to tell which. Any compensating logic built on that error — mark the order as not-notified, retry it later from the caller — will double-send an unknown subset.

## The outbox during the outage

The other design writes the event as a row in the same transaction as the business change, and a relay publishes it later. Same twenty events, same paused broker, the relay ticking every five seconds:

```text
  cycle 1 at   5.0 s: {'pending/attempts=0': 20}
  cycle 2 at  10.0 s: {'pending/attempts=0': 20}
  ...
  cycle 7 at  35.2 s: {'pending/attempts=0': 20}
```

Nothing moves, which is exactly right. The rows stay `pending`, and, importantly, `attempts` stays at zero across every cycle.

That second number is the design decision the outage tests. An outbox row usually carries an attempt budget, so that a message the broker will *never* accept — a payload above the message size limit, a topic that does not exist and cannot be created — stops being retried forever and is parked for a human. A broker outage is not that. If the outage spends the budget, then after enough cycles every row in the outbox is `failed`, and when Kafka comes back the relay publishes nothing at all: the backlog has to be requeued by hand, and until somebody notices, the queue is silently empty.

So the rule is: **the attempt budget belongs to the row, not to the outage.** A failure that is clearly about the broker's availability leaves the budget alone and, better still, stops the batch immediately rather than trying the other ninety-nine rows against a broker that is not there. That is why the seven cycles above took thirty-five seconds and not much longer: each cycle is one probe, not twenty timeouts.

When the broker comes back, one cycle drains the backlog:

```text
  next relay cycle: {'completed/attempts=0': 20}; messages on the topic: 22
```

Twenty rows, twenty messages, in order, no requeue, nobody woken up.

## What an hour actually costs you

The outbox turns a lost-events problem into a backlog problem, and a backlog has arithmetic worth doing before the incident rather than during it.

**Table growth.** At a hundred events a second, an hour is 360,000 rows, and each row carries its payload. That is fine for PostgreSQL and it is not fine to leave there forever: completed rows need a retention policy, and the table needs an index that supports the relay's query without a sequential scan over the backlog.

**Catch-up rate.** The relay drains at batch size times cycles per second. If that number is not comfortably above your event rate, the outbox never catches up after an outage, and the backlog is permanent. A batch of a hundred and a cycle every second is 360,000 events in an hour of catch-up: exactly break-even with the hour you lost, which is not enough. Two or three times the steady rate is the number to aim for.

**The thundering backlog.** An hour of events lands on the consumers in a few minutes. Anything downstream with a rate limit — an email provider, a payment gateway, a partner's API — sees a spike it has never seen in normal traffic. The consumer side needs to be able to be slow without falling over, which is a different property from being fast.

**Ordering.** Ordering holds per partition, so the partition key decides what stays in order through the drain. Per aggregate is almost always the right key: events for one order arrive in the order they happened, and different orders may interleave.

## What it does not solve

The outbox gives you at-least-once publishing, and at-least-once means duplicates. A relay that publishes a row and dies before marking it completed will publish it again. So the topic can contain the same event twice, and every consumer has to be able to handle that, which is [the inbox](2026-09-07-transactional-inbox.md) and [idempotent effects](2026-09-07-exactly-once-effects.md). The outbox moves the problem from "did this event ever get sent" to "this event may arrive twice", and the second problem has a known answer.

It also does not make the relay's own failure free. The relay is a process that has to be running, and its lag is the thing to alert on: not "is the relay up", but "what is the age of the oldest pending row". That number is the honest health of the whole arrangement, and it goes red during the outage exactly as it should — the events are late, and lateness is what you traded loss for.

## The pieces

The outbox above is [omni-box](https://bedrock-python.github.io/omni-box/): a table, a repository that writes rows in your transaction, a relay that claims a batch and publishes it, an attempt budget per row and a broker publisher that recognises "the broker is unreachable" as a different thing from "this message is bad". The consumer half of the pattern, the inbox, is in the same library.

Twenty events, an hour of nothing, and one cycle to drain. The alternative was three errors, one of which was a lie.
