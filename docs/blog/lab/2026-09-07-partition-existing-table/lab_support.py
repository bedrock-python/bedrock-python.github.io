"""A disposable database and checks shared by the migration and UUIDv7 labs."""
from contextlib import contextmanager
import json

import asyncpg
from testcontainers.community.postgres import PostgresContainer


@contextmanager
def database():
    with PostgresContainer("postgres:17-alpine", username="test", password="test", dbname="test", driver="asyncpg") as pg:
        engine_url = pg.get_connection_url()
        yield engine_url, engine_url.replace("postgresql+asyncpg://", "postgresql://", 1)


async def expect_sqlstate(connection, code, sql, *args):
    try:
        async with connection.transaction():
            await connection.execute(sql, *args)
    except asyncpg.PostgresError as error:
        assert error.sqlstate == code, error
    else:
        raise AssertionError(f"Expected SQLSTATE {code}")


async def scanned_relations(connection, sql, *args):
    plan = json.loads(await connection.fetchval(f"EXPLAIN (FORMAT JSON) {sql}", *args))
    def names(node):
        result = {node["Relation Name"]} if "Relation Name" in node else set()
        for child in node.get("Plans", []):
            result.update(names(child))
        return result
    return names(plan[0]["Plan"])
