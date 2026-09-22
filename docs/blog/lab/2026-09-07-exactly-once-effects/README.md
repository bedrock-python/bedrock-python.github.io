# Lab: exactly-once effects

Runnable code from [the article](../../posts/2026-09-13-reliable-events-outbox-inbox-kafka.md).
Docker must be running. The script creates and removes its own PostgreSQL and Kafka
containers. Run from this directory in a repository checkout:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt effects_lab.py
```

Dependencies are pinned in `requirements.txt`: omni-box 0.3.0, aiokafka 0.14.0,
SQLAlchemy 2.0.54, asyncpg 0.31.0 and testcontainers 4.15.0.
Images: `postgres:17-alpine` and `confluentinc/cp-kafka:7.6.0` in KRaft mode.
The PostgreSQL driver is explicitly asyncpg.

`models.py` defines orders, invoices and the two omni-box ORM models.
`event_flow.py` contains all seven Python snippets printed in both article editions.
`lab_support.py` provides the containers and bounded Kafka reads used by all three labs.
The two services share one database here to keep the fixture small.

Assertions verify:

- order commit followed by a simulated crash leaves an order without an event;
- publication followed by transaction rollback leaves an event without an order;
- an order and its Outbox event roll back together;
- failure after Kafka acknowledgement but before the Outbox commit causes another publication;
- the two Kafka records have different offsets and the same `event_id`;
- Inbox processes the first record, skips the second and leaves one invoice.

The invoice's order ID is deliberately **not unique**: a constraint must not hide a
duplicate handler execution. A production rule limiting invoices per order should
also have its own constraint.

Failures at transaction boundaries are injected exceptions, not killed processes.
This single-broker setup tests delivery and database effects, not replication or cluster
failover. Kafka audits read to a captured end offset rather than trusting one timed poll.
Every `PASS` line follows assertions; a failed assertion exits the script with an error.

Continue with [handler failure and Inbox boundaries](../2026-09-07-transactional-inbox/README.md)
or [a paused broker and recovery](../2026-09-07-when-kafka-is-down/README.md).
