# Lab: PgBouncer transaction mode and async SQLAlchemy

PostgreSQL 17 and PgBouncer 1.25 run in containers on one Docker network, started by the scripts.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "sqlalchemy-foundation-kit[settings]==0.3.0" asyncpg "testcontainers[postgres]"
.venv/bin/python pgbouncer_lab.py
.venv/bin/python jit_probe.py
```

| Script | What it measures |
|---|---|
| `pgbouncer_lab.py` | twenty clients, twenty distinct statements each, twice, through: PostgreSQL directly, PgBouncer with its current defaults, PgBouncer with `max_prepared_statements=0` (the default before 1.22), and sqlalchemy-foundation-kit's settings (the post also quotes the 0.2.1 rows, run before the fix); then a plain `SET` on one client connection read back from another |
| `jit_probe.py` | what `SHOW jit`, `SHOW search_path` and `SHOW application_name` return through PgBouncer with `ignore_startup_parameters=jit,search_path` |
