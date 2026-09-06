"""The five tests, inherited."""

import pytest
from alembic_gauntlet import MigrationTestBase
from sqlalchemy import MetaData

from shop.models import Base


@pytest.mark.integration
class TestMigrations(MigrationTestBase):
    @pytest.fixture
    def orm_metadata(self) -> MetaData:
        return Base.metadata
