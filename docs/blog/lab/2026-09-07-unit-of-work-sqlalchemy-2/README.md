# Lab: the unit of work in SQLAlchemy 2

Runnable code from [the article](../../posts/2026-09-13-sqlalchemy-sessions-and-transactions.md).
Docker must be running. The script creates and removes its own PostgreSQL container;
it does not use an existing database. Run from this directory in a repository checkout:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt uow_lab.py
```

Dependencies are pinned in `requirements.txt`: sqlalchemy-foundation-kit 0.4.0,
SQLAlchemy 2.0.54, asyncpg 0.31.0 and testcontainers 4.15.0.
The image is `postgres:17-alpine`; the script prints its server version
(17.11 in the verified run). The asyncpg driver is selected explicitly.

`models.py` defines orders, their events and optional newsletter subscriptions.
`order_flow.py` contains the ten Python snippets printed in both article editions.
`uow_lab.py` exercises them against real PostgreSQL, without repository mocks.

Assertions cover:

- two commits leaving an order without its rejected event;
- complete rollback with both native SQLAlchemy and the kit's Unit of Work;
- a generated ID after flush while another session still sees no row;
- successful commit and a dictionary result usable after session close;
- a duplicate optional subscription rolling back to a savepoint;
- another subscription constraint violation rolling back the entire operation;
- `query()` discarding an uncommitted write while allowing an explicit commit;
- PostgreSQL rejecting an INSERT after `SET TRANSACTION READ ONLY`;
- cancellation before commit rolling back rows and returning pool connections.

The `query()` test deliberately commits an isolated order to prove that the method
does not enforce a database write prohibition. This is a diagnostic example, not a checkout flow.
The lab resets its tables between independent scenarios. It prints
`PASS: transaction scenarios` only when all assertions succeed.

Connection lifetimes and the remaining external-wait/concurrency snippets are exercised
by the [session lab](../2026-09-07-stop-passing-asyncsession-everywhere/README.md).
