"""One PostgreSQL container per session, and the migration history variant under test."""

import os

import pytest
from alembic.config import Config
from alembic_gauntlet.contrib.testcontainers import migration_db_url  # noqa: F401  (session-scoped fixture)

VARIANT = os.getenv("VARIANT", "clean")


@pytest.fixture
def alembic_config() -> Config:
    config = Config("alembic.ini")
    config.set_main_option("version_locations", f"migrations/versions/{VARIANT}")
    return config
