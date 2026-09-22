# Lab: a Kafka outage and backlog recovery {#lab-what-happens-when-kafka-is-down-for-an-hour}

Runnable outage scenario from [the article](../../posts/2026-09-13-reliable-events-outbox-inbox-kafka.md).
Docker must be running. Run from this directory in a repository checkout:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt kafka_down_lab.py
```

The script imports the application code and container helpers from the
[delivery lab](../2026-09-07-exactly-once-effects/README.md); keep that sibling directory.
Its requirements pin omni-box 0.3.0, aiokafka 0.14.0, SQLAlchemy 2.0.54,
asyncpg 0.31.0 and testcontainers 4.15.0.
The script creates and removes `postgres:17-alpine` and a single
`confluentinc/cp-kafka:7.6.0` broker in KRaft mode.

The scenario:

1. Save and publish one warmup order so the producer has connected.
2. Pause the Kafka container and commit three new orders with their Outbox events.
3. Run three relay cycles. Each query must return three pending events and zero attempts spent.
4. Unpause Kafka in a `finally` block before producer shutdown.
5. Drain the backlog within a bounded wait and verify that all four event IDs reached Kafka.

The relay's publication timeout is two seconds. In omni-box 0.3.0, that timeout and
`TransientError` defer publication without consuming the event's retry budget.
The test makes no claim that other publication errors behave the same way.
An in-flight send may arrive after a timeout, so recovery checks delivered event IDs
and completed Outbox rows rather than asserting one Kafka record per event.

`BACKLOG_SQL` is the exact SQL query shown in both article editions.
All status and delivery checks use assertions; `PASS` lines report verified results.
The outage lasts seconds, not an hour. The article's hour-long backlog example is arithmetic,
not a load test. This single-broker experiment does not test replication, sustained
throughput or database capacity.
