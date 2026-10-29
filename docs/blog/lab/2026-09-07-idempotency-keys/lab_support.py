"""Fault fixtures: Redis is real; payment and mail providers are local simulations."""
import asyncio
from contextlib import asynccontextmanager
from uuid import uuid4

from redis.asyncio import Redis
from testcontainers.community.redis import RedisContainer

from payment_flow import Charge, Payment


def payment():
    return Payment(tenant_id=uuid4(), order_id=uuid4(), amount=1999)


class Provider:
    def __init__(self, *, deduplicate=False, fail_after_effect=False):
        self.deduplicate = deduplicate
        self.fail_after_effect = fail_after_effect
        self.calls = 0
        self.effects = []
        self.saved = {}

    async def charge(self, request, key):
        self.calls += 1
        payload = request.model_dump(mode="json")
        if self.deduplicate and key in self.saved:
            previous, result = self.saved[key]
            assert previous == payload, "Provider key reused with different parameters"
            return result
        result = Charge(charge_id=f"ch_{len(self.effects) + 1}", amount=request.amount)
        self.effects.append(result)
        self.saved[key] = (payload, result)
        if self.fail_after_effect:
            self.fail_after_effect = False
            raise ConnectionError("Provider accepted the charge; its response was lost")
        return result


class BlockingProvider(Provider):
    def __init__(self):
        super().__init__()
        self.started = asyncio.Event()
        self.both_started = asyncio.Event()
        self.release = asyncio.Event()
        self.entered = 0

    async def charge(self, request, key):
        self.entered += 1
        self.started.set()
        if self.entered == 2:
            self.both_started.set()
        await self.release.wait()
        return await super().charge(request, key)


@asynccontextmanager
async def redis_client(url):
    async with Redis.from_url(url, socket_connect_timeout=0.5, socket_timeout=0.5) as redis:
        await redis.ping()
        yield redis


def run(main):
    with RedisContainer("redis:7-alpine") as container:
        url = f"redis://{container.get_container_host_ip()}:{container.get_exposed_port(6379)}"

        async def bounded():
            async with asyncio.timeout(45):
                await main(url)

        asyncio.run(bounded())
