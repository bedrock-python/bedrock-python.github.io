"""How long a GET takes to fail against a paused Redis, per client configuration."""

import asyncio
import time

from redis.asyncio import Redis
from redis.asyncio.retry import Retry
from redis.backoff import NoBackoff
from testcontainers.redis import RedisContainer

from redis_client_kit import create_async_redis_client
from redis_client_kit.settings import BaseRedisSettings, RedisConnectionSettings, RedisPoolSettings, RedisRetrySettings


async def timed(label: str, coro, cap: float = 20.0) -> None:
    started = time.perf_counter()
    try:
        result = await asyncio.wait_for(coro, timeout=cap)
        print(f"  {label:<58} -> {result!s:<20} {time.perf_counter() - started:6.2f} s")
    except asyncio.TimeoutError:
        print(f"  {label:<58} -> {'still waiting':<20} {time.perf_counter() - started:6.2f} s  (gave up watching)")
    except Exception as error:  # noqa: BLE001
        print(f"  {label:<58} -> {type(error).__name__:<20} {time.perf_counter() - started:6.2f} s")


async def main(host: str, port: int, wrapped) -> None:
    fast = RedisPoolSettings(socket_timeout=0.5, socket_connect_timeout=0.5)
    clients = {
        "bare redis-py, defaults": Redis(host=host, port=port),
        "bare redis-py, timeouts 0.5 + Retry(NoBackoff(), 0)": Redis(host=host, port=port, socket_timeout=0.5, socket_connect_timeout=0.5, retry=Retry(NoBackoff(), 0)),
        "kit, timeouts 0.5, retry settings default": create_async_redis_client(BaseRedisSettings(key_prefix="s", connection=RedisConnectionSettings(host=host, port=port), pool=fast)),
        "kit, timeouts 0.5, retry.enabled=False explicitly": create_async_redis_client(BaseRedisSettings(key_prefix="s", connection=RedisConnectionSettings(host=host, port=port), pool=fast, retry=RedisRetrySettings(enabled=False, max_attempts=0))),
    }
    for label, client in clients.items():
        retry = client.connection_pool.connection_kwargs.get("retry")
        print(f"  {label:<58} retry handed to redis-py: {type(retry).__name__} retries={getattr(retry, '_retries', None)} backoff={type(getattr(retry, '_backoff', None)).__name__}")
        await client.ping()
    wrapped.pause()
    print("--- Redis paused: one GET per client ---")
    for label, client in clients.items():
        await timed(label, client.get("k"))
    wrapped.unpause()
    for client in clients.values():
        await client.aclose()


with RedisContainer("redis:7-alpine") as container:
    asyncio.run(main(container.get_container_host_ip(), int(container.get_exposed_port(6379)), container.get_wrapped_container()))
