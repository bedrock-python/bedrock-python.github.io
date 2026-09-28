# Lab: what every production Python microservice reimplements {#lab-what-every-production-python-microservice-reimplements}

An orders API reads PostgreSQL and asks a local warehouse for stock. It combines servicewright, sqlalchemy-foundation-kit, clientwright and deadline-budget. Companion to [Why I extract Python service infrastructure into libraries](../../posts/2026-09-13-why-bedrock-python-libraries.md).

## Run {#run}

You need a running Docker daemon and uv. Run from the website repository root:

```bash
cd docs/blog/lab/2026-09-07-what-every-microservice-reimplements
uv run --no-project --python 3.13 --with-requirements requirements.txt python run_skeleton.py
```

The runner creates a temporary `postgres:17-alpine` container and two local HTTP listeners on automatically selected ports. Testcontainers removes its database on exit. Initial image download and container startup may take longer than the application checks. Network access is needed for uncached images, Python and dependencies.

`requirements.txt` pins servicewright 0.13.1, sqlalchemy-foundation-kit 0.4.0, clientwright 0.5.0, deadline-budget 0.1.3 and the main integration dependencies. Python 3.13 is used. The database schema is a fixture created by the runner; it is not a replacement for application migrations.

## What is asserted {#checks}

- Known orders are read by ID and matched with stock queried by SKU. Different quantities produce different `can_fulfill` results.
- Unknown orders return `404` without calling stock; zero, negative, oversized and nonnumeric deadline headers return `422`.
- One warehouse `503` is followed by one successful retry with a smaller forwarded time budget. Persistent `503` returns `503` after two attempts.
- An invalid stock payload becomes `503`; a stalled warehouse request becomes `504` under the request deadline.
- Readiness depends on PostgreSQL in this example and stays successful during a warehouse outage.
- The SQL connection is returned before the outbound HTTP call. During shutdown, readiness drops and an active request is allowed to finish before the shared client and database manager close.
- A PostgreSQL warmup failure prevents the HTTP listener from starting and closes resources that were already opened.
- The application use case works with ordinary objects, and the outbound adapter works without starting servicewright or FastAPI.

Assertions stop the run on a mismatch. Timeouts bound waits; no exact elapsed-time assertion is used. The shutdown scenario uses the runtime's stop event, not an operating-system signal, and releases its held request within the configured grace period.

## Files {#files}

- `orders.py`: order data, two small protocols and the application decision.
- `adapters.py`: SQL lookup, shared HTTP client configuration and stock-response validation.
- `service.py`: request budget, HTTP error mapping, resource scopes and runtime configuration.
- `lab_support.py`: controllable HTTP warehouse and runtime test helpers.
- `run_skeleton.py`: temporary database, fixtures and all assertions.
- `requirements.txt`: pinned dependencies.

The standalone `service.py` reads `DATABASE_URL`, `WAREHOUSE_URL` and optional `PORT` (default 8080), then calls `run_sync()`. Supply a migrated database and a warehouse that returns `{"available": 3}` from `/stock/{sku}`. The automated runner supplies both locally.

This read-only view does not reserve stock or create a distributed transaction. Authentication, TLS, deployment configuration and load testing are outside this local composition lab.
