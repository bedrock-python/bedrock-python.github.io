# Lab: UUIDv7 as a PostgreSQL partition key

One script against PostgreSQL 17 in a container: a table whose primary key is a single `UUID`
column and which is RANGE-partitioned on that column, with monthly windows whose bounds are the
smallest UUIDv7 of each month. It prints the generated bounds, routes rows written now and two
months ago, compares what the planner prunes for an id range against a timestamp column, and tries
the ids that do not fit: imported history, a clock three months ahead, a plain uuid4, and a late
row for a month retention has already retired.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "pg-partsmith==1.5.0" asyncpg "testcontainers[postgres]"
.venv/bin/python uuidv7_lab.py
```
