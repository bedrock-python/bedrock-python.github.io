"""What an in-house HTTP wrapper costs, and what a policy beside the native client looks like instead."""

import asyncio

import aiohttp
import httpx
import requests
from tenacity import retry, stop_after_attempt, wait_fixed

from clientwright import (
    AdapterDeps,
    ClientConfig,
    RetryConfig,
    TimeoutConfig,
    UnsupportedCapabilityError,
    build,
    build_sync,
    inspect,
)
from clientwright.core.testing import OriginServer, RecordingMetrics

POLICY = ClientConfig(
    service_name="orders",
    timeout=TimeoutConfig(total=5.0, connect=1.0),
    retry=RetryConfig(max_attempts=3, initial_backoff=0.05, jitter=0.0),
)


async def main() -> None:
    with OriginServer() as origin:
        print("--- the native client stays native ---")
        async_httpx = build("httpx", POLICY)
        async_aiohttp = build("aiohttp", POLICY)
        sync_requests = build_sync("requests", ClientConfig(service_name="orders", retry=POLICY.retry))
        for name, client, expected in (("httpx", async_httpx, httpx.AsyncClient), ("aiohttp", async_aiohttp, aiohttp.ClientSession),
                                       ("requests", sync_requests, requests.Session)):
            print(f"  build({name!r}) -> {type(client).__module__}.{type(client).__qualname__}   type(client) is {expected.__name__}: {type(client) is expected}")

        print("\n--- one policy, two SDKs, one dashboard ---")
        for name, deps_metrics in (("httpx", RecordingMetrics()), ("aiohttp", RecordingMetrics())):
            client = build(name, POLICY, AdapterDeps(metrics=deps_metrics))
            key = f"{name}-k"
            if name == "httpx":
                response = await client.get(f"{origin.url}/flaky/{key}/2")
                status = response.status_code
                await client.aclose()
            else:
                async with client.get(f"{origin.url}/flaky/{key}/2") as response:
                    status = response.status
                await client.close()
            attempts = deps_metrics.attempts
            call = deps_metrics.calls[0]
            labels = {k: v for k, v in call.items() if k in ("adapter", "seam", "service", "outcome", "status", "attempts", "method")}
            print(f"  {name:<8} status={status} origin saw {origin.request_count(f'/flaky/{key}')} requests; "
                  f"attempt records={len(attempts)}; call record: {labels}")

        print("\n--- a retry loop on top of a retry loop ---")
        client = build("httpx", POLICY)

        @retry(stop=stop_after_attempt(3), wait=wait_fixed(0.05), reraise=True)
        async def fetch_with_wrapper_retries() -> int:
            response = await client.get(f"{origin.url}/status/503")
            response.raise_for_status()
            return response.status_code

        try:
            await fetch_with_wrapper_retries()
        except httpx.HTTPStatusError:
            pass
        print(f"  tenacity(3) around a client with max_attempts=3, one 503 endpoint: origin saw {origin.request_count('/status/503')} requests")
        await client.aclose()

        print("\n--- capability honesty ---")
        wants_attempt_ceiling = ClientConfig(service_name="orders", timeout=TimeoutConfig(total=5.0, attempt=0.5), retry=POLICY.retry)
        report = inspect(build_sync("requests", wants_attempt_ceiling)).report
        print(f"  requests, attempt=0.5, on_unsupported=warn  -> built; report.dropped = { {str(k): v for k, v in report.dropped.items()} }")
        try:
            build_sync("requests", ClientConfig(service_name="orders", timeout=TimeoutConfig(total=5.0, attempt=0.5), retry=POLICY.retry, on_unsupported="strict"))
        except UnsupportedCapabilityError as error:
            print(f"  requests, attempt=0.5, on_unsupported=strict -> {type(error).__name__}: {str(error)[:150]}")
        report = inspect(build("aiohttp", ClientConfig(service_name="orders", timeout=TimeoutConfig(total=5.0, write=1.0)))).report
        print(f"  aiohttp, write=1.0                             -> built; report.dropped = { {str(k): v[:70] for k, v in report.dropped.items()} }")

    await async_httpx.aclose(); await async_aiohttp.close(); sync_requests.close()


asyncio.run(main())
