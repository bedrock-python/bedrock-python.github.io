"""The five checks, written against Alembic's own API. Each one is a few lines once the plumbing exists."""

import re

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

from shop.models import Base
from tests.helpers import current_revision, fresh_schema, migrate, revisions_base_to_head


async def test_every_revision_up_down_up(migration_engine: AsyncEngine, alembic_config: Config) -> None:
    """The stairway: each revision applied, rolled back one step, applied again."""
    revisions = revisions_base_to_head(alembic_config)
    async with fresh_schema(migration_engine) as schema:
        for i, revision in enumerate(revisions):
            await migrate(migration_engine, alembic_config, schema, command.upgrade, revision)
            assert await current_revision(migration_engine, schema) == revision
            await migrate(migration_engine, alembic_config, schema, command.downgrade, revisions[i - 1] if i else "base")
            await migrate(migration_engine, alembic_config, schema, command.upgrade, revision)


async def test_schema_matches_the_models(migration_engine: AsyncEngine, alembic_config: Config) -> None:
    """After a full upgrade, autogenerate would have nothing to say."""

    def diff(conn: Connection) -> list[object]:
        conn.execute(text(f'SET LOCAL search_path TO "{schema}"'))
        ctx = MigrationContext.configure(conn, opts={"version_table_schema": schema})
        return [item for item in compare_metadata(ctx, Base.metadata) if not is_the_version_table(item)]

    async with fresh_schema(migration_engine) as schema:
        await migrate(migration_engine, alembic_config, schema, command.upgrade, "head")
        async with migration_engine.connect() as conn:
            assert await conn.run_sync(diff) == []


def is_the_version_table(item: object) -> bool:
    ops = item if isinstance(item, list) else [item]
    return all(op[0] == "remove_table" and op[1].name == "alembic_version" for op in ops)


def test_exactly_one_head(alembic_config: Config) -> None:
    """Two heads means two branches merged without `alembic merge`; nothing else runs until this is one."""
    assert len(ScriptDirectory.from_config(alembic_config).get_heads()) == 1


async def test_downgrade_to_base(migration_engine: AsyncEngine, alembic_config: Config) -> None:
    """The emergency rollback: head to nothing, and the version table agrees."""
    async with fresh_schema(migration_engine) as schema:
        await migrate(migration_engine, alembic_config, schema, command.upgrade, "head")
        await migrate(migration_engine, alembic_config, schema, command.downgrade, "base")
        assert await current_revision(migration_engine, schema) is None


NAME_RULES = {"pk": r"^pk_", "fk": r"^fk_", "uq": r"^uq_", "ck": r"^chk_", "ix": r"^idx_"}


async def test_names_follow_the_convention(migration_engine: AsyncEngine, alembic_config: Config) -> None:
    """Every constraint and index the migrations created is named the way the convention says."""

    def offenders(conn: Connection) -> list[str]:
        insp = inspect(conn)
        bad = []
        for table in insp.get_table_names(schema=schema):
            if table == "alembic_version":
                continue
            named = [("pk", insp.get_pk_constraint(table, schema=schema)["name"])]
            named += [("fk", fk["name"]) for fk in insp.get_foreign_keys(table, schema=schema)]
            named += [("uq", uq["name"]) for uq in insp.get_unique_constraints(table, schema=schema)]
            named += [("ck", ck["name"]) for ck in insp.get_check_constraints(table, schema=schema)]
            named += [("ix", ix["name"]) for ix in insp.get_indexes(table, schema=schema) if not ix.get("duplicates_constraint")]
            bad += [f"{table}.{name}" for kind, name in named if not re.match(NAME_RULES[kind], name or "")]
        return bad

    async with fresh_schema(migration_engine) as schema:
        await migrate(migration_engine, alembic_config, schema, command.upgrade, "head")
        async with migration_engine.connect() as conn:
            assert await conn.run_sync(offenders) == []
