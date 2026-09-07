# Lab: who owns the session

One use case, "place an order", written four ways against PostgreSQL 17 in a container: a session
per repository, a threaded session that a repository commits, one unit of work, and a unit of
work with a savepoint. The outbox write fails in every one, and the lab counts what survived.
Then the same designs run against a pool of two connections, a session is shared between two
tasks, and a transaction is used after its block.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "sqlalchemy-foundation-kit==0.3.0" "testcontainers[postgres]"
.venv/bin/python sessions_lab.py
```
