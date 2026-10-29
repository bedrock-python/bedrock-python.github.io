"""Assert concurrency, replay, validation and failure boundaries against real Redis."""
import asyncio
import logging
import socket
from uuid import uuid4

from idempotency_kit import (
    AsyncIdempotencyCoordinator, IdempotencyDomainService,
    IdempotencyInProgressError, NoOpIdempotencyMetrics,
)
from idempotency_kit.infra.storage.redis.aio import RedisAsyncIdempotencyRepository
from pydantic import ValidationError
from redis.asyncio import Redis
from redis.backoff import NoBackoff
from redis.retry import Retry

from lab_support import BlockingProvider, Provider, payment, redis_client, run
from payment_flow import charge_once, make_coordinator, replay_example


class Collisions(NoOpIdempotencyMetrics):
    def __init__(self):
        self.seen = asyncio.Event()

    def record_collision(self, operation):
        self.seen.set()


async def concurrency(redis, mode):
    metrics = Collisions()
    coordinator = AsyncIdempotencyCoordinator(
        RedisAsyncIdempotencyRepository(redis), IdempotencyDomainService(),
        in_flight=mode, metrics=metrics,
    )
    provider, request, key = BlockingProvider(), payment(), str(uuid4())
    async with asyncio.TaskGroup() as tasks:
        first = tasks.create_task(charge_once(coordinator, provider.charge, request, key))
        await provider.started.wait()
        if mode == "raise":
            try:
                await charge_once(coordinator, provider.charge, request, key)
            except IdempotencyInProgressError:
                pass
            else:
                raise AssertionError("The concurrent request must be refused")
            second = None
        else:
            second = tasks.create_task(charge_once(coordinator, provider.charge, request, key))
            await (provider.both_started if mode == "run" else metrics.seen).wait()
        provider.release.set()
    assert len(provider.effects) == (2 if mode == "run" else 1)
    if mode == "wait":
        assert first.result() == second.result()
    print(f"PASS concurrent {mode}: effects={len(provider.effects)}")


async def wait_until_absent(repository, operation, key):
    async with asyncio.timeout(4):
        while await repository.get(operation, key) is not None:
            await asyncio.sleep(0.03)


async def expired_lease(redis):
    repository = RedisAsyncIdempotencyRepository(redis)
    coordinator = AsyncIdempotencyCoordinator(
        repository, IdempotencyDomainService(),
        in_flight="raise", in_flight_lease_seconds=1,
    )
    provider, request, key = BlockingProvider(), payment(), str(uuid4())
    async with asyncio.TaskGroup() as tasks:
        tasks.create_task(charge_once(coordinator, provider.charge, request, key))
        await provider.started.wait()
        await wait_until_absent(repository, f"payment.charge.{request.tenant_id.hex}", key)
        tasks.create_task(charge_once(coordinator, provider.charge, request, key))
        await provider.both_started.wait()
        provider.release.set()
    assert len(provider.effects) == 2
    print("PASS expired lease: first action still alive, effects=2")


async def after_effect(coordinator):
    for protected in (False, True):
        provider = Provider(deduplicate=protected, fail_after_effect=True)
        request, key = payment(), str(uuid4())
        try:
            await charge_once(coordinator, provider.charge, request, key)
        except ConnectionError:
            pass
        else:
            raise AssertionError("Expected a lost provider response")
        await charge_once(coordinator, provider.charge, request, key)
        assert provider.calls == 2
        assert len(provider.effects) == (1 if protected else 2)
        print(f"PASS response lost inside action: provider_key={protected}, effects={len(provider.effects)}")


async def store_down():
    # Keep a port bound but not listening: deterministic connection refusal.
    with socket.socket() as reserved:
        reserved.bind(("127.0.0.1", 0))
        async with Redis(
            host="127.0.0.1", port=reserved.getsockname()[1],
            socket_connect_timeout=0.2, socket_timeout=0.2,
            retry=Retry(NoBackoff(), 0),
        ) as redis:
            provider, request, key = Provider(), payment(), str(uuid4())
            coordinator = make_coordinator(redis)
            await charge_once(coordinator, provider.charge, request, key)
            await charge_once(coordinator, provider.charge, request, key)
            assert len(provider.effects) == 2
    print("PASS Redis unavailable: same key, effects=2 (fail open)")


async def main(url):
    async with redis_client(url) as redis:
        for mode in ("run", "wait", "raise"):
            await concurrency(redis, mode)
        coordinator = make_coordinator(redis)
        provider, request, key = Provider(), payment(), str(uuid4())
        await replay_example(coordinator, provider.charge, request, key)
        assert len(provider.effects) == 1
        other = request.model_copy(update={"tenant_id": uuid4()})
        await charge_once(coordinator, provider.charge, other, key)
        assert len(provider.effects) == 2
        for invalid in ("order:42", "", "x" * 256):
            try:
                await charge_once(coordinator, provider.charge, request, invalid)
            except ValidationError:
                pass
            else:
                raise AssertionError("Validate before entering the coordinator")
        assert len(provider.effects) == 2
        print("PASS replay, changed parameters, tenant scope, invalid keys")

        provider, request = Provider(), payment()
        await charge_once(coordinator, provider.charge, request, str(uuid4()))
        await charge_once(coordinator, provider.charge, request, str(uuid4()))
        assert len(provider.effects) == 2
        print("PASS identical payload, two operation keys: effects=2")

        await after_effect(coordinator)
        await expired_lease(redis)

        provider, request, key = Provider(), payment(), str(uuid4())
        await charge_once(coordinator, provider.charge, request, key)
        operation = f"payment.charge.{request.tenant_id.hex}"
        repository = RedisAsyncIdempotencyRepository(redis)
        record = await repository.get(operation, key)
        assert 3590 < record.ttl_seconds <= 3600
        # Accelerate expiry only for this disposable lab record.
        await redis.pexpire(f"idempotency:{operation}:{key}", 50)
        await wait_until_absent(repository, operation, key)
        await charge_once(coordinator, provider.charge, request, key)
        assert len(provider.effects) == 2
        print("PASS completed TTL: 3600 seconds; late replay after expiry repeats the effect")
    await store_down()


if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    run(main)
