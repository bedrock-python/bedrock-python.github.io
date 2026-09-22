"""Application functions shared by the article and the three executable labs."""

# snippet:models
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class Payment(BaseModel):
    tenant_id: UUID
    order_id: UUID
    amount: int = Field(gt=0)
    currency: Literal["RUB"] = "RUB"


class Charge(BaseModel):
    charge_id: str
    amount: int
# /snippet:models

# snippet:setup
from redis.asyncio import Redis
from idempotency_kit import AsyncIdempotencyCoordinator, IdempotencyDomainService
from idempotency_kit.infra.storage.redis.aio import RedisAsyncIdempotencyRepository


def make_coordinator(redis: Redis) -> AsyncIdempotencyCoordinator:
    return AsyncIdempotencyCoordinator(
        RedisAsyncIdempotencyRepository(redis),
        IdempotencyDomainService(),
        in_flight="raise",
        in_flight_lease_seconds=30,
    )
# /snippet:setup

# snippet:charge
from collections.abc import Awaitable, Callable
from idempotency_kit import (
    IdempotencyIdentifiers, PydanticResultAdapter, fingerprint_of,
)


async def charge_once(
    coordinator: AsyncIdempotencyCoordinator,
    charge: Callable[[Payment, str], Awaitable[Charge]],
    payment: Payment,
    key: str,
) -> Charge:
    ids = IdempotencyIdentifiers(
        operation=f"payment.charge.{payment.tenant_id.hex}",
        idempotency_key=key,
    )
    provider_key = f"{ids.operation}.{ids.idempotency_key}"
    return await coordinator.coordinate(
        ids.operation, ids.idempotency_key, 3600,
        PydanticResultAdapter(Charge), charge, payment, provider_key,
        idempotency_fingerprint=fingerprint_of(
            order_id=str(payment.order_id),
            amount=payment.amount,
            currency=payment.currency,
        ),
    )
# /snippet:charge

# snippet:replay
from idempotency_kit import IdempotencyKeyReuseError


async def replay_example(coordinator, charge, payment, key):
    first = await charge_once(coordinator, charge, payment, key)
    again = await charge_once(coordinator, charge, payment, key)
    assert first == again

    changed = payment.model_copy(update={"amount": 5})
    try:
        await charge_once(coordinator, charge, changed, key)
    except IdempotencyKeyReuseError:
        return first
    raise AssertionError("A changed amount must not reuse the saved result")
# /snippet:replay

# snippet:http_retry
import httpx


async def request_payment(http, url, payment, key):
    for attempt in range(2):
        try:
            response = await http.post(
                url,
                json=payment.model_dump(mode="json"),
                headers={"Idempotency-Key": key},
            )
            response.raise_for_status()
            return Charge.model_validate(response.json())
        except httpx.TransportError:
            if attempt == 1:
                raise
# /snippet:http_retry

# snippet:invoice
from idempotency_kit import JsonResultAdapter


class InvoiceJob(BaseModel):
    delivery_id: UUID
    tenant_id: UUID
    order_id: UUID
    invoice_version: int = Field(ge=1)
    email: str


async def send_invoice_once(coordinator, send, job: InvoiceJob):
    operation = f"mail.invoice.{job.tenant_id.hex}"
    key = f"{job.order_id.hex}.v{job.invoice_version}"
    return await coordinator.coordinate(
        operation, key, 86400, JsonResultAdapter(),
        send, job, f"{operation}.{key}",
        idempotency_fingerprint=fingerprint_of(email=job.email),
    )
# /snippet:invoice

# snippet:worker
async def handle_invoice(coordinator, send, job, ack):
    receipt = await send_invoice_once(coordinator, send, job)
    await ack(job.delivery_id)
    return receipt
# /snippet:worker
