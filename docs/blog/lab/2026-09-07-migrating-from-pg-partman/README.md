# Lab: adopting a pg_partman-managed table

PostgreSQL 17 with pg_partman 5.5 in a container built from the `Dockerfile` here. pg_partman
creates and maintains a monthly `events` table; the lab reads its `part_config` row, maps it onto a
pg-partsmith configuration, and asks pg-partsmith what it sees in a tree it did not build — then
runs both maintainers side by side, and finally switches pg_partman off and applies a policy that
differs from it.

```bash
docker build -t pg-partman-lab:17 .
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "pg-partsmith==1.5.1" asyncpg testcontainers
.venv/bin/python partman_lab.py
```
