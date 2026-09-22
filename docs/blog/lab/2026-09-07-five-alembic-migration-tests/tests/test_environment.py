"""The standalone Alembic path must commit the same DDL as the injected path."""
import asyncio
import os
import sys

from sqlalchemy import text

from tests.helpers import current_revision, fresh_schema


async def test_standalone_env_commits(migration_engine, migration_db_url, alembic_config):
    async with fresh_schema(migration_engine) as schema:
        # Execute Alembic in another process: env.py must create its own engine here.
        script = (
            "import os; from alembic import command; from alembic.config import Config; "
            "config=Config('alembic.ini'); "
            "config.set_main_option('sqlalchemy.url', os.environ['LAB_DATABASE_URL']); "
            "config.set_main_option('version_locations', os.environ['LAB_VERSIONS']); "
            "command.upgrade(config, 'head')"
        )
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-c", script,
            env={**os.environ, "MIGRATION_SCHEMA": schema, "LAB_DATABASE_URL": migration_db_url,
                 "LAB_VERSIONS": alembic_config.get_main_option("version_locations")},
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        try:
            async with asyncio.timeout(30):
                stdout, stderr = await process.communicate()
        except BaseException:
            if process.returncode is None:
                process.kill()
                await process.communicate()
            raise
        assert process.returncode == 0, (stdout + stderr).decode(errors="replace")
        assert await current_revision(migration_engine, schema) == "0004"
        async with migration_engine.connect() as connection:
            names = (await connection.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema=:schema"
            ), {"schema": schema})).scalars().all()
        assert set(names) == {"alembic_version", "users", "orders"}
