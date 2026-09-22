# Lab: the transactional inbox

Runnable consumer scenarios from [the article](../../posts/2026-09-13-reliable-events-outbox-inbox-kafka.md).
Docker must be running. Run from this directory in a repository checkout:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt inbox_lab.py
```

The script imports `event_flow.py`, models and container helpers from the
[delivery lab](../2026-09-07-exactly-once-effects/README.md); keep that sibling directory.
`requirements.txt` includes its pinned dependencies: omni-box 0.3.0, aiokafka 0.14.0,
SQLAlchemy 2.0.54, asyncpg 0.31.0 and testcontainers 4.15.0.
The script creates and removes `postgres:17-alpine` and a single
`confluentinc/cp-kafka:7.6.0` broker in KRaft mode.

The handler writes an invoice in the Inbox transaction. The runner uses
`EXACTLY_ONCE_INBOX`, disables automatic Kafka commits and leaves
`exactly_once_commit_on_failed=False`.

Assertions cover:

- an exception after the invoice INSERT rolls back both invoice and Inbox;
- the article's worker loop stops on an uncommitted result before processing the next record;
- a fresh consumer in the same group retries that record before the next one;
- failure at the offset-commit boundary leaves the invoice and completed Inbox committed;
- replay then skips the handler and commits the real Kafka offset;
- another consumer group has a separate Inbox identity and processes the event;
- deleting the completed Inbox row lets a replay run the handler again;
- two publications without stable ID headers become two messages identified by their offsets.

The offset failure is injected by a consumer subclass that raises from `commit()`.
It first queries PostgreSQL to verify that the invoice and completed Inbox already exist.
The handler exception and explicit Inbox deletion are also controlled failure scenarios.
Kafka, database transactions and restarted consumers are real.

Invoices deliberately allow repeated order IDs, exposing duplicate effects.
Each scenario prints `PASS` only after its assertions succeed. This lab verifies one
sequential consumer flow; it does not establish safe concurrent processing of one partition.
