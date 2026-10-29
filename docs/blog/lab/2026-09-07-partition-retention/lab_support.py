"""Disposable PostgreSQL and assertions for the maintenance labs."""
from contextlib import contextmanager
import asyncpg
from testcontainers.community.postgres import PostgresContainer


@contextmanager
def database(image="postgres:17-alpine"):
    with PostgresContainer(image, username="test", password="test", dbname="test", driver="asyncpg") as pg:
        url = pg.get_connection_url()
        yield url, url.replace("postgresql+asyncpg://", "postgresql://", 1)


async def relations(connection):
    return await connection.fetch("""
        SELECT c.oid, c.relname, pg_get_expr(c.relpartbound, c.oid) AS bounds
        FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND c.relkind IN ('r', 'p') ORDER BY c.relname
    """)


async def expect_sqlstate(connection, sqlstate, sql, *args):
    try:
        async with connection.transaction():
            await connection.execute(sql, *args)
    except asyncpg.PostgresError as error:
        assert error.sqlstate == sqlstate, error
    else:
        raise AssertionError(f"Expected SQLSTATE {sqlstate}")
