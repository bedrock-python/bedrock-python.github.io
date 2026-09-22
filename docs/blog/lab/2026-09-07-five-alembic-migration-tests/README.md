# Lab: the five migration tests

The historical title is retained. The current lab has **20 tests, one correct migration history and 13 broken variants** for a shop with users and orders. Each broken variant changes one revision file; its `BUG.txt` explains the error.

Docker and `uv` are required. Run from this directory:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python -m pytest -q
uv run --no-project --python 3.13 --with-requirements requirements.txt python run_matrix.py
```

The first command expects `20 passed`. `run_matrix.py` checks every history, requiring the designated test to fail for each deliberate bug. It exits unsuccessfully for unexpected success, skips, infrastructure errors or a broken clean history. For `two_heads`, it runs the two head checks and the basic upgrade: the other tests require an unambiguous head. All other histories run the complete suite.

To run only the new behavior and data cases, including the clean baseline:

```bash
uv run --no-project --python 3.13 --with-requirements requirements.txt python run_matrix.py --variants clean,drift_check_expression,data_loss
```

PostgreSQL runs in `postgres:17-alpine`. The normal pytest run starts one container for the session; the matrix starts one container for all its subprocesses. Each test uses its own schema, which is removed afterward, and the container is removed on exit. `MIGRATION_TEST_URL` optionally supplies an existing **disposable test database**. `VARIANT` selects a history; `clean` is the default.

`requirements.txt` pins alembic-gauntlet 0.3.0, Alembic 1.20.0, SQLAlchemy 2.0.54, asyncpg 0.31.0, pytest 9.1.1, pytest-asyncio 1.4.0 and testcontainers 4.15.0. `pytest.ini` enables asyncio auto mode. Installing alembic-gauntlet registers the `migration_engine` fixture as a pytest plugin.

| File | Purpose |
|---|---|
| `shop/models.py` | Users, orders, enum values and naming convention |
| `tests/conftest.py` | Container/database fixture and selected migration history |
| `migrations/env.py` | Accept injected connection/schema; otherwise create an engine and commit the migration transaction |
| `tests/test_plain_ci.py` | Apply `head` once to an empty schema |
| `tests/test_by_hand.py` | Five checks through Alembic's API, including reapplying every revision |
| `tests/test_gauntlet.py` | Seven inherited checks, with server-default comparison enabled |
| `tests/test_drift_extras.py` | Handwritten checks for defaults, CHECK names and enum values |
| `tests/test_business_rules.py` | Reject amounts `0` and `-1`; preserve a paid order and its user when upgrading `0003` to `0004` |
| `tests/test_environment.py` | Run the standalone environment in a subprocess; verify committed revision and tables from a new connection |
| `ci-example.yml` | GitHub Actions template; copy to `.github/workflows/` to enable it and adapt the working directory for your project |

The clean history creates users, then orders and their enum, then a positive-amount CHECK, then `users.is_active` with a server default of `true`.

| Variant | Expected detection |
|---|---|
| `enum_leftover` | Up/down/up fails because the enum survives downgrade |
| `wrong_name_in_downgrade` | Rollback tries to drop a nonexistent CHECK |
| `two_heads` | Both head checks and `upgrade head` fail |
| `bad_name` | Naming-convention check fails |
| `drift`, `drift_type`, `drift_server_default` | Schema diff reports nullable, type or default mismatch |
| `drift_index_missing`, `drift_extra_column` | Schema diff reports a missing index or extra column |
| `drift_check_missing` | Explicit CHECK-name comparison fails |
| `drift_enum_value` | Enum-value comparison fails |
| `drift_check_expression` | Names match, but the zero-amount behavior test fails |
| `data_loss` | Schema matches, but the saved order disappears |

The matrix also asserts that the seven inherited gauntlet checks pass in the last two variants: they demonstrate the need for application-specific tests. The hand-written round trip covers the final revision's reapplication; the gauntlet 0.3.0 stairway ends with that revision downgraded.

Alembic 1.20 has an optional CHECK-name autogenerate plugin, disabled in this lab. Neither that name comparison nor gauntlet's CHECK-name check proves expression equivalence. These tests verify correctness on small data sets; they do not measure production lock times or migration throughput.

[Read the article](../../posts/2026-09-13-testing-alembic-migrations-in-ci.md).
