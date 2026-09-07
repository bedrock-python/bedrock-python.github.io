"""When Redis is gone: what each use of it should do, and how long deciding takes."""

import asyncio
import logging
import time

from pydantic import BaseModel
from redis.asyncio import Redis
from redis.exceptions import ConnectionError, TimeoutError as RedisTimeoutError
from testcontainers.redis import RedisContainer

from idempotency_kit import AsyncIdempotencyCoordinator, IdempotencyDomainService, PydanticResultAdapter
from idempotency_kit.infra.storage.redis.aio import RedisAsyncIdempotencyRepository
from redis_client_kit import check_async_redis_health, close_async_redis_client, create_async_redis_client
from redis_client_kit.settings import BaseRedisSettings, RedisConnectionSettings, RedisPoolSettings

logging.disable(logging.CRITICAL)


class Charge(BaseModel):
    charge_id: str


charges = 0


async def charge_card(amount: int) -> Charge:
    global charges
    charges += 1
    return Charge(charge_id=f"ch_{charges}")


async def timed(label: str, coro, cap: float = 3.0) -> None:
    started = time.perf_counter()
    try:
        result = await asyncio.wait_for(coro, timeout=cap)
        print(f"  {label:<52} -> {result!s:<28} {time.perf_counter() - started:6.2f} s")
    except asyncio.TimeoutError:
        print(f"  {label:<52} -> {'still waiting':<28} {time.perf_counter() - started:6.2f} s  (gave up watching)")
    except (ConnectionError, RedisTimeoutError) as error:
        print(f"  {label:<52} -> {type(error).__name__:<28} {time.perf_counter() - started:6.2f} s")


async def cached_price(redis: Redis, sku: str) -> str:
    """A cache that fails open: Redis trouble costs the lookup, never the request."""
    try:
        hit = await redis.get(f"price:{sku}")
        if hit:
            return f"hit {hit.decode()}"
    except (ConnectionError, RedisTimeoutError):
        return "computed (cache unavailable)"
    await asyncio.sleep(0.05)  # the expensive computation
    try:
        await redis.set(f"price:{sku}", "9.99", ex=60)
    except (ConnectionError, RedisTimeoutError):
        pass
    return "computed"


async def rate_limited(redis: Redis, user: str, *, fail_open: bool) -> str:
    try:
        count = await redis.incr(f"rl:{user}")
        return "allowed" if count <= 100 else "denied"
    except (ConnectionError, RedisTimeoutError):
        return "allowed (limiter unavailable)" if fail_open else "denied (limiter unavailable)"


async def main(host: str, port: int, wrapped) -> None:
    settings = BaseRedisSettings(
        key_prefix="shop",
        connection=RedisConnectionSettings(host=host, port=port),
        pool=RedisPoolSettings(socket_timeout=0.5, socket_connect_timeout=0.5),   # the decision this post is about
    )
    kit = create_async_redis_client(settings)
    bare = Redis(host=host, port=port)   # redis-py's defaults: no socket timeout at all
    coordinator = AsyncIdempotencyCoordinator(RedisAsyncIdempotencyRepository(kit), IdempotencyDomainService())

    print("--- Redis is up ---")
    await timed("cache, first lookup", cached_price(kit, "sku-1"))
    await timed("cache, second lookup", cached_price(kit, "sku-1"))
    await timed("rate limiter", rate_limited(kit, "u1", fail_open=True))
    await timed("idempotent charge", coordinator.coordinate("payment.charge", "order-1", 3600, PydanticResultAdapter(Charge), charge_card, 10))
    await timed("health check", check_async_redis_health(kit))

    wrapped.pause()   # the box is there, the process is not answering: every packet goes into a hole
    print("\n--- Redis is paused: connections neither succeed nor fail ---")
    await timed("bare redis-py GET, no timeouts configured", bare.get("price:sku-1"))
    await timed("kit GET, socket_timeout=0.5", kit.get("price:sku-1"))
    await timed("cache lookup (fails open)", cached_price(kit, "sku-1"))
    await timed("rate limiter, fail_open=True", rate_limited(kit, "u1", fail_open=True))
    await timed("rate limiter, fail_open=False", rate_limited(kit, "u1", fail_open=False))
    before = charges
    await timed("idempotent charge, new key (fails open: runs)", coordinator.coordinate("payment.charge", "order-2", 3600, PydanticResultAdapter(Charge), charge_card, 10))
    await timed("idempotent charge, SAME key again (store gone)", coordinator.coordinate("payment.charge", "order-2", 3600, PydanticResultAdapter(Charge), charge_card, 10))
    print(f"  charges made while the store was gone: {charges - before}")
    await timed("health check", check_async_redis_health(kit))

    wrapped.unpause()
    print("\n--- Redis is back ---")
    await timed("kit GET, same client, no restart", kit.get("price:sku-1"))
    await timed("health check", check_async_redis_health(kit))
    await close_async_redis_client(kit)
    await bare.aclose()


with RedisContainer("redis:7-alpine") as container:
    asyncio.run(main(container.get_container_host_ip(), int(container.get_exposed_port(6379)), container.get_wrapped_container()))
