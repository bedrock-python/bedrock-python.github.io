"""Plumbing shared by the hand-written tests: a throwaway schema, and Alembic driven on an injected connection."""

import uuid
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine


@asynccontextmanager
async def fresh_schema(engine: AsyncEngine) -> AsyncIterator[str]:
    """One empty schema per test, dropped with everything in it afterwards."""
    name = f"lab_{uuid.uuid4().hex[:8]}"
    async with engine.begin() as conn:
        await conn.execute(text(f'CREATE SCHEMA "{name}"'))
    try:
        yield name
    finally:
        async with engine.begin() as conn:
            await conn.execute(text(f'DROP SCHEMA "{name}" CASCADE'))


async def migrate(
    engine: AsyncEngine, config: Config, schema: str, direction: Callable[[Config, str], None], revision: str
) -> None:
    """Run `alembic upgrade`/`downgrade` in-process, in one transaction, in the given schema.

    env.py reads the two attributes; see migrations/env.py.
    """

    def run(conn: Connection) -> None:
        config.attributes["connection"] = conn
        config.attributes["target_schema"] = schema
        try:
            direction(config, revision)
        finally:
            config.attributes.pop("connection", None)
            config.attributes.pop("target_schema", None)

    async with engine.begin() as conn:
        await conn.run_sync(run)


async def current_revision(engine: AsyncEngine, schema: str) -> str | None:
    async with engine.connect() as conn:
        return await conn.run_sync(
            lambda c: MigrationContext.configure(c, opts={"version_table_schema": schema}).get_current_revision()
        )


def revisions_base_to_head(config: Config) -> list[str]:
    script = ScriptDirectory.from_config(config)
    return [rev.revision for rev in reversed(list(script.walk_revisions()))]
