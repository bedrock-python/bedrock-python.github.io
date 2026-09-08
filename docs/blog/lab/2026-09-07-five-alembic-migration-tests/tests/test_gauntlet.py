"""The five tests, inherited, plus the two the 0.3.0 base class adds and the one it makes opt-in."""

import pytest
from alembic_gauntlet import MigrationTestBase
from sqlalchemy import MetaData

from shop.models import Base


@pytest.mark.integration
class TestMigrations(MigrationTestBase):
    # Server defaults are not compared unless asked, because a database that rewrites the
    # expression it was given reports a difference that is not one.
    migration_diff_compare_server_default = True

    @pytest.fixture
    def orm_metadata(self) -> MetaData:
        return Base.metadata
