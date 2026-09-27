# Lab: UUIDv7 as a PostgreSQL partition key

This separate design keeps `PRIMARY KEY (id)` by partitioning directly on `id`. It uses PostgreSQL 17 and pg-partsmith 1.5.1, with explicit July–October 2026 partitions so results do not depend on today's date.

Docker and `uv` are required. Run from this directory:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python uuidv7_lab.py
```

| Check | Assertion |
|---|---|
| UUIDv7 monthly boundaries | Adjacent bounds meet; the September lower boundary routes into September |
| August id-range query | JSON `EXPLAIN` scans one partition |
| August `created_at` query | JSON `EXPLAIN` scans all four partitions |
| Old and future identifiers outside prepared ranges | Inserts fail with SQLSTATE `23514` |
| UUIDv4 constructed with an in-range prefix | Range routing accepts it; a separate UUID-version CHECK rejects it |
| September UUIDv7 with `created_at` in 2020 | Row routes into September |
| Late July row after July is detached | Insert fails because no partition accepts it |

`uuid_flow.py` contains the configuration and query from the article. `sample_uuid7()` is a lab fixture that constructs version/variant bits for supplied dates; it is not a production id-generation recommendation. `UUIDv7BoundaryCodec` encodes range boundaries, not fresh unique event ids.

`requirements.txt` and the database/query-plan helpers come from the neighboring [migration lab](../2026-09-07-partition-existing-table/README.md); keep both directories when copying the example. The PostgreSQL container is removed on exit. The July detach is an explicit step illustrating late-arrival behavior; automatic retention is covered in the separate maintenance article.
