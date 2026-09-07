---
date: 2026-09-07
authors:
  - alex
categories:
  - Design
tags:
  - omni-box
  - kafka
  - inbox
  - outbox
  - idempotency
  - postgresql
---

# Transactional inbox: the other half of the outbox pattern

The outbox gets the attention because it solves the dramatic problem, the event that never left. The inbox solves the quiet one: the event that arrived twice, or arrived once and was half-handled when the consumer died. Every Kafka consumer has this problem, most consumers handle it with a comment that says "handlers must be idempotent", and the comment is honoured by whoever wrote the first handler and forgotten by whoever wrote the fourth. This post is the inbox as a mechanism: a row per message in the consumer's own database, in the same transaction as the effect, and a measurement of what each way of acknowledging a message does when the handler fails halfway.

<!-- more -->

The numbers come from [the post's lab script](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-transactional-inbox) and from the inbox scene of [the exactly-once lab](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-exactly-once-effects), both against PostgreSQL 17 and Kafka in containers. Versions: omni-box 0.2.0, aiokafka 0.14.0, Python 3.13.

## The consumer's two problems

A broker delivers at least once. That is not a Kafka limitation to be engineered around; it is the only guarantee a broker can give without losing messages, and the [outbox](2026-09-07-exactly-once-effects.md) on the producer side deliberately produces duplicates rather than gaps. So a consumer will see the same message twice: after a rebalance, after a crash between processing and committing the offset, after the relay republished. That is the first problem.

The second is subtler. A handler that writes an invoice and then fails, on a network error to a downstream service or a bug in the second half of the function, leaves the invoice written and the message unacknowledged. The redelivery writes a second invoice. Or the handler writes the invoice, the consumer commits the offset, and the process dies before the write commits: no invoice, no redelivery. Either way the effect and the acknowledgement disagree, and the reason is the same as on the producer side: two systems, two commits.

## The inbox row

The inbox is a table in the consumer's database, keyed by `(message_id, consumer_group)` with a unique index. To process a message, the consumer opens a transaction, inserts the inbox row, runs the handler *inside that transaction*, and commits. The handler's writes and the row commit together or not at all. A redelivery inserts the same key, collides with the row, and the collision is the answer: this message was handled, skip it.

```python
async def create_invoice(event: InboxEvent, repo: InboxEventRepository) -> None:
    await repo.session.execute(invoices.insert().values(order_id=event.payload["order_id"]))


runner = InboxConsumerRunner(
    consumer=KafkaEventConsumer(kafka_consumer),
    transaction_provider=InboxTxProvider(session_factory),   # opens the transaction, yields the repository
    handler=create_invoice,                                   # runs inside it, writes through repo.session
    worker_id="billing-1",
    consumer_group="billing",                                 # part of the key: each group gets its own once
)
```

The handler writes through `repo.session`, which is the transaction the inbox row is in. That one line is the whole guarantee. A handler that opened its own session would be back to two commits.

The duplicate case, measured in the exactly-once post's lab, where the relay had put the same message on the topic twice:

```text
delivery 1: processed=True  duplicate=False  committed=True   invoices=1
delivery 2: processed=False duplicate=True   committed=True   invoices=1
```

The second delivery found the row, reported itself as a duplicate, committed its offset so it is not delivered a third time, and never ran the handler.

## Measured: the handler fails halfway

The interesting case is the failing handler, and it is where the acknowledgement strategy decides whether the message is lost, duplicated or handled once. The lab sends one message, runs a handler that writes the invoice and then raises, stops the consumer, and starts a fresh consumer in the same group to see what it receives. Four strategies:

```text
AT_MOST_ONCE                       first: processed=False committed=True   second consumer: nothing delivered   handler ran=1  invoices=0
AT_LEAST_ONCE, commit ON_PERSIST   first: processed=False committed=True   second consumer: nothing delivered   handler ran=1  invoices=0
AT_LEAST_ONCE, commit ON_SUCCESS   first: processed=False committed=False  second consumer: processed=True      handler ran=2  invoices=1
EXACTLY_ONCE_INBOX (default)       first: processed=False committed=False  second consumer: processed=True      handler ran=2  invoices=1
```

The first two rows lose the message. `AT_MOST_ONCE` commits the offset before it tries anything, which is the right choice for a metric or a log line that is cheaper to drop than to repeat, and the wrong choice for an invoice. `AT_LEAST_ONCE` with the offset committed on persist commits after the transaction *whatever happened to it*, and the transaction rolled back, so the message is acknowledged and its effect is gone. The name is honest about the broker's guarantee and misleading about the outcome; it exists for consumers that record the failure elsewhere and retry from there.

The last two rows handle it once. The handler ran twice, because the first run's exception rolled the whole transaction back, invoice and inbox row together, and left the offset uncommitted, so the fresh consumer got the message again and the second run wrote the one invoice that exists. That is the exactly-once *effect*: not that the handler ran once, but that its effect exists once, because the first run's effect was never committed. The default strategy, `EXACTLY_ONCE_INBOX`, is the last row; its difference from the row above it is how it treats the duplicate and the locked cases, which the runner handles for you and the plain at-least-once mode leaves to the handler.

## What the inbox does not do

It does not make a side effect *outside* the database happen once. A handler that sends an email and then fails will send it again on the redelivery, because the email is not in the transaction. The inbox protects effects that share its database; anything else needs its own key, which is the idempotency-key argument from [the idempotency post](2026-09-07-idempotency-keys-the-part-everyone-gets-wrong.md) applied to a downstream call.

It does not deduplicate forever. The window is the lifetime of the row, and a retention job that deletes old rows makes an old message new again, so the retention has to outlive the broker's, not the disk's.

And it does not retry. The runner records no failure and no attempt count; a failed handler's retry comes from the broker, by redelivery, which is the correct source for it, because a retry that came from the inbox table would need the row to exist, and the row rolled back with the failure.

## The pair

Outbox and inbox are one pattern seen from two sides. The producer writes the event next to its state and lets a relay deliver it at least once; the consumer writes a row next to its effect and lets the collision dedupe it. Neither side needs the other to be perfect, and neither side delivers exactly once. Between them, every effect happens once, which is the property the message counts were standing in for all along.

The runner, the repository and the row above are [omni-box](https://bedrock-python.github.io/omni-box/)'s inbox half, which shares its pipeline and its PostgreSQL repository with the outbox half and never opens a transaction of its own.

The point was the third column. `invoices=0`, `invoices=0`, `invoices=1`, `invoices=1`.
