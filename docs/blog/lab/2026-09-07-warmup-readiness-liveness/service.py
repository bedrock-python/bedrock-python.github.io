"""Add mandatory Redis readiness to the reports service. Redis represents its job state store."""
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / '2026-09-07-one-lifecycle'))
from one_lifecycle import Container, StoreWarmer, make_spec, router
from redis.asyncio import Redis
from servicewright import AsyncWarmer, Service
from servicewright.adapters.fastapi import FastApiEntrypoint, HttpConfig


# snippet:redis_check
from redis.exceptions import RedisError
from servicewright import HealthRegistry


class RedisReady:
    def __init__(self, redis):
        self.redis = redis

    async def check(self) -> bool:
        try:
            async with asyncio.timeout(0.25):
                return bool(await self.redis.ping())
        except (RedisError, TimeoutError):
            return False


def redis_health(redis):
    health = HealthRegistry()
    health.add_check('job-state', RedisReady(redis))
    return health
# /snippet:redis_check


class RedisWarmer(AsyncWarmer):
    def __init__(self, redis):
        super().__init__()
        self.redis = redis

    async def warmup(self):
        async with asyncio.timeout(1):
            await self.redis.ping()


class RedisContainer(Container):
    def __init__(self, url, store):
        super().__init__(store)
        self.redis = Redis.from_url(url, socket_timeout=0.2, socket_connect_timeout=0.2)
        self.closed = False

    @asynccontextmanager
    async def app_scope(self):
        try:
            async with self.redis:
                async with super().app_scope() as scope:
                    yield scope
        finally:
            self.closed = True


def build_health_service(url, store):
    container = RedisContainer(url, store)
    spec = make_spec(container)
    spec.health = redis_health(container.redis)
    spec.warmers = [StoreWarmer(store), RedisWarmer(container.redis)]
    api = FastApiEntrypoint(config=HttpConfig(host='127.0.0.1', port=0), routers=(router,))
    return Service(spec, entrypoints=[api]), api, container
