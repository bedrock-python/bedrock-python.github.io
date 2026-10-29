"""Assert equivalent application errors over actual localhost HTTP and gRPC."""
import asyncio
import logging

import grpc
import httpx

from service import Settings, build_service
from lab_support import PRIVATE_MARKER, InvoiceStore, call, expect_error, result, wait_until


async def main():
    store = InvoiceStore()
    service, http, rpc = build_service(store)
    stop = asyncio.Event()
    async with httpx.AsyncClient(timeout=3, trust_env=False) as client:
        task = asyncio.create_task(service.run(Settings(), stop=stop))
        try:
            await wait_until(lambda: http.bound_port is not None and rpc.bound_port is not None or task.done())
            if task.done():
                await task
                raise AssertionError("Service exited during startup")
            base = f"http://127.0.0.1:{http.bound_port}"
            async with asyncio.timeout(8):
                while True:
                    try:
                        ready = await client.get(base + "/system/health/readyz")
                        if ready.status_code == 200:
                            break
                    except httpx.TransportError:
                        pass
                    if task.done():
                        await task
                        raise AssertionError("Service exited before readiness")
                    await asyncio.sleep(0.02)

            async with grpc.aio.insecure_channel(f"127.0.0.1:{rpc.bound_port}") as channel:
                await asyncio.wait_for(channel.channel_ready(), 3)
                response = await client.get(base + "/orders/ready/invoice")
                assert response.status_code == 200
                assert response.json() == result(await call(channel))
                cases = {
                    "missing": (404, "NOT_FOUND", "order_not_found"),
                    "unpaid": (412, "FAILED_PRECONDITION", "invoice_not_ready"),
                    "foreign": (403, "PERMISSION_DENIED", "invoice_access_denied"),
                    "offline": (503, "UNAVAILABLE", "invoice_store_unavailable"),
                    "private": (500, "INTERNAL", "internal_error"),
                    "bug": (500, "INTERNAL", "internal_error"),
                    "value-bug": (500, "INTERNAL", "internal_error"),
                }
                for name, (status, code, error_code) in cases.items():
                    response = await client.get(base + f"/orders/{name}/invoice")
                    assert response.status_code == status, response.text
                    body = response.json()
                    assert body["code"] == error_code, body
                    assert response.headers["content-type"].startswith("application/problem+json")
                    error = await expect_error(call(channel, name), getattr(grpc.StatusCode, code))
                    metadata = dict(error.trailing_metadata() or ())
                    assert metadata["x-error-code"] == error_code, metadata
                    assert PRIVATE_MARKER not in response.text + error.details()
                    if name in ("private", "bug", "value-bug"):
                        assert "ledger_corrupted" not in response.text + str(metadata)
                        assert "private-row" not in response.text
                    print(f"PASS {name}: HTTP={status}, gRPC={code}, application_code={error_code}")
        finally:
            stop.set()
            await asyncio.wait_for(task, 10)
    assert store.closed and store.active == 0
    print("PASS success payloads match; both transports stop before the shared store closes")


if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    async def bounded():
        async with asyncio.timeout(35):
            await main()
    asyncio.run(bounded())
