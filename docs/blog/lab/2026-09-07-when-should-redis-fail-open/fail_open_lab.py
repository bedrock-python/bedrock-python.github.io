"""Exercise the article's functions against a real Redis, including failures."""

import asyncio
import logging
import socket
import time

from testcontainers.community.redis import RedisContainer

import shop


class Catalog:
    """Stand-in for PostgreSQL; count reads so a fallback is observable."""

    def __init__(self):
        self.reads = 0

    async def load_price(self, sku):
        self.reads += 1
        return "9.99"


class PaymentProvider:
    """In-memory test double, not a real payment integration or durable store."""

    def __init__(self):
        self.charges = {}

    async def charge(self, *, amount_minor, idempotency_key):
        if idempotency_key in self.charges:
            previous_amount, receipt = self.charges[idempotency_key]
            if amount_minor != previous_amount:
                raise ValueError("The same key cannot describe a different payment")
            return receipt
        receipt = f"charge-{len(self.charges) + 1}"
        self.charges[idempotency_key] = (amount_minor, receipt)
        return receipt


async def expect_error(kind, command):
    try:
        await command
    except kind:
        return
    raise AssertionError(f"Expected {kind.__name__}")


async def wait_ready(redis):
    """Wait for the Docker fixture before testing the application's tight budgets."""
    async with asyncio.timeout(10):
        while not await shop.redis_health(redis):
            await asyncio.sleep(0.05)


async def unavailable(redis, catalog, provider, label):
    started = time.perf_counter()
    before = catalog.reads
    assert await shop.product_price(redis, catalog.load_price, "sku-1") == "9.99"
    assert catalog.reads == before + 1
    await expect_error(shop.ServiceUnavailable, shop.allow_login(redis, "alice"))
    before = len(provider.charges)
    await expect_error(
        shop.ServiceUnavailable,
        shop.pay_order(redis, provider.charge, "order-outage", 999),
    )
    assert len(provider.charges) == before
    assert not await shop.redis_health(redis, require_write=True)
    elapsed = time.perf_counter() - started
    assert elapsed < 2.0, f"Failure handling stalled for {elapsed:.2f}s"
    print(f"{label}: DB fallback; login/payment refused; no new charge ({elapsed:.2f}s)")


async def main(container):
    redis = shop.make_redis(
        container.get_container_host_ip(), int(container.get_exposed_port(6379)),
    )
    catalog, provider = Catalog(), PaymentProvider()
    wrapped = container.get_wrapped_container()
    try:
        await wait_ready(redis)
        print("Redis", (await redis.info("server"))["redis_version"])
        assert await shop.product_price(redis, catalog.load_price, "sku-1") == "9.99"
        assert await shop.product_price(redis, catalog.load_price, "sku-1") == "9.99"
        assert catalog.reads == 1
        assert 0 < await redis.ttl("shop:price:sku-1") <= 60
        print("cache: two reads, one DB lookup, expiring cache entry")

        decisions = await asyncio.gather(
            *(shop.allow_login(redis, "alice") for _ in range(8)),
            return_exceptions=True,
        )
        assert decisions.count(None) == 5
        assert sum(isinstance(item, shop.TooManyRequests) for item in decisions) == 3
        assert 0 < await redis.pttl("shop:login:alice") <= 60_000
        # Shorten the fixture's TTL instead of waiting a minute.
        await redis.pexpire("shop:login:alice", 1)
        await asyncio.sleep(0.03)
        await shop.allow_login(redis, "alice")
        assert await redis.get("shop:login:alice") == "1"
        print("login: five admitted, three limited; next window admits again")

        results = await asyncio.gather(
            *(shop.pay_order(redis, provider.charge, "order-1", 999) for _ in range(2)),
            return_exceptions=True,
        )
        assert "charge-1" in results
        assert sum(isinstance(item, shop.PaymentBusy) for item in results) == 1
        await redis.pexpire("shop:payment:order-1", 1)
        await asyncio.sleep(0.03)
        assert await shop.pay_order(redis, provider.charge, "order-1", 999) == "charge-1"
        assert len(provider.charges) == 1
        print("payment: concurrent duplicate refused; retry after TTL returns same charge")

        # The provider commits a charge, but its response never reaches our handler.
        async def lost_response(**kwargs):
            await provider.charge(**kwargs)
            raise TimeoutError("Provider response lost after charge")

        await expect_error(TimeoutError, shop.pay_order(redis, lost_response, "order-2", 999))
        await redis.pexpire("shop:payment:order-2", 1)
        await asyncio.sleep(0.03)
        assert await shop.pay_order(redis, provider.charge, "order-2", 999) == "charge-2"
        assert len(provider.charges) == 2
        print("payment: lost response, same provider key, no second charge")

        wrapped.pause()
        try:
            await unavailable(redis, catalog, provider, "paused Redis")
            # Caller cancellation must not be converted into a cache fallback.
            before = catalog.reads
            task = asyncio.create_task(shop.product_price(redis, catalog.load_price, "sku-1"))
            await asyncio.sleep(0.02)
            task.cancel()
            await expect_error(asyncio.CancelledError, task)
            assert catalog.reads == before
        finally:
            wrapped.unpause()

        held = []
        try:
            for _ in range(10):
                held.append(await redis.connection_pool.get_connection())
            await unavailable(redis, catalog, provider, "exhausted pool")
        finally:
            for connection in held:
                await redis.connection_pool.release(connection)

        # Reserve a local port without listening so no other service can claim it.
        with socket.socket() as reserved:
            reserved.bind(("127.0.0.1", 0))
            refused = shop.make_redis("127.0.0.1", reserved.getsockname()[1])
            try:
                await unavailable(refused, catalog, provider, "refused connection")
            finally:
                await refused.aclose()

        for _ in range(8):
            await shop.db_slots.acquire()
        try:
            before = catalog.reads
            await expect_error(
                shop.ServiceUnavailable,
                shop.product_price(redis, catalog.load_price, "uncached-sku"),
            )
            assert catalog.reads == before
        finally:
            for _ in range(8):
                shop.db_slots.release()
        print("DB overload: bounded wait, request refused without another DB read")

        assert await shop.redis_health(redis, require_write=True)
        assert await shop.product_price(redis, catalog.load_price, "sku-1") == "9.99"
        await shop.allow_login(redis, "after-recovery")
        assert await shop.pay_order(redis, provider.charge, "order-outage", 999) == "charge-3"
        print("recovery: cache, login, payment and health work with the same client")
    finally:
        await redis.aclose()


if __name__ == "__main__":
    logging.disable(logging.CRITICAL)
    with RedisContainer("redis:7-alpine") as container:
        asyncio.run(main(container))
    print("PASS: shop scenarios")
