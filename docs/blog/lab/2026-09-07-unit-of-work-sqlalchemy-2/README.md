# Lab: the unit of work in SQLAlchemy 2

One script against PostgreSQL 17 in a container.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "sqlalchemy-foundation-kit==0.3.0" asyncpg "testcontainers[postgres]"
.venv/bin/python uow_lab.py
```

Five scenes: a use case that fails on its second write with repositories that commit for
themselves and with a unit of work; the same use case succeeding; a write inside a read-only block;
a savepoint around one failing step; and the use case under a unit test with no database.
