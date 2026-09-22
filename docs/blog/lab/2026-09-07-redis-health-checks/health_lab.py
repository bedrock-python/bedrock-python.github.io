"""Verify PING, write capability, application policy and recovery on real Redis."""

import asyncio
from contextlib import ExitStack
import logging
from pathlib import Path
import sys

from redis.exceptions import ReadOnlyError, ResponseError
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network
from testcontainers.core.wait_strategies import LogMessageWaitStrategy

# Reuse exactly the functions printed in the article.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "2026-09-07-when-should-redis-fail-open"))
from shop import make_redis, redis_health, product_price, allow_login, pay_order, ServiceUnavailable
from fail_open_lab import Catalog, PaymentProvider, expect_error, wait_ready


def start_redis(stack, network, alias, *args):
    container = (
        DockerContainer("redis:7-alpine")
        .with_exposed_ports(6379)
        .with_network(network)
        .with_network_aliases(alias)
        .with_command("redis-server " + " ".join(args))
        .waiting_for(LogMessageWaitStrategy("Ready to accept connections"))
    )
    stack.callback(container.stop)
    container.start()
    return container


def client_for(container):
    return make_redis(container.get_container_host_ip(), int(container.get_exposed_port(6379)))


async def probe(label, redis, expected_ping, expected_write):
    ping = await redis_health(redis)
    write = await redis_health(redis, require_write=True)
    assert (ping, write) == (expected_ping, expected_write), (label, ping, write)
    print(f"{label}: PING={ping}, PING+SET={write}")


async def rejected_writes(redis, error_type):
    await expect_error(error_type, redis.set("shop:direct-write", "1", ex=5))
    catalog, provider = Catalog(), PaymentProvider()
    assert await product_price(redis, catalog.load_price, "uncached-sku") == "9.99"
    assert catalog.reads == 1
    await expect_error(ServiceUnavailable, allow_login(redis, "alice"))
    await expect_error(ServiceUnavailable, pay_order(redis, provider.charge, "order-1", 999))
    assert not provider.charges


async def main(primary, full, replica):
    healthy, stuffed, rep = [client_for(container) for container in (primary, full, replica)]
    try:
        for client in (healthy, stuffed, rep):
            await wait_ready(client)
        print("Redis", (await healthy.info("server"))["redis_version"])
        await probe("primary", healthy, True, True)
        assert await healthy.get("shop:health:write") == "1"
        assert 0 < await healthy.ttl("shop:health:write") <= 60

        # Set maxmemory below current usage: deterministic OOM without a fill loop.
        used = int((await stuffed.info("memory"))["used_memory"])
        await stuffed.config_set("maxmemory", max(1, used // 2))
        await probe("noeviction, memory limit reached", stuffed, True, False)
        await rejected_writes(stuffed, ResponseError)
        await stuffed.config_set("maxmemory", 0)
        await probe("memory limit removed, same client", stuffed, True, True)

        # Wait for replication instead of relying on a fixed sleep.
        async with asyncio.timeout(15):
            while (await rep.info("replication"))["master_link_status"] != "up":
                await asyncio.sleep(0.1)
        await probe("read-only replica", rep, True, False)
        await rejected_writes(rep, ReadOnlyError)

        wrapped = primary.get_wrapped_container()
        wrapped.pause()
        try:
            await probe("paused primary", healthy, False, False)
        finally:
            wrapped.unpause()
        await probe("resumed primary, same client", healthy, True, True)
        print("write refusals: catalog falls back, login/payment stop, no charge")
    finally:
        for client in (healthy, stuffed, rep):
            await client.aclose()


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    with ExitStack() as stack:
        network = stack.enter_context(Network())
        primary = start_redis(stack, network, "primary", "--save", '""', "--appendonly", "no")
        full = start_redis(stack, network, "full", "--maxmemory-policy", "noeviction")
        replica = start_redis(stack, network, "replica", "--replicaof", "primary", "6379")
        asyncio.run(main(primary, full, replica))
    print("PASS: Redis health scenarios")
