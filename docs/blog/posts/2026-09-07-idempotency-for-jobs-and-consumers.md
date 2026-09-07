---
date: 2026-09-07
authors:
  - alex
categories:
  - Tutorials
tags:
  - idempotency-kit
  - idempotency
  - background-jobs
  - kafka
  - redis
  - workers
---

# Idempotency for background jobs and Kafka consumers

The `Idempotency-Key` header gets the attention because it has a name and a spec, but the same problem arrives at every worker that takes jobs from a queue, and it arrives more often, because queues deliver at least once by design. A worker sends the invoice email, dies before it acknowledges the job, and the job is delivered again; a visibility timeout expires while a slow worker is still running and a second worker picks the job up in parallel; a Kafka partition is rebalanced and the last uncommitted batch is replayed. None of those is a bug in the queue. All of them are a duplicate effect unless something dedupes it, and that something is the same idempotency key as the HTTP case, with one difference in what it should be made of.

<!-- more -->

The numbers come from [the post's lab script](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-idempotency-for-jobs-and-consumers), with Redis 7 in a container and an in-process queue that delivers at least once. Versions: idempotency-kit 0.3.0, redis-py 8.1.0, Python 3.13.

## The crash before the ack

A queue that will not lose a job keeps it visible until the worker acknowledges it. The worker's job is: do the effect, then acknowledge. Between the two the process can die, and when it does the queue redelivers, which is correct, and the worker does the effect again, which is not:

```text
plain handler                                deliveries=2  mails sent=2
handler under an idempotency key = job id    deliveries=2  mails sent=1
```

Two deliveries either way. The plain handler sent the invoice twice. The handler wrapped in an idempotency key, using the job id as the key, sent it once: the redelivery found the record of the first run and replayed its result without calling the mailer. That is the whole mechanism from [the HTTP post](2026-09-07-idempotency-keys-the-part-everyone-gets-wrong.md), pointed at a job instead of a request, and the store is the same Redis.

```python
async def handle(job: dict) -> None:
    await coordinator.coordinate("mail.invoice", job["job_id"], 3600, adapter, mailer.send_invoice, job["order_id"])
```

The queue's own at-least-once guarantee and the key's at-most-once effect compose into the job happening once, which is exactly the outbox-plus-inbox argument from [the exactly-once post](2026-09-07-exactly-once-effects.md) with a queue in place of Kafka.

## Two workers, one job

The nastier redelivery is the concurrent one. A worker is slow, the queue's visibility timeout expires, a second worker receives the same job, and now both are running it at the same time. A result cache does not help here, because neither has finished; this is the case that needs the in-flight reservation:

```text
in_flight='wait'     {'A': 'em_1', 'B': 'em_1'}               mails sent=1
in_flight='raise'    {'A': 'em_1', 'B': 'in progress, requeue'}  mails sent=1
```

Worker A reserved the key and ran. Worker B found the reservation. In `wait` mode it waited for A's result and returned the same receipt, so both acknowledge and the queue is clean. In `raise` mode it got an error saying the job is in progress, which is the right answer for a queue that would rather requeue with a delay than hold a worker idle: B puts the job back, A finishes, and the next delivery replays A's receipt. Both modes sent one mail. The plain handler, in this scene, would have sent two, with nothing in either worker's logs to say so.

## What the key is made of

This is the one place jobs differ from HTTP. For a request, the client mints the key and its meaning is "this request". For a job, the worker chooses the key, and the obvious choice, the job id, is the identity of the *delivery*, which is the wrong thing:

```text
key = job id: two jobs for order-9           -> mails sent=2   (the key must be the effect's identity, not the delivery's)
key = 'order-9:invoice': the same two jobs   -> mails sent=2   (a colon is not allowed in a key; the record fails validation and the action runs unprotected)
key = 'order-9.invoice': the same two jobs   -> mails sent=1
```

Two jobs were enqueued for the same order, by a retrying producer or two code paths that both decided the invoice should go out. Keyed by job id they are two different keys and two invoices. Keyed by the effect, "the invoice for order 9", they are one key and one invoice, however many jobs carry it. The key should name the effect: the order and the action, not the message that asked for it.

The middle row is a mistake I made writing the lab and left in, because it is exactly the kind a reader will make. The key contained a colon, which the library reserves as the separator in its storage key, so the record failed validation; the coordinator treats validation trouble the way it treats storage trouble, counts it, logs it and runs the action unprotected, and the two jobs sent two mails. The rule is documented and the failure is logged, and it is still the sort of thing to have a test for: a key that cannot be stored is a job with no idempotency, and nothing raises.

## Consumers: the inbox and the key are not the same tool

A Kafka consumer has all three of the scenarios above, and it also has [the inbox](2026-09-07-transactional-inbox.md). The two solve different halves of the problem and a consumer that does anything external needs both.

The inbox row commits in the same database transaction as the handler's *database* effect. A redelivered message collides with the row and the handler does not run. That covers the invoice row, the ledger entry, the status update, anything written through the same session, and it covers them exactly once, because the row and the effect are one commit.

It does not cover the mail. A handler that writes the ledger entry and sends an email is protected on the entry and not on the email, because the email is not in the transaction; a redelivery after a crash between the send and the commit rolls the row back and sends the mail again. The external effect needs its own key, and the natural one is the message id, or better, the effect's identity derived from the message, wrapped exactly as the job above:

```python
async def on_order_created(event: InboxEvent, repo: InboxEventRepository) -> None:
    await repo.session.execute(ledger.insert().values(order_id=event.payload["order_id"]))       # the inbox protects this
    await coordinator.coordinate("mail.invoice", f"{event.payload['order_id']}.invoice", 86400,   # the key protects this
                                 adapter, mailer.send_invoice, event.payload["order_id"])
```

One transaction for the row, one reservation for the side effect, and a message delivered three times produces one row and one mail.

## Lifetime

A job's key has to outlive the longest plausible redelivery, which for a queue with a dead-letter policy can be days, and for a batch job that reruns from a checkpoint after a crash can be a full day later. Twenty-four hours is the usual answer, a week for jobs that are replayed by hand after incidents, and the floor of a minute is not relevant here; what matters is that the record outlives the queue's own retention for the job, because a redelivery after the record expired is a new job as far as the key is concerned.

Everything above is [idempotency-kit](https://bedrock-python.github.io/idempotency-kit/), the same coordinator as the HTTP case with the same reservation semantics; the only thing that changed between the two posts is who chooses the key and what it names.

The point was the third table. Two, two, one.
