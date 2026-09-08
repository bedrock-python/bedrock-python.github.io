"""A retry storm, and a retry budget: what an origin sees when fifty callers retry against it."""

import asyncio
import time

import httpx

from clientwright import AdapterDeps, ClientConfig, RetryConfig, TimeoutConfig, build
from clientwright.core.testing import OriginServer, RecordingMetrics

CALLERS = 50
CHAIN_CALLERS = 10


async def storm(origin: OriginServer, label: str, retry: RetryConfig | None, paths: list[str], base: str | None = None, breaker="default") -> None:
    prefix = paths[0].split("/")[1]
    before = origin.request_count(f"/{prefix}")
    metrics = RecordingMetrics()
    config = ClientConfig(service_name="orders", timeout=TimeoutConfig(total=10.0), retry=retry) if breaker == "default" else ClientConfig(service_name="orders", timeout=TimeoutConfig(total=10.0), retry=retry, circuit_breaker=breaker)
    client = build("httpx", config, AdapterDeps(metrics=metrics))
    started = time.perf_counter()

    async def one(path: str) -> int | str:
        try:
            return (await client.get(f"{base or origin.url}{path}")).status_code
        except httpx.HTTPError as error:
            return type(error).__name__

    callers = CHAIN_CALLERS if base else CALLERS
    results = await asyncio.gather(*(one(paths[i % len(paths)]) for i in range(callers)))
    took = time.perf_counter() - started
    await client.aclose()
    seen = origin.request_count(f"/{prefix}") - before
    ok = sum(1 for r in results if r == 200)
    skipped = sum(1 for s in metrics.retry_skips if "budget" in str(s))
    print(f"  {label:<44} callers={callers:<3} origin saw {seen:>4} requests ({seen / callers:>5.2f}x)  callers ok={ok:<3} retries refused by budget={skipped:<3} {took:.2f}s")


async def hop(origin_url: str, retry: RetryConfig | None, next_url: str | None = None, breaker=None) -> tuple[asyncio.AbstractServer, str]:
    """A service in the middle: every request it receives becomes one outbound call to the next hop."""
    client = build("httpx", ClientConfig(service_name="hop", timeout=TimeoutConfig(total=10.0), retry=retry, circuit_breaker=breaker))

    async def handle(reader, writer) -> None:
        head = (await reader.readuntil(b"\r\n\r\n")).decode()
        path = head.split(" ")[1]
        try:
            status = (await client.get(f"{next_url or origin_url}{path}")).status_code
        except httpx.HTTPError:
            status = 502
        writer.write(f"HTTP/1.1 {status} X\r\nContent-Length: 0\r\n\r\n".encode())
        await writer.drain()
        writer.close()

    server = await asyncio.start_server(handle, "127.0.0.1", 0)
    return server, f"http://127.0.0.1:{server.sockets[0].getsockname()[1]}"


async def main() -> None:
    with OriginServer() as origin:
        no_budget = RetryConfig(max_attempts=3, initial_backoff=0.02, jitter=0.0, budget_ratio=None)
        budget = RetryConfig(max_attempts=3, initial_backoff=0.02, jitter=0.0)  # budget_ratio=0.1 is the default
        print(f"--- {CALLERS} callers, an origin answering 503 to everything ---")
        await storm(origin, "no retries", None, ["/status/503"])
        await storm(origin, "max_attempts=3, no budget", no_budget, ["/status/503"])
        await storm(origin, "max_attempts=3, budget_ratio=0.1 (default)", budget, ["/status/503"])

        print(f"\n--- {CALLERS} callers, 5 of them hit a request that fails once then recovers ---")
        sparse = [f"/flaky/sparse{i}/1" if i < 5 else "/flaky/never/0" for i in range(CALLERS)]
        await storm(origin, "max_attempts=3, no budget", no_budget, sparse)
        await storm(origin, "max_attempts=3, budget_ratio=0.1", budget, [p.replace("sparse", "sparseb") for p in sparse])

        print(f"\n--- {CALLERS} callers, every one of them fails twice then recovers ---")
        await storm(origin, "max_attempts=3, no budget", no_budget, [f"/flaky/dense{i}/2" for i in range(CALLERS)])
        await storm(origin, "max_attempts=3, budget_ratio=0.1", budget, [f"/flaky/denseb{i}/2" for i in range(CALLERS)])

        print(f"\n--- three services deep, the origin answering 503, {CHAIN_CALLERS} callers at the top ---")
        from clientwright import CircuitBreakerConfig
        for label, retry, breaker in (
            ("3 attempts per hop, no budget, no breaker", no_budget, None),
            ("3 attempts per hop, no budget, breaker on", no_budget, CircuitBreakerConfig()),
            ("3 attempts per hop, budget on, breaker on", budget, CircuitBreakerConfig()),
        ):
            c, c_url = await hop(origin.url, retry, breaker=breaker)
            b, b_url = await hop(origin.url, retry, c_url, breaker=breaker)
            a, a_url = await hop(origin.url, retry, b_url, breaker=breaker)
            await storm(origin, label, retry, ["/status/503"], base=a_url, breaker=breaker)
            for srv in (a, b, c):
                srv.close()


asyncio.run(main())
