"""PING is not the whole story: three Redis servers that answer PONG, and what a write probe says."""

import asyncio
import time

from redis.asyncio import Redis
from redis.exceptions import ReadOnlyError, ResponseError
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.waiting_utils import wait_for_logs

from redis_client_kit import check_async_redis_health, create_async_redis_client
from redis_client_kit.settings import BaseRedisSettings, RedisConnectionSettings, RedisPoolSettings


def start_redis(network, alias: str, *args: str) -> DockerContainer:
    c = DockerContainer("redis:7-alpine").with_exposed_ports(6379).with_network(network).with_network_aliases(alias).with_command(f"redis-server {' '.join(args)}")
    c.start()
    wait_for_logs(c, "Ready to accept connections", timeout=30)
    return c


def client_for(c: DockerContainer) -> Redis:
    return create_async_redis_client(BaseRedisSettings(key_prefix="shop", connection=RedisConnectionSettings(host=c.get_container_host_ip(), port=int(c.get_exposed_port(6379))),
                                                       pool=RedisPoolSettings(socket_timeout=0.5, socket_connect_timeout=0.5)))


async def probe(label: str, redis: Redis) -> None:
    started = time.perf_counter()
    ping = await check_async_redis_health(redis)                            # the default: PING
    ping_ms = (time.perf_counter() - started) * 1000
    started = time.perf_counter()
    write = await check_async_redis_health(redis, write_key="shop:health")  # opt-in: PING, then SET
    write_ms = (time.perf_counter() - started) * 1000
    try:
        await redis.set("shop:health-probe", "1", ex=5)
        value = await redis.get("shop:health-probe")
        raw = "ok" if value == b"1" else f"read back {value!r}"
    except (ResponseError, ReadOnlyError) as error:
        raw = f"{type(error).__name__}: {str(error)[:52]}"
    print(f"  {label:<42} PING health={ping!s:<6} ({ping_ms:6.1f} ms)   "
          f"write_key health={write!s:<6} ({write_ms:6.1f} ms)   a plain SET: {raw}")


async def main(primary, full, replica) -> None:
    healthy = client_for(primary)
    print("--- a healthy primary ---")
    await probe("primary", healthy)

    print("\n--- a primary at maxmemory with noeviction ---")
    stuffed = client_for(full)
    try:
        for i in range(2000):
            await stuffed.set(f"fill:{i}", "x" * 4096)
    except ResponseError:
        pass                                              # it is full now
    await probe("maxmemory 1mb, noeviction, full", stuffed)

    print("\n--- a read-only replica ---")
    rep = client_for(replica)
    await asyncio.sleep(1.0)
    await probe("replica of the primary", rep)

    print("\n--- the primary, paused ---")
    primary.get_wrapped_container().pause()
    started = time.perf_counter()
    ping = await check_async_redis_health(healthy)
    ping_ms = (time.perf_counter() - started) * 1000
    started = time.perf_counter()
    write = await check_async_redis_health(healthy, write_key="shop:health")
    print(f"  {'paused primary':<42} PING health={ping!s:<6} ({ping_ms:6.1f} ms)   "
          f"write_key health={write!s:<6} ({(time.perf_counter() - started) * 1000:6.1f} ms)")
    primary.get_wrapped_container().unpause()
    for c in (healthy, stuffed, rep):
        await c.aclose()


with Network() as net:
    primary = start_redis(net, "primary")
    full = start_redis(net, "full", "--maxmemory", "1mb", "--maxmemory-policy", "noeviction")
    replica = start_redis(net, "replica", "--replicaof", "primary", "6379")
    try:
        asyncio.run(main(primary, full, replica))
    finally:
        for c in (replica, full, primary):
            c.stop()
