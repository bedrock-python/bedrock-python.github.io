# Lab: partitioning a live table

`migrate_lab.py` starts PostgreSQL 17 in a container, fills a plain `events` table with two
million rows over the last year and an `event_notes` table referencing it, and walks the
migration to a monthly partitioned table while a writer and a reader keep hitting `events`:
the key change, the swap, the first maintenance tick, the batched drain, the foreign key and
the empty DEFAULT. Every step prints its duration and what the writer and the reader saw.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "pg-partsmith==1.5.0" asyncpg "testcontainers[postgres]"
.venv/bin/python migrate_lab.py
```
