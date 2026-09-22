"""Prove that ignored startup parameters are dropped rather than applied."""
import asyncio
import asyncpg
from sqlalchemy_foundation_kit import create_async_session_manager

from lab_support import DatabaseLab, seed
from pool_flow import effective_settings


async def raw_settings(dsn, settings):
    connection = await asyncpg.connect(dsn, statement_cache_size=0, server_settings=settings)
    try:
        async with connection.transaction():
            return {name: await connection.fetchval(f"SHOW {name}") for name in ("jit", "search_path", "application_name")}
    finally:
        await connection.close()


async def main(lab, strict, ignoring):
    async with asyncio.timeout(25):
        direct = lab.direct_config()
        async with create_async_session_manager(direct) as manager:
            await seed(manager)
        settings = {"jit": "off", "search_path": "app", "application_name": "startup-probe"}
        actual = await raw_settings(direct.to_dsn(driver=None), settings)
        assert actual == {"jit": "off", "search_path": "app", "application_name": "startup-probe"}
        print("PASS direct startup: jit=off, search_path=app")
        try:
            await raw_settings(strict.dsn, settings)
        except asyncpg.PostgresError as error:
            assert "unsupported startup parameter" in str(error)
        else:
            raise AssertionError("Strict PgBouncer must reject unsupported startup settings")
        actual = await raw_settings(ignoring.dsn, settings)
        baseline = await raw_settings(direct.to_dsn(driver=None), {"application_name": "baseline"})
        assert actual["jit"] == baseline["jit"] == "on"
        assert actual["search_path"] == baseline["search_path"] != "app"
        assert actual["application_name"] == "startup-probe"
        print(f"PASS ignored startup: jit={actual['jit']}, search_path={actual['search_path']!r}; application_name kept")

        async with create_async_session_manager(strict.config()) as manager:
            actual = await effective_settings(manager)
            assert actual == {"jit": "on", "search_path": "app", "application_name": "orders-api"}
        print("PASS kit config: no jit startup parameter; schema applied inside each transaction")


if __name__ == "__main__":
    with DatabaseLab() as lab:
        strict = lab.bouncer()
        ignoring = lab.bouncer(ignore_startup_parameters="jit,search_path")
        asyncio.run(main(lab, strict, ignoring))
