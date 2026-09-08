"""Three drifts autogenerate does not report, and the checks that do."""

from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import CheckConstraint, Enum, inspect, text
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

from shop.models import Base
from tests.helpers import fresh_schema, migrate


async def test_server_defaults_match(migration_engine: AsyncEngine, alembic_config: Config) -> None:
    """compare_metadata skips server defaults unless asked; ask."""

    def diff(conn: Connection) -> list[object]:
        conn.execute(text(f'SET LOCAL search_path TO "{schema}"'))
        ctx = MigrationContext.configure(conn, opts={"version_table_schema": schema, "compare_server_default": True})
        return [d for d in compare_metadata(ctx, Base.metadata) if str(d).find("alembic_version") < 0]

    async with fresh_schema(migration_engine) as schema:
        await migrate(migration_engine, alembic_config, schema, command.upgrade, "head")
        async with migration_engine.connect() as conn:
            assert await conn.run_sync(diff) == []


async def test_check_constraints_match(migration_engine: AsyncEngine, alembic_config: Config) -> None:
    """Autogenerate never compares CHECK constraints; reflect them and compare by name."""

    def offenders(conn: Connection) -> list[str]:
        insp = inspect(conn)
        bad = []
        for table in Base.metadata.sorted_tables:
            expected = {c.name for c in table.constraints if isinstance(c, CheckConstraint)}
            expected = {table.metadata.naming_convention["ck"] % {"table_name": table.name, "constraint_name": n} if not str(n).startswith("chk_") else n for n in expected}
            actual = {c["name"] for c in insp.get_check_constraints(table.name, schema=schema)}
            bad += [f"{table.name}: missing {n}" for n in expected - actual] + [f"{table.name}: unexpected {n}" for n in actual - expected]
        return bad

    async with fresh_schema(migration_engine) as schema:
        await migrate(migration_engine, alembic_config, schema, command.upgrade, "head")
        async with migration_engine.connect() as conn:
            assert await conn.run_sync(offenders) == []


async def test_enum_values_match(migration_engine: AsyncEngine, alembic_config: Config) -> None:
    """Autogenerate does not compare enum members; read pg_enum and compare."""

    def offenders(conn: Connection) -> list[str]:
        bad = []
        for table in Base.metadata.sorted_tables:
            for column in table.columns:
                if isinstance(column.type, Enum) and column.type.name:
                    rows = conn.execute(text("SELECT e.enumlabel FROM pg_enum e JOIN pg_type t ON t.oid = e.enumtypid "
                                             "JOIN pg_namespace n ON n.oid = t.typnamespace WHERE t.typname = :t AND n.nspname = :s ORDER BY e.enumsortorder"),
                                        {"t": column.type.name, "s": schema}).scalars().all()
                    if list(rows) != list(column.type.enums):
                        bad.append(f"{column.type.name}: database {list(rows)} model {list(column.type.enums)}")
        return bad

    async with fresh_schema(migration_engine) as schema:
        await migrate(migration_engine, alembic_config, schema, command.upgrade, "head")
        async with migration_engine.connect() as conn:
            assert await conn.run_sync(offenders) == []
