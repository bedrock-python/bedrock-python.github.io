# Lab: what to monitor in a SQLAlchemy connection pool

One script against PostgreSQL 17 in a container: eight workers, a pool of two plus two overflow, a
one-second pool timeout, and a database that slows down halfway through. The kit's Prometheus
metrics are sampled every half second — the pool gauges, the wait in front of the pool and the
held time behind it — and printed next to the application's own count of failed checkouts.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "sqlalchemy-foundation-kit[settings,metrics]==0.4.0" asyncpg "testcontainers[postgres]"
.venv/bin/python pool_metrics_lab.py
```
