# Lab: who owns the session

Docker must be running. The script creates and removes its own PostgreSQL 17 container.
Run from this directory in a repository checkout, keeping the neighboring
`2026-09-07-unit-of-work-sqlalchemy-2` directory: it supplies the shared models,
article functions and pinned requirements.

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt sessions_lab.py
```

The script prints the PostgreSQL version (17.11 in the verified run).
It checks that session construction leaves the pool free, the first query checks out
a connection, and closing the session returns it.

A controlled async wait models a shipping API. Two requests wait inside transactions
and occupy a two-connection pool, so a third request hits the pool timeout.
Moving that same wait before the transaction leaves the connections available.
Assertions inspect checked-out connections and persisted order/event rows; no HTTP
server or throughput benchmark is involved.

The script also reports what happens when two statements share one session.
Unsupported sharing may appear to work on an individual run, so a specific exception
is not required. Both tasks are awaited before cleanup. The supported variant uses
the article's `TaskGroup` function: six independent orders must receive six distinct
sessions, save six order/event pairs and return every connection.

A successful run ends with `PASS: session and pool scenarios`.
