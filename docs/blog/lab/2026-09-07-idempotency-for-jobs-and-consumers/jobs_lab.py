"""Simulated queue redelivery; real Redis; local mail side-effect counter."""
import logging
from pathlib import Path
import sys
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "2026-09-07-idempotency-keys"))
from lab_support import redis_client, run
from payment_flow import InvoiceJob, handle_invoice, make_coordinator, send_invoice_once
from idempotency_kit import IdempotencyKeyReuseError


class Mailer:
    def __init__(self):
        self.sent = []

    async def send(self, job, key):
        self.sent.append((job.order_id, job.invoice_version, job.email))
        return {"email_id": f"em_{len(self.sent)}"}


async def main(url):
    async with redis_client(url) as redis:
        coordinator = make_coordinator(redis)
        for protected in (False, True):
            mailer = Mailer()
            first = InvoiceJob(
                delivery_id=uuid4(), tenant_id=uuid4(), order_id=uuid4(),
                invoice_version=1, email="buyer@example.test",
            )
            redelivery = first.model_copy(update={"delivery_id": uuid4()})
            acknowledgements = []

            async def ack(delivery_id):
                if delivery_id == first.delivery_id:
                    raise ConnectionError("Worker interrupted before ACK")
                acknowledgements.append(delivery_id)

            for job in (first, redelivery):
                try:
                    if protected:
                        receipt = await handle_invoice(coordinator, mailer.send, job, ack)
                    else:
                        receipt = await mailer.send(job, str(job.delivery_id))
                        await ack(job.delivery_id)
                except ConnectionError:
                    assert job is first
            assert len(acknowledgements) == 1
            assert len(mailer.sent) == (1 if protected else 2)
            if protected:
                assert receipt == {"email_id": "em_1"}
            print(f"PASS two deliveries, protected={protected}: emails={len(mailer.sent)}, ACKs=1")

        newer = first.model_copy(update={"invoice_version": 2, "delivery_id": uuid4()})
        await send_invoice_once(coordinator, mailer.send, newer)
        assert len(mailer.sent) == 2
        changed = first.model_copy(update={"email": "someone-else@example.test"})
        try:
            await send_invoice_once(coordinator, mailer.send, changed)
        except IdempotencyKeyReuseError:
            pass
        else:
            raise AssertionError("Changed recipient must be refused")
        assert len(mailer.sent) == 2
        print("PASS new invoice version sends; changed recipient with old key is refused")


if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    run(main)
