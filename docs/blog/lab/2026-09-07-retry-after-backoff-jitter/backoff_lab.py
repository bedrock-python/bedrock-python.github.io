"""What a production HTTP client actually does about a failed attempt: Retry-After, backoff, jitter, methods, and the read timeout that may have been received."""

import asyncio
import statistics
import time

import httpx

from clientwright import AdapterDeps, ClientConfig, RetryConfig, TimeoutConfig, build
from clientwright.adapters.httpx import IDEMPOTENT_EXTENSION
from clientwright.core.testing import OriginServer, RecordingMetrics

CALLERS = 50


async def main() -> None:
    with OriginServer() as origin:
        print("--- Retry-After: the server says when ---")
        retry = RetryConfig(max_attempts=2, initial_backoff=0.05, jitter=0.0)
        for label, cfg in (("respect_retry_after=True (default)", retry),
                           ("respect_retry_after=False", RetryConfig(max_attempts=2, initial_backoff=0.05, jitter=0.0, respect_retry_after=False))):
            client = build("httpx", ClientConfig(service_name="lab", timeout=TimeoutConfig(total=5.0), retry=cfg))
            started = time.perf_counter()
            response = await client.get(f"{origin.url}/retry-after/1")
            print(f"  {label:<36} -> {response.status_code} after {time.perf_counter() - started:.2f}s (server asked for 1 s between attempts)")
            await client.aclose()

        print(f"\n--- {CALLERS} callers fail at once and retry: when do the retries land? ---")
        for label, cfg in (("fixed backoff 0.3 s, no jitter", RetryConfig(max_attempts=2, initial_backoff=0.3, jitter=0.0, budget_ratio=None)),
                           ("backoff 0.3 s, jitter=0.5", RetryConfig(max_attempts=2, initial_backoff=0.3, jitter=0.5, budget_ratio=None))):
            client = build("httpx", ClientConfig(service_name="lab", timeout=TimeoutConfig(total=5.0), retry=cfg))
            key = label.replace(" ", "")[:8]
            arrivals: list[float] = []
            t0 = time.perf_counter()

            async def one(i: int) -> None:
                await client.get(f"{origin.url}/flaky/{key}{i}/1")   # fails once, then answers
                arrivals.append(time.perf_counter() - t0)

            await asyncio.gather(*(one(i) for i in range(CALLERS)))
            await client.aclose()
            spread = max(arrivals) - min(arrivals)
            print(f"  {label:<32} retries landed between {min(arrivals):.2f}s and {max(arrivals):.2f}s  (spread {spread * 1000:.0f} ms, "
                  f"{sum(1 for a in arrivals if abs(a - statistics.median(arrivals)) < 0.01)} within 10 ms of the median)")

        print("\n--- a POST that timed out: was it received? ---")
        posted_before = origin.request_count("/slow")
        client = build("httpx", ClientConfig(service_name="lab", timeout=TimeoutConfig(total=1.0, read=0.3),
                                             retry=RetryConfig(max_attempts=3, initial_backoff=0.01, jitter=0.0, budget_ratio=None)))
        try:
            await client.post(f"{origin.url}/slow/2", content=b"charge 10 EUR")
        except httpx.HTTPError as error:
            print(f"  POST, read timeout at 0.3 s, 3 attempts allowed -> {type(error).__name__}; the origin received {origin.request_count('/slow') - posted_before} POST(s)")
        await asyncio.sleep(2.2)
        posted_before = origin.request_count("/slow")
        try:
            await client.post(f"{origin.url}/slow/2", content=b"charge 10 EUR", extensions={IDEMPOTENT_EXTENSION: True})
        except httpx.HTTPError as error:
            print(f"  the same POST marked idempotent=True           -> {type(error).__name__}; the origin received {origin.request_count('/slow') - posted_before} POST(s)")
        await client.aclose()
        await asyncio.sleep(2.2)

        print("\n--- what is retried, by default ---")
        metrics = RecordingMetrics()
        client = build("httpx", ClientConfig(service_name="lab", timeout=TimeoutConfig(total=5.0),
                                             retry=RetryConfig(max_attempts=3, initial_backoff=0.01, jitter=0.0, budget_ratio=None)), AdapterDeps(metrics=metrics))
        for label, method, path in (("GET 503", "GET", "/status/503"), ("GET 500", "GET", "/status/500"), ("GET 429", "GET", "/status/429"),
                                    ("GET disconnect", "GET", "/flaky-disconnect/d/1"), ("POST 503", "POST", "/status/503"), ("DELETE 503", "DELETE", "/status/503")):
            before = origin.request_count(path.split("/", 2)[1] and "/" + path.split("/", 2)[1])
            try:
                r = await client.request(method, f"{origin.url}{path}")
                result = str(r.status_code)
            except httpx.HTTPError as error:
                result = type(error).__name__
            prefix = "/" + path.split("/")[1]
            print(f"  {label:<16} -> {result:<14} attempts={origin.request_count(prefix) - before}")
        await client.aclose()


asyncio.run(main())
