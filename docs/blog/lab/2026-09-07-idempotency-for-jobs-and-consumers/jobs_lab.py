"""Idempotency beyond HTTP: a job queue that delivers at least once, a worker that crashes before it acknowledges, and two workers holding the same job."""

import asyncio
import logging

from pydantic import BaseModel
from redis.asyncio import Redis
from testcontainers.redis import RedisContainer

from idempotency_kit import AsyncIdempotencyCoordinator, IdempotencyDomainService, IdempotencyInProgressError, PydanticResultAdapter
from idempotency_kit.infra.storage.redis.aio import RedisAsyncIdempotencyRepository

logging.disable(logging.CRITICAL)


class Receipt(BaseModel):
    email_id: str


class Mailer:
    def __init__(self) -> None:
        self.sent: list[str] = []

    async def send_invoice(self, order_id: str) -> Receipt:
        await asyncio.sleep(0.2)                       # the mail provider round trip
        self.sent.append(order_id)
        return Receipt(email_id=f"em_{len(self.sent)}")


class Queue:
    """A queue that delivers at least once: a job stays visible until it is acknowledged."""

    def __init__(self) -> None:
        self.jobs: list[dict] = []
        self.deliveries = 0

    def put(self, job_id: str, order_id: str) -> None:
        self.jobs.append({"job_id": job_id, "order_id": order_id, "acked": False})

    def next(self) -> dict | None:
        for job in self.jobs:
            if not job["acked"]:
                self.deliveries += 1
                return job
        return None

    def ack(self, job: dict) -> None:
        job["acked"] = True


async def run_worker(queue: Queue, handle, *, crash_before_ack_once: bool) -> None:
    crashed = False
    while (job := queue.next()) is not None:
        await handle(job)
        if crash_before_ack_once and not crashed:
            crashed = True
            continue                                   # the worker died after the effect, before the ack: redelivery
        queue.ack(job)


async def main(url: str) -> None:
    redis = Redis.from_url(url)
    adapter = PydanticResultAdapter(Receipt)
    coordinator = AsyncIdempotencyCoordinator(RedisAsyncIdempotencyRepository(redis), IdempotencyDomainService())

    print("--- a worker that crashes after sending the mail and before acknowledging the job ---")
    for label, wrapped in (("plain handler", False), ("handler under an idempotency key = job id", True)):
        queue, mailer = Queue(), Mailer()
        queue.put(f"job-{label[:5]}", "order-42")

        async def handle(job: dict) -> None:
            if wrapped:
                await coordinator.coordinate("mail.invoice", job["job_id"], 3600, adapter, mailer.send_invoice, job["order_id"])
            else:
                await mailer.send_invoice(job["order_id"])

        await run_worker(queue, handle, crash_before_ack_once=True)
        print(f"  {label:<44} deliveries={queue.deliveries} mails sent={len(mailer.sent)}")

    print("\n--- two workers pick the same job at the same time (a visibility timeout expired) ---")
    for label, kwargs in (("in_flight='wait'", {}), ("in_flight='raise'", {"in_flight": "raise"})):
        mailer = Mailer()
        c = AsyncIdempotencyCoordinator(RedisAsyncIdempotencyRepository(redis), IdempotencyDomainService(), **kwargs)
        job_id = f"job-race-{label[-6:-1]}"

        async def worker(name: str):
            try:
                return name, (await c.coordinate("mail.invoice", job_id, 3600, adapter, mailer.send_invoice, "order-7")).email_id
            except IdempotencyInProgressError:
                return name, "in progress, requeue"

        results = await asyncio.gather(worker("A"), worker("B"))
        print(f"  {label:<20} {dict(results)}  mails sent={len(mailer.sent)}")

    print("\n--- the same order, two different jobs ---")
    mailer = Mailer()
    for job_id in ("job-1", "job-2"):
        await coordinator.coordinate("mail.invoice", job_id, 3600, adapter, mailer.send_invoice, "order-9")
    print(f"  key = job id: two jobs for order-9 -> mails sent={len(mailer.sent)}   (the key must be the effect's identity, not the delivery's)")
    mailer = Mailer()
    for job_id in ("job-3", "job-4"):
        await coordinator.coordinate("mail.invoice", "order-9:invoice", 3600, adapter, mailer.send_invoice, "order-9")
    print(f"  key = 'order-9:invoice': the same two jobs -> mails sent={len(mailer.sent)}   (a colon is not allowed in a key; the record fails validation and the action runs unprotected)")
    mailer = Mailer()
    for job_id in ("job-5", "job-6"):
        await coordinator.coordinate("mail.invoice", "order-9.invoice", 3600, adapter, mailer.send_invoice, "order-9")
    print(f"  key = 'order-9.invoice': the same two jobs -> mails sent={len(mailer.sent)}")
    await redis.aclose()


with RedisContainer("redis:7-alpine") as container:
    asyncio.run(main(f"redis://{container.get_container_host_ip()}:{container.get_exposed_port(6379)}"))
