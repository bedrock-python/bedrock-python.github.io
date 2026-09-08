"""Idempotency keys against a payment provider that counts its charges: the concurrent case, the reused key, the failed action, the store that is down."""

import asyncio
import logging

from pydantic import BaseModel
from redis.asyncio import Redis
from testcontainers.redis import RedisContainer

from idempotency_kit import (
    AsyncIdempotencyCoordinator,
    IdempotencyDomainService,
    IdempotencyInProgressError,
    IdempotencyKeyReuseError,
    PydanticResultAdapter,
    fingerprint_of,
)
from idempotency_kit.infra.storage.redis.aio import RedisAsyncIdempotencyRepository

logging.disable(logging.CRITICAL)


class Charge(BaseModel):
    charge_id: str
    amount: int


class Provider:
    def __init__(self) -> None:
        self.charges: list[Charge] = []
        self.fail_next = False

    async def charge(self, amount: int) -> Charge:
        await asyncio.sleep(0.3)  # the payment provider round trip
        if self.fail_next:
            self.fail_next = False
            raise RuntimeError("provider timed out")
        charge = Charge(charge_id=f"ch_{len(self.charges) + 1}", amount=amount)
        self.charges.append(charge)
        return charge


adapter = PydanticResultAdapter(Charge)


def coordinator_for(redis: Redis, **kwargs) -> AsyncIdempotencyCoordinator:
    return AsyncIdempotencyCoordinator(RedisAsyncIdempotencyRepository(redis), IdempotencyDomainService(), **kwargs)


async def two_at_once(coordinator: AsyncIdempotencyCoordinator, provider: Provider, key: str, label: str) -> None:
    provider.charges.clear()
    first = asyncio.create_task(coordinator.coordinate("payment.charge", key, 3600, adapter, provider.charge, 1999))
    await asyncio.sleep(0.05)  # the client timed out and retried while the first charge is still in flight
    second = asyncio.create_task(coordinator.coordinate("payment.charge", key, 3600, adapter, provider.charge, 1999))
    results = await asyncio.gather(first, second, return_exceptions=True)
    shown = [r.charge_id if isinstance(r, Charge) else type(r).__name__ for r in results]
    print(f"  {label:<40} responses={shown}  charges made={[c.charge_id for c in provider.charges]}")


async def main(url: str) -> None:
    redis = Redis.from_url(url)
    provider = Provider()

    print("--- two identical requests, 50 ms apart, same key ---")
    await two_at_once(coordinator_for(redis, in_flight="run"), provider, "order-1", "in_flight='run' (a result cache)")
    await two_at_once(coordinator_for(redis), provider, "order-2", "in_flight='wait' (the default)")
    await two_at_once(coordinator_for(redis, in_flight="raise"), provider, "order-3", "in_flight='raise' (409 for the second)")

    coordinator = coordinator_for(redis)
    print("\n--- the same key, a different request ---")
    provider.charges.clear()
    await coordinator.coordinate("payment.charge", "order-4", 3600, adapter, provider.charge, 1999, idempotency_fingerprint=fingerprint_of(amount=1999))
    replay = await coordinator.coordinate("payment.charge", "order-4", 3600, adapter, provider.charge, 1999, idempotency_fingerprint=fingerprint_of(amount=1999))
    print(f"  same key, same amount     -> replayed {replay.charge_id}, charges made={len(provider.charges)}")
    try:
        await coordinator.coordinate("payment.charge", "order-4", 3600, adapter, provider.charge, 5, idempotency_fingerprint=fingerprint_of(amount=5))
    except IdempotencyKeyReuseError as error:
        print(f"  same key, amount 5        -> {type(error).__name__}, charges made={len(provider.charges)}")

    print("\n--- the action fails: nothing is cached, the retry runs again ---")
    provider.charges.clear()
    provider.fail_next = True
    try:
        await coordinator.coordinate("payment.charge", "order-5", 3600, adapter, provider.charge, 1999)
    except RuntimeError as error:
        print(f"  first call  -> {error}")
    again = await coordinator.coordinate("payment.charge", "order-5", 3600, adapter, provider.charge, 1999)
    print(f"  second call -> {again.charge_id}, charges made={len(provider.charges)}")

    print("\n--- the store is down ---")
    provider.charges.clear()
    down = coordinator_for(Redis.from_url("redis://127.0.0.1:1"))
    result = await down.coordinate("payment.charge", "order-6", 3600, adapter, provider.charge, 1999)
    print(f"  Redis unreachable -> the action ran anyway: {result.charge_id}, charges made={len(provider.charges)}  (availability over exactly-once, by design)")
    await redis.aclose()


with RedisContainer("redis:7-alpine") as container:
    asyncio.run(main(f"redis://{container.get_container_host_ip()}:{container.get_exposed_port(6379)}"))
