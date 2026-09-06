"""What idempotency-kit 0.2.0 does with two concurrent callers and with a reused key."""
import asyncio
from pydantic import BaseModel
from redis.asyncio import Redis
from testcontainers.redis import RedisContainer

from idempotency_kit import AsyncIdempotencyCoordinator, IdempotencyDomainService, PydanticResultAdapter
from idempotency_kit.infra.storage.redis.aio import RedisAsyncIdempotencyRepository


class Charge(BaseModel):
    charge_id: str
    amount: int


charges_made: list[Charge] = []


async def charge_card(amount: int) -> Charge:
    await asyncio.sleep(0.3)  # the payment provider round trip
    charge = Charge(charge_id=f"ch_{len(charges_made) + 1}", amount=amount)
    charges_made.append(charge)
    return charge


async def main(url: str) -> None:
    redis = Redis.from_url(url)
    coordinator = AsyncIdempotencyCoordinator(RedisAsyncIdempotencyRepository(redis), IdempotencyDomainService())
    adapter = PydanticResultAdapter(Charge)

    print("--- two identical requests, 50 ms apart, same key ---")
    first = asyncio.create_task(coordinator.coordinate("payment.charge", "order-42", 3600, adapter, charge_card, 1999))
    await asyncio.sleep(0.05)
    second = asyncio.create_task(coordinator.coordinate("payment.charge", "order-42", 3600, adapter, charge_card, 1999))
    results = await asyncio.gather(first, second)
    print(f"responses: {[r.charge_id for r in results]}")
    print(f"charges made by the provider: {len(charges_made)} -> {[c.charge_id for c in charges_made]}")

    print("\n--- the same key again, with a different amount ---")
    replay = await coordinator.coordinate("payment.charge", "order-42", 3600, adapter, charge_card, 5)
    print(f"requested amount 5, got back: {replay}")
    await redis.aclose()


with RedisContainer("redis:7-alpine") as container:
    asyncio.run(main(f"redis://{container.get_container_host_ip()}:{container.get_exposed_port(6379)}"))
