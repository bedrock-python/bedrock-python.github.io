# Lab: what to monitor in a SQLAlchemy connection pool

The orders service can wait for SQLAlchemy, run slow SQL, hold a connection while calling shipping, or wait inside PgBouncer. This script separates those cases using actual Prometheus observations and database connections.

Docker and `uv` are required. Run from this directory:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python pool_metrics_lab.py
```

| Scenario | Assertion |
|---|---|
| Local pool has one held connection | Second checkout times out after 200 ms; the exported timeout counter increases by one; the next request works after release |
| SQL executes `pg_sleep(0.2)` | The held-time histogram sum increases by at least about 200 ms |
| Shipping is awaited inside the transaction | One connection remains checked out during the external wait |
| Shipping is awaited after the transaction | No connection remains checked out; the response is unchanged |
| SQLAlchemy has two client connections, PgBouncer has one server connection | Checkout finishes, `SHOW POOLS` reports `cl_waiting=1`, and the local timeout counter stays at zero |

Events keep transactions and the local shipping fixture waiting until the script observes the expected state. PostgreSQL 17 and PgBouncer 1.25.2 run in disposable containers. This is a behavior check, not a throughput benchmark.

For the final scenario, both client connections are warmed and pre-ping and the schema hook are disabled. This prevents extra SQL from moving the server wait into connection acquisition or transaction setup.

The script imports setup helpers and the article's functions from the neighboring [PgBouncer lab](../2026-09-07-pgbouncer-async-sqlalchemy/README.md). Its `requirements.txt` includes that lab's pinned dependencies; keep both directories when copying the example. Each instrumented manager uses a different metrics prefix to avoid duplicate Prometheus registrations.
