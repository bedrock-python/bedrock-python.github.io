# Lab: the five migration tests

The code behind [the post](../../posts/2026-09-07-five-alembic-migration-tests.md): a four-revision
Alembic history for a small shop, five variants of it with one bug each, and three test suites run
against every variant. Needs Docker; PostgreSQL 17 runs in a container started by the test session.

```bash
uv venv --python 3.13 .venv
uv pip install --python .venv/bin/python "alembic-gauntlet[asyncio,testcontainers]==0.2.2" asyncpg
.venv/bin/python -m pytest -q                       # the clean history: 11 passed
VARIANT=drift .venv/bin/python -m pytest -q         # one buggy history
.venv/bin/python run_matrix.py                      # every suite against every history
```

| Path | What it is |
|---|---|
| `shop/models.py` | the ORM side: two tables, one enum, the naming convention |
| `migrations/env.py` | the `env.py` contract: injected connection, injected schema, `SET LOCAL search_path` |
| `migrations/versions/clean/` | the four revisions as autogenerate would have written them |
| `migrations/versions/<bug>/` | the same four with one file changed; `BUG.txt` says which and how |
| `tests/test_plain_ci.py` | what most pipelines do: `upgrade head` on an empty database |
| `tests/test_by_hand.py` | the five checks written against Alembic's own API; plumbing in `tests/helpers.py` |
| `tests/test_gauntlet.py` | the same five inherited from `alembic_gauntlet.MigrationTestBase` |
| `run_matrix.py` | runs the suite once per variant and prints the pass/fail matrix |

The `VARIANT` environment variable selects `migrations/versions/<variant>` through Alembic's
`version_locations`; `clean` is the default.
