---
date: 2026-09-07
authors:
  - alex
categories:
  - Design
tags:
  - omni-box
  - idempotency-kit
  - kafka
  - outbox
  - inbox
  - exactly-once
  - postgresql
---

# Exactly-once is a lie; exactly-once effects are not

<div class="bdr-post__hero" data-bdr-post="2026-09-07-exactly-once-effects" role="img" aria-label="Two systems, two commits, no shared transaction: close each window one at a time" markdown="0"></div>

Kafka cannot make your database update exactly once. Nothing can, because the database and the broker are two systems with two commits and no transaction that spans them, and every guarantee a broker advertises stops at its own edge. What you can have is something better named and just as useful: every effect happens once, however many times the message that caused it is delivered. This post maps every window in which a commit and a publish can disagree, measures each of them against a real PostgreSQL and a real Kafka, and closes them one at a time with the outbox on the producer side, the inbox on the consumer side, and the idempotency key at the HTTP edge.

<!-- more -->

The numbers come from [the post's lab script](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-exactly-once-effects), which runs PostgreSQL 17 and Kafka in containers and counts rows and messages after each scene. Versions: omni-box 0.2.0, aiokafka 0.14.0, SQLAlchemy 2.0.52, Python 3.13. The producer side of the outbox has [its own post](2026-05-15-transactional-outbox-with-omni-box.md); this one is about the whole path.

## Messages versus effects

"At-least-once", "at-most-once" and "exactly-once" are statements about *messages*: how many times a consumer will see a given record. They are the broker's vocabulary and they are true inside the broker. Kafka's own exactly-once, transactions across topics with an idempotent producer, is real and it is scoped to Kafka: a consume-transform-produce loop whose input and output are both topics can be made exactly-once. The moment the transform writes a row in PostgreSQL, the guarantee ends at the JDBC boundary, or in our case the asyncpg one.

The business does not care about messages. It cares that the customer was charged once, the invoice was created once, the email was sent once. Those are *effects*, and the question to ask about a pipeline is not "how many times is the message delivered" but "how many times does each effect happen, and does it happen at all". Two different questions, and the second one has a good answer even though the first one does not.

## Every window, measured

Start with the simplest thing a service does: write an order, tell the world. Two writes, two systems, and a process that can die between them.

```text
commit, then publish, crash between:  orders=1  messages=0
publish, then commit, commit fails:   orders=0  messages=1
```

The first row is an order that exists and an event that does not. Billing never hears about it; the customer has an order nobody will invoice. The second row is the other order: an event without a row, a bill for an order that does not exist. There is no ordering of the two writes that avoids both, because whichever goes second can fail after the first succeeded. This is the dual-write problem, and it is not a bug in the code that does it; it is a property of two commits.

## The outbox closes the producer side

Write the event *into the database*, in the same transaction as the row. Now there is one commit, and either both the order and the event exist or neither does. A relay process reads pending events from the table, publishes them to Kafka, and marks them completed. The relay is where the second commit went, and it is where the failure window went with it:

```text
relay cycle 1, crash after the send:  outbox rows [('pending', 0)]    messages=1
relay cycle 2, normal:                outbox rows [('completed', 0)]  messages=2
```

In cycle one the relay sent the event to Kafka and died before the transaction that marks the row completed could commit. The row is still pending; the message is on the topic. In cycle two the relay finds the pending row and does its job: the message is on the topic twice. Nothing was lost. Something was duplicated. That is the whole trade: an outbox turns "maybe lost, maybe duplicated" into "never lost, maybe duplicated", and the guarantee on the wire is at-least-once, by construction, because the send happens before the commit that records it and a crash between the two republishes.

This is where a lot of designs stop, with a note saying consumers must be idempotent, and then every consumer team implements that note differently.

## The inbox closes the consumer side

The consumer's half of the pattern is the inbox: a table keyed by `(message_id, consumer_group)` with a unique index, into which the consumer inserts a row for each message it processes, in the same transaction as its effect. A second delivery of the same message collides with the row, the collision is the signal, and the effect is skipped:

```text
delivery 1: processed=True  duplicate=False  committed=True   invoices=1
delivery 2: processed=False duplicate=True   committed=True   invoices=1
```

Both copies of the message arrived. One invoice. The second delivery was committed at the broker, so it is not redelivered, and the handler never ran for it. The dedup window is the lifetime of the inbox row, which has to outlive the broker's retention, and the key is per consumer group, so two consumers of the same topic each get their own once.

The word *transaction* in that description is doing all the work. The inbox row and the invoice have to commit together. If the handler wrote the invoice in its own session and the inbox row committed separately, a crash between the two would give either an invoice with no record of it, so the redelivery makes a second one, or a record with no invoice, so the redelivery is skipped and the invoice never exists. The handler must write through the transaction the runner opened, and the library has to hand it that transaction:

```python
async def create_invoice(event: InboxEvent, repo: InboxEventRepository) -> None:
    await repo.session.execute(invoices.insert().values(order_id=event.payload["order_id"]))
```

That `repo.session` is the inbox row's transaction. The runner inserts the row, runs the handler, commits both, then commits the broker offset. If the handler raises, the row rolls back with it and the broker redelivers, which is a retry that starts from nothing, as a retry should.

## The HTTP edge

There is one more window, before any of this: the client that sent the order in the first place timed out and sent it again. Two orders, two outbox events, two invoices, all of them correct and all of them duplicates. The outbox and the inbox cannot see this one, because from where they stand these are two different orders. The dedup here belongs at the edge, keyed by the client's idempotency key, and it is the subject of [the idempotency post](2026-09-07-idempotency-keys-the-part-everyone-gets-wrong.md). Three points of deduplication, one per boundary a request crosses.

## The whole path

```text
HTTP request        ──  idempotency key: the same request is handled once
      │
PostgreSQL          ──  one transaction: the business row and the outbox row
      │
relay               ──  at least once: publish, then mark completed
      │
Kafka               ──  delivers each message at least once
      │
inbox               ──  (message_id, consumer_group): the same message is handled once
      │
consumer            ──  one transaction: the inbox row and the effect
```

Every arrow in that picture is at-least-once. Every box is a place where "once" is enforced by a unique key inside one transaction. The guarantee the whole path gives is that each effect happens exactly once, and it is built entirely out of at-least-once delivery plus three keys, which is why it survives crashes at every arrow and why no single component has to promise more than it can keep.

## Why the library must not own the transaction

Every step above says "in one transaction", and every one of those transactions has something of yours in it: the order row, the invoice row. A library that opened and committed its own transactions would put the outbox row in one and your order in another, which is the dual write again with extra steps. So the outbox repository takes your session and inserts into it, the relay runs its fetch, publish and mark inside a transaction you open and commit, and the inbox runner opens the transaction and hands it to your handler. The transactional boundary is the one thing the library cannot take from you, because the guarantee lives there.

## What it looks like

The producer side, the row and the event together:

```python
async with session_factory() as session, session.begin():
    await session.execute(orders.insert().values(id=order_id))
    await PostgresOutboxRepository(session, model_class=OutboxEventDB).create(
        domain.create_outbox_event(
            aggregate_type="order", aggregate_id=order_id, event_type="order.created",
            topic="orders.events", partition_key=str(order_id), payload={"order_id": str(order_id)},
            idempotency_key=f"order.created:{order_id}",
        )
    )
```

The relay, one cycle, in a transaction that is yours:

```python
async with session_factory() as session, session.begin():
    repo = PostgresOutboxRepository(session, model_class=OutboxEventDB)
    await OutboxPublisher(repo, KafkaEventPublisher(producer, EnvelopeEventConverter())).publish_batch(worker_id="relay-1", batch_size=100)
```

And the consumer, whose handler writes through the transaction it was given:

```python
runner = InboxConsumerRunner(
    consumer=KafkaEventConsumer(kafka_consumer),
    transaction_provider=InboxTxProvider(session_factory),   # opens the transaction, yields the repository
    handler=create_invoice,                                   # writes through repo.session
    worker_id="billing-1",
    consumer_group="billing",
)
```

Those three fragments are the three rows of measurements above, in order. They are [omni-box](https://bedrock-python.github.io/omni-box/), which ships the outbox and the inbox as primitives over a transaction it never opens, and the edge is [idempotency-kit](https://bedrock-python.github.io/idempotency-kit/). Neither delivers exactly once. Together with your transactions, they make each effect happen once, which was the thing you wanted from exactly-once all along.

The point was the second table. Two messages, one invoice.
