"""Compare one attempt, retries, and a total budget against a paused Redis."""

import asyncio
import logging
import time

from redis_client_kit import create_async_redis_client
from redis_client_kit.settings import (
    BaseRedisSettings, RedisConnectionSettings, RedisPoolSettings, RedisRetrySettings,
)
from testcontainers.community.redis import RedisContainer

from shop import REDIS_FAILURES, make_redis, redis_call
from fail_open_lab import wait_ready


async def main(container):
    host, port = container.get_container_host_ip(), int(container.get_exposed_port(6379))
    single = make_redis(host, port)
    retried = create_async_redis_client(BaseRedisSettings(
        key_prefix="shop",
        connection=RedisConnectionSettings(host=host, port=port),
        pool=RedisPoolSettings(socket_timeout=0.1, socket_connect_timeout=0.1),
        retry=RedisRetrySettings(enabled=True, max_attempts=2, backoff_base=0, backoff_cap=0),
        health_check_interval=0,
    ))
    try:
        await wait_ready(single)
        await wait_ready(retried)
        wrapped = container.get_wrapped_container()
        wrapped.pause()
        try:
            for label, client, bounded in (
                ("one attempt", single, False),
                ("two retries, no total", retried, False),
                ("two retries, 0.15s total", retried, True),
            ):
                started = time.perf_counter()
                try:
                    async with asyncio.timeout(3):
                        command = client.get("shop:probe")
                        await (redis_call(command) if bounded else command)
                except REDIS_FAILURES as error:
                    elapsed = time.perf_counter() - started
                    assert elapsed < 2, "The probe hit its watchdog instead of failing promptly"
                    print(f"{label}: {type(error).__name__}, {elapsed:.3f}s")
                else:
                    raise AssertionError("A paused Redis unexpectedly answered")
        finally:
            wrapped.unpause()
        assert await single.ping()
        assert await retried.ping()
    finally:
        await single.aclose()
        await retried.aclose()


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    with RedisContainer("redis:7-alpine") as container:
        asyncio.run(main(container))
    print("PASS: retry and timeout probe")
