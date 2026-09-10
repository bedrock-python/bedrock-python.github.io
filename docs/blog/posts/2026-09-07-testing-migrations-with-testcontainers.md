---
date: 2026-09-07
authors:
  - alex
categories:
  - Tutorials
tags:
  - alembic-gauntlet
  - alembic
  - testcontainers
  - postgresql
  - pytest
  - ci
---

# Testing database migrations with Testcontainers: up, down and up again

<div class="bdr-post__hero" data-bdr-post="2026-09-07-testing-migrations-with-testcontainers" role="img" aria-label="A disposable real database, walked forward, back and forward again" markdown="0"></div>

[The five migration tests](2026-09-07-five-alembic-migration-tests.md) post made the case; this one is the setup, step by step, from an empty `tests/` directory to a green job in CI that walks every revision forward, back and forward again against a real PostgreSQL. It is short because the hard part, the contract between the test runner and `env.py`, is fifteen lines, and everything else is a fixture and a marker. The numbers at the end are what the whole thing costs on a laptop and in a GitHub Actions job.

<!-- more -->

The code is [the lab from the five-tests post](https://github.com/bedrock-python/bedrock-python.github.io/tree/master/docs/blog/lab/2026-09-07-five-alembic-migration-tests): a four-revision history for a small shop and the three suites that run against it. Versions: Alembic 1.19.2, SQLAlchemy 2.0.52, asyncpg 0.31.0, testcontainers 4.15.0, pytest 9.1.1, pytest-asyncio 1.4.0, alembic-gauntlet 0.2.2, PostgreSQL 17, Python 3.13.

## Step 1: a database that exists only for the test session

SQLite cannot stand in for PostgreSQL here: no schemas, no enum types, different constraint reflection, and a migration tested against a different engine is a different migration. The cheapest real PostgreSQL is a container that starts once per test session, which is a session-scoped fixture yielding a DSN:

```python
# tests/conftest.py
from alembic_gauntlet.contrib.testcontainers import migration_db_url  # noqa: F401
```

That fixture starts `postgres:17-alpine`, waits for it, and yields its connection URL rewritten for asyncpg; the container is stopped when the session ends. If a database already exists, in a developer's compose file or a CI service, override the fixture with your own session-scoped one returning an async DSN:

```python
@pytest.fixture(scope="session")
def migration_db_url() -> str:
    return "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"
```

The DSN must name an async driver. A bare `postgresql://` selects psycopg2 and the async engine refuses it before a single query.

## Step 2: pytest configuration

Two settings, neither optional:

```ini
# pytest.ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
markers =
    integration: needs the PostgreSQL container
```

The tests and fixtures are `async def` with no marker, so pytest-asyncio has to run in auto mode; in strict mode they fail with "async def functions are not natively supported" and the fixtures arrive as unawaited generators. The marker lets `pytest -m "not integration"` run the unit suite without Docker.

## Step 3: the contract with env.py

The runner does not shell out to `alembic`. It drives `alembic.command.upgrade` and `downgrade` in-process on a connection it opened, inside a transaction it will roll back, in a schema it created for this one test. For that to be real, `env.py` has to use what it is given:

```python
target_schema = config.attributes.get("target_schema") or os.getenv("MIGRATION_SCHEMA", "public")


def do_run_migrations(connection: Connection) -> None:
    if target_schema != "public":
        connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{target_schema}"'))
        connection.execute(text(f'SET LOCAL search_path TO "{target_schema}"'))  # LOCAL: dies with the transaction
    context.configure(connection=connection, target_metadata=target_metadata, version_table_schema=target_schema)
    with context.begin_transaction():
        context.run_migrations()


injected = config.attributes.get("connection")
if injected is not None:
    do_run_migrations(injected)          # the test runner owns the connection and the transaction
else:
    asyncio.run(run_migrations_online())  # production: build the engine from the URL
```

Two attributes, `connection` and `target_schema`, are set by the runner before every command and removed after. In production neither is set and the `else` branch runs as before. The one line to get right is `SET LOCAL`: a plain `SET search_path` outlives the transaction, goes back to the pool with the connection, and sends the next test's queries into a schema that was dropped.

<!-- diagram:concept -->
<figure class="bdr-diagram" markdown="1">
<figcaption><span class="bdr-diagram__eyebrow">THE IDEA, VISUALIZED</span><strong>The test and Alembic must reach the same schema</strong></figcaption>
<div class="bdr-diagram__viewport" markdown="1" data-search-exclude>

```mermaid
---
config:
  theme: default
  look: classic
  flowchart:
    useMaxWidth: false
    wrappingWidth: 150
    padding: 12
    nodeSpacing: 24
    rankSpacing: 32
---
flowchart TD
    accTitle: The test and Alembic must reach the same schema
    accDescr: A real PostgreSQL container supplies the database. Each test isolates its schema, and env.py must honor the supplied connection so migrations and assertions inspect the same place.
    P[("PostgreSQL / Testcontainers")] --> S["Isolated schema per test"]
    S --> C["Connection with the test search_path"]
    C --> E["Alembic env.py"]
    E --> M["Run migrations"]
    M --> A["Assert schema and data"]
    A --> X["Clean up the test schema"]
```

</div>
<p class="bdr-diagram__caption">A real PostgreSQL container supplies the database. Each test isolates its schema, and env.py must honor the supplied connection so migrations and assertions inspect the same place.</p>
</figure>
<!-- /diagram:concept -->

## Step 4: the test file

```python
# tests/test_migrations.py
import pytest
from alembic.config import Config
from alembic_gauntlet import MigrationTestBase
from sqlalchemy import MetaData

from shop.models import Base


@pytest.mark.integration
class TestMigrations(MigrationTestBase):
    @pytest.fixture
    def orm_metadata(self) -> MetaData:
        return Base.metadata

    @pytest.fixture
    def alembic_config(self) -> Config:      # only if alembic.ini is not in the working directory
        return Config("alembic.ini")
```

Inheriting the base class yields five tests: every revision up, down one step and up again; the schema after a full upgrade compared against the models with autogenerate; exactly one head; a full downgrade to base; and every constraint and index name checked against the metadata's naming convention. Each test runs in its own schema, `test_mig_<hex>`, dropped with `CASCADE` afterwards, so tests can run in parallel with `pytest -n auto`.

The stairway, written out, is the loop that matters:

```python
for i, revision in enumerate(revisions):            # base -> head
    upgrade(revision)
    assert current_revision() == revision
    downgrade(revisions[i - 1] if i else "base")
    upgrade(revision)                                # a downgrade that left something behind fails here
```

## Step 5: CI

GitHub's Ubuntu runners have Docker, so the same conftest works there with no `services:` block:

```yaml
test-integration:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v7
    - uses: astral-sh/setup-uv@v7
    - run: uv sync --group dev
    - run: uv run pytest -m integration
```

On a runner without Docker, a `services: postgres:` block plus the override fixture from step 1 does the same job.

## What it costs

On a laptop with the image already pulled, the lab's eleven tests, the plain upgrade, five by hand and the five inherited, run in 4.3 s, of which 2.7 s is the container starting and 0.4 s is the stairway over four revisions. A history of forty revisions is ten times the stairway and the same container: under ten seconds. Every one of the five bugs in the five-tests post was caught inside that budget, and the one that `alembic upgrade head` alone catches, two heads, is the only one that would have been caught without it.

The base class is [alembic-gauntlet](https://bedrock-python.github.io/alembic-gauntlet/guide/quickstart/), and the `env.py` contract above is [its own page](https://bedrock-python.github.io/alembic-gauntlet/guide/env-py/).

The point was step 3. Fifteen lines, and `SET LOCAL`.
