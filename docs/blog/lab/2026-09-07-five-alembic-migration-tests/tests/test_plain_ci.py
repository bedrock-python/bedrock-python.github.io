"""What most pipelines do: apply the migrations once, on an empty database, and call it tested."""

from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncEngine

from tests.helpers import fresh_schema, migrate


async def test_upgrade_head(migration_engine: AsyncEngine, alembic_config: Config) -> None:
    async with fresh_schema(migration_engine) as schema:
        await migrate(migration_engine, alembic_config, schema, command.upgrade, "head")
