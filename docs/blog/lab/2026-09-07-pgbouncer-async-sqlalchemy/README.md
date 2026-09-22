# Lab: PgBouncer transaction mode and async SQLAlchemy

The orders service reads `app.orders` through PgBouncer in transaction mode. The scripts start disposable PostgreSQL and PgBouncer containers, check the results and remove the containers on exit. Docker and `uv` are required.

Run from this directory:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python pgbouncer_lab.py
uv run --no-project --python 3.13 --with-requirements requirements.txt python jit_probe.py
```

| Script | What it asserts |
|---|---|
| `pgbouncer_lab.py` | Four workers run 40 parameterized statements per setup: directly, through PgBouncer with tracking and both caches enabled, and with tracking and both caches disabled using the kit's unique names. Also checks order lookup, rollback and schema scope |
| `pgbouncer_lab.py`, forced backend switch | A prepared statement survives a PostgreSQL connection change with tracking enabled; the same reuse fails with SQLSTATE `26000` when tracking is disabled |
| `pgbouncer_lab.py`, query cancellation | `SET LOCAL statement_timeout='100ms'` cancels `pg_sleep(1)` with SQLSTATE `57014`; rollback restores normal queries and the original timeout |
| `jit_probe.py` | Unsupported startup parameters are rejected. Ignoring `jit` and `search_path` drops their values; the kit applies `db_schema` inside each transaction instead |

The scripts print `PASS` only after checking each result. They use `postgres:17-alpine` and the versioned image `edoburu/pgbouncer:v1.25.2-p0`; the main script also checks the reported PgBouncer version and active settings. `requirements.txt` pins sqlalchemy-foundation-kit 0.4.0, SQLAlchemy 2.0.54, asyncpg 0.31.0 and the other direct Python dependencies.

`pool_flow.py` contains the article's Python examples. `pgbouncer-settings.ini` supplies the actual pool settings: two server connections per database/user pair, 50 clients and up to 200 tracked prepared statements per server connection. `lab_support.py` adds routing, disposable test credentials and the Docker network. Its `Bouncer.admin()` uses the container's `psql` to run `SHOW POOLS`, `SHOW STATS` and other admin commands with the required simple-query protocol.

The concurrent SQL workload allows three seconds for local checkout so it tests compatibility without intentionally triggering the article's 200 ms timeout. The separate [pool metrics lab](../2026-09-07-sqlalchemy-pool-metrics/README.md) checks that timeout and both queues. These scripts verify behavior; they are not capacity benchmarks or production configuration templates.
