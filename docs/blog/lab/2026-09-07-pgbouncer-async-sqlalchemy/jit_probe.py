import asyncio
from pydantic import SecretStr
from sqlalchemy import text
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.waiting_utils import wait_for_logs
from testcontainers.postgres import PostgresContainer
from sqlalchemy_foundation_kit import create_async_session_manager
from sqlalchemy_foundation_kit.contrib.settings import BasePostgresConfig, ConnectionSettings

async def probe(host, port, label):
    config = BasePostgresConfig(connection=ConnectionSettings(host=host, port=int(port), user="test", password=SecretStr("test"), database="test"),
                                application_name="probe", db_schema="app", use_orjson_serialization=False)
    m = create_async_session_manager(config)
    async with m.get_session() as s:
        jit = (await s.execute(text("SHOW jit"))).scalar(); sp = (await s.execute(text("SHOW search_path"))).scalar(); an = (await s.execute(text("SHOW application_name"))).scalar()
    print(f"  {label:<48} jit={jit!r} search_path={sp!r} application_name={an!r}")
    await m.aclose()

with Network() as net, PostgresContainer("postgres:17-alpine", username="test", password="test", dbname="test").with_network(net).with_network_aliases("db") as pg:
    d = pg.get_connection_url().split("@")[1].split("/")[0].split(":")
    b = DockerContainer("edoburu/pgbouncer:latest").with_exposed_ports(5432).with_network(net)
    for k, v in {"DB_HOST": "db", "DB_USER": "test", "DB_PASSWORD": "test", "DB_NAME": "test", "POOL_MODE": "transaction", "AUTH_TYPE": "scram-sha-256", "IGNORE_STARTUP_PARAMETERS": "jit,search_path"}.items():
        b = b.with_env(k, v)
    b.start(); wait_for_logs(b, "process up", timeout=30)
    try:
        asyncio.run(probe(d[0], d[1], "direct to PostgreSQL"))
        asyncio.run(probe(b.get_container_host_ip(), b.get_exposed_port(5432), "PgBouncer, ignore_startup_parameters=jit,search_path"))
    finally:
        b.stop()
