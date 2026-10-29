"""Disposable PostgreSQL/PgBouncer setup and controlled workload helpers."""
import asyncio
from configparser import ConfigParser
from contextlib import ExitStack
import csv
from io import StringIO
from pathlib import Path

from sqlalchemy import text
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.wait_strategies import LogMessageWaitStrategy
from testcontainers.postgres import PostgresContainer

from pool_flow import database_config

PGBOUNCER_IMAGE = "edoburu/pgbouncer:v1.25.2-p0"


class Bouncer:
    def __init__(self, container):
        self.container = container
        self.host = container.get_container_host_ip()
        self.port = int(container.get_exposed_port(5432))
        self.dsn = f"postgresql://test:test@{self.host}:{self.port}/test"

    def config(self):
        return database_config(self.host, self.port, "test", "test", "test")

    def admin(self, statement):
        # psql uses the simple-query protocol required by the admin console.
        result = self.container.exec([
            "psql", "-h", "127.0.0.1", "-U", "test", "-d", "pgbouncer",
            "--csv", "-c", statement,
        ])
        assert result.exit_code == 0, result.output.decode()
        return list(csv.DictReader(StringIO(result.output.decode())))


class DatabaseLab:
    def __enter__(self):
        self.stack = ExitStack()
        try:
            self.network = self.stack.enter_context(Network())
            self.pg = self.stack.enter_context(
                PostgresContainer("postgres:17-alpine", username="test", password="test", dbname="test", driver="asyncpg")
                .with_network(self.network).with_network_aliases("db")
            )
            return self
        except BaseException:
            self.stack.close()
            raise

    def __exit__(self, *args):
        return self.stack.__exit__(*args)

    def direct_config(self):
        return database_config(self.pg.get_container_host_ip(), int(self.pg.get_exposed_port(5432)), "test", "test", "test")

    def bouncer(self, **overrides):
        settings = ConfigParser()
        settings.read(Path(__file__).with_name("pgbouncer-settings.ini"), encoding="utf-8")
        environment = {
            "DB_HOST": "db", "DB_PORT": "5432", "DB_USER": "test", "DB_PASSWORD": "test", "DB_NAME": "test",
            "AUTH_TYPE": "scram-sha-256", "ADMIN_USERS": "test", "PGPASSWORD": "test",
            **{key.upper(): value for key, value in settings["pgbouncer"].items()},
            **{key.upper(): str(value) for key, value in overrides.items()},
        }
        container = DockerContainer(PGBOUNCER_IMAGE).with_network(self.network).with_exposed_ports(5432)
        for key, value in environment.items():
            container.with_env(key, value)
        container.waiting_for(LogMessageWaitStrategy("process up").with_startup_timeout(30))
        self.stack.enter_context(container)
        return Bouncer(container)


async def seed(manager):
    async with manager.engine.begin() as connection:
        await connection.execute(text("CREATE SCHEMA IF NOT EXISTS app"))
        await connection.execute(text("CREATE TABLE IF NOT EXISTS app.orders (id integer PRIMARY KEY, total integer NOT NULL)"))
        await connection.execute(text("INSERT INTO app.orders VALUES (42, 1999) ON CONFLICT DO NOTHING"))


async def wait_until(predicate, timeout=5):
    async with asyncio.timeout(timeout):
        while not predicate():
            await asyncio.sleep(0.02)


class Shipping:
    def __init__(self):
        self.started = asyncio.Event()
        self.release = asyncio.Event()

    async def quote(self, order_id):
        self.started.set()
        await self.release.wait()
        return 350
