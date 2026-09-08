# Lab: partition retention is not DROP TABLE

One script against PostgreSQL 17 in a container. It builds `events` partitioned by month with
fifteen monthly partitions, one partition attached by hand on a boundary the scheme does not use,
and a `receipts` table with a foreign key into `events`. Then it runs the retention job most
codebases have — `DROP TABLE` by name pattern, `CASCADE` when that fails — and prints what is left.
It rebuilds the same table and runs the same retention as a plan: the plan printed before anything
happens, detach and drop as separate steps with a grace period, an archive hook before the drop
(and a hook that fails), and a partition another table still references.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "pg-partsmith==1.5.0" asyncpg "testcontainers[postgres]"
.venv/bin/python retention_lab.py
```
