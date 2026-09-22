"""Gateway driver -> two real HTTP services -> real Redis; simulated payment provider."""
import asyncio
from collections import Counter
from contextlib import asynccontextmanager
import logging
from pathlib import Path
import sys
from uuid import uuid4

from aiohttp import web
import httpx
from pydantic import ValidationError
from idempotency_kit import IdempotencyInProgressError, IdempotencyKeyReuseError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "2026-09-07-idempotency-keys"))
from lab_support import Provider, payment, redis_client, run
from payment_flow import Payment, charge_once, make_coordinator, request_payment


@asynccontextmanager
async def serve(path, handler):
    app = web.Application()
    app.router.add_post(path, handler)
    runner = web.AppRunner(app, handle_signals=False, shutdown_timeout=2)
    await runner.setup()
    try:
        await web.TCPSite(runner, "127.0.0.1", 0).start()
        yield f"http://127.0.0.1:{runner.addresses[0][1]}{path}"
    finally:
        await runner.cleanup()


def drop_response(request):
    assert request.transport is not None
    request.transport.close()
    return web.Response()


async def scenario(redis, mode):
    coordinator, provider = make_coordinator(redis), Provider()
    calls = Counter()
    request_body, original_key = payment(), str(uuid4())

    async def payments_handler(request):
        calls["payments"] += 1
        try:
            dto = Payment.model_validate(await request.json())
            key = request.headers["Idempotency-Key"]
            if mode == "unprotected":
                result = await provider.charge(dto, key)
            else:
                result = await charge_once(coordinator, provider.charge, dto, key)
        except (ValidationError, KeyError):
            return web.json_response({"error": "invalid_request"}, status=400)
        except IdempotencyInProgressError:
            return web.json_response(
                {"error": "payment_in_progress"}, status=409,
                headers={"Retry-After": "1"},
            )
        except IdempotencyKeyReuseError:
            return web.json_response({"error": "key_reused"}, status=409)
        if calls["payments"] == 1:
            # Charge AND the completed Redis result exist before the TCP connection closes.
            return drop_response(request)
        return web.json_response(result.model_dump())

    async with httpx.AsyncClient(timeout=2, trust_env=False) as downstream:
        async with serve("/payments", payments_handler) as payments_url:
            async def orders_handler(request):
                calls["orders"] += 1
                dto = Payment.model_validate(await request.json())
                result = await request_payment(
                    downstream, payments_url, dto, request.headers["Idempotency-Key"],
                )
                if calls["orders"] == 1:
                    return drop_response(request)
                return web.json_response(result.model_dump())

            async with serve("/orders", orders_handler) as orders_url:
                async with httpx.AsyncClient(timeout=2, trust_env=False) as gateway:
                    if mode == "fresh-key":
                        # Deliberately wrong: a network retry becomes a new business operation.
                        for attempt in range(2):
                            try:
                                response = await gateway.post(
                                    orders_url, json=request_body.model_dump(mode="json"),
                                    headers={"Idempotency-Key": str(uuid4())},
                                )
                                response.raise_for_status()
                                break
                            except httpx.TransportError:
                                if attempt == 1:
                                    raise
                    else:
                        result = await request_payment(gateway, orders_url, request_body, original_key)
                        assert result.amount == 1999

                assert calls == Counter(orders=2, payments=3)
                expected = {"unprotected": 3, "fresh-key": 2, "stable-key": 1}[mode]
                assert len(provider.effects) == expected
                print(f"PASS {mode}: orders=2, payments=3, charges={expected}")

                if mode == "stable-key":
                    changed = request_body.model_copy(update={"amount": 5})
                    response = await downstream.post(
                        payments_url, json=changed.model_dump(mode="json"),
                        headers={"Idempotency-Key": original_key},
                    )
                    assert response.status_code == 409
                    assert response.json()["error"] == "key_reused"
                    response = await downstream.post(
                        payments_url, json=request_body.model_dump(mode="json"),
                        headers={"Idempotency-Key": "bad:key"},
                    )
                    assert response.status_code == 400
                    assert len(provider.effects) == 1
                    print("PASS HTTP 409 for changed amount; HTTP 400 for invalid key; no extra charges")


async def main(url):
    async with redis_client(url) as redis:
        for mode in ("unprotected", "fresh-key", "stable-key"):
            await scenario(redis, mode)


if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    run(main)
