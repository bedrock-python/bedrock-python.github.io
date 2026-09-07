"""One dependency that goes bad, and five clients pointed at it.

The origin answers `/slow/2` — two seconds per request — which is what a dependency looks like
when it is overloaded rather than down. Forty callers hit it through five configurations: no
retries, retry=3, retry plus a deadline, retry plus a budget, and retry plus a per-origin circuit
breaker. For each: how many requests the origin actually received, how many callers got an answer,
how long the slowest caller waited, and how long the whole wave took.
"""

from __future__ import annotations

import asyncio
import time

import httpx

from clientwright import (
    AdapterDeps,
    CircuitBreakerConfig,
    ClientConfig,
    RetryConfig,
    TimeoutConfig,
    build,
)
from clientwright.core.testing import OriginServer, RecordingMetrics

CALLERS = 40
SLOW_SECONDS = 2.0


def log(msg: str) -> None:
    print(msg, flush=True)


async def wave(origin: OriginServer, label: str, config: ClientConfig, path: str) -> None:
    prefix = "/" + path.split("/")[1]
    before = origin.request_count(prefix)
    metrics = RecordingMetrics()
    client = build("httpx", config, AdapterDeps(metrics=metrics))
    latencies: list[float] = []

    async def one() -> str:
        started = time.perf_counter()
        try:
            response = await client.get(f"{origin.url}{path}")
            return str(response.status_code)
        except httpx.HTTPError as error:
            return type(error).__name__
        except Exception as error:  # noqa: BLE001 - a tripped breaker is not an httpx error
            return type(error).__name__
        finally:
            latencies.append(time.perf_counter() - started)

    started = time.perf_counter()
    results = await asyncio.gather(*(one() for _ in range(CALLERS)))
    took = time.perf_counter() - started
    await client.aclose()

    seen = origin.request_count(prefix) - before
    ok = sum(1 for r in results if r == "200")
    refused = sum(1 for s in metrics.retry_skips if "budget" in str(s))
    outcomes = {}
    for r in results:
        if r != "200":
            outcomes[r] = outcomes.get(r, 0) + 1
    log(
        f"  {label:<38} origin saw {seen:>3} ({seen / CALLERS:.2f}x)  ok={ok:<3} "
        f"slowest caller {max(latencies):5.2f}s  wave {took:5.2f}s  "
        f"{'budget refused ' + str(refused) + '  ' if refused else ''}"
        f"{', '.join(f'{k}={v}' for k, v in sorted(outcomes.items())) if outcomes else ''}"
    )


def config_for(
    *, retry: RetryConfig | None, total: float, breaker: CircuitBreakerConfig | None = None
) -> ClientConfig:
    kwargs = {
        "service_name": "orders",
        "timeout": TimeoutConfig(total=total),
        "retry": retry,
    }
    if breaker is not None:
        kwargs["circuit_breaker"] = breaker
    return ClientConfig(**kwargs)


async def main() -> None:
    plain = RetryConfig(max_attempts=3, initial_backoff=0.05, jitter=0.0, budget_ratio=None)
    budgeted = RetryConfig(max_attempts=3, initial_backoff=0.05, jitter=0.0, budget_ratio=0.1)
    breaker = CircuitBreakerConfig(fail_threshold=8, recovery_timeout=5.0)

    with OriginServer() as origin:
        log(f"--- {CALLERS} callers against an origin that takes {SLOW_SECONDS:.0f} s per request")
        await wave(origin, "no retries, total=30s", config_for(retry=None, total=30.0), f"/slow/{SLOW_SECONDS}")
        await wave(origin, "retry=3, total=30s", config_for(retry=plain, total=30.0), f"/slow/{SLOW_SECONDS}")
        await wave(origin, "retry=3, total=1.0s (a deadline)", config_for(retry=plain, total=1.0), f"/slow/{SLOW_SECONDS}")

        log("")
        log(f"--- the same {CALLERS} callers against an origin that returns 503")
        await wave(origin, "no retries", config_for(retry=None, total=10.0), "/status/503")
        await wave(origin, "retry=3", config_for(retry=plain, total=10.0), "/status/503")
        await wave(origin, "retry=3, budget_ratio=0.1", config_for(retry=budgeted, total=10.0), "/status/503")
        await wave(
            origin,
            "retry=3, budget, breaker(8, 5s)",
            config_for(retry=budgeted, total=10.0, breaker=breaker),
            "/status/503",
        )

        log("")
        log("--- the wave after that one, with the same client (the breaker has now seen the failures)")
        breaker_client_config = config_for(retry=budgeted, total=10.0, breaker=breaker)
        shared = build("httpx", breaker_client_config)
        for round_number in (1, 2):
            before = origin.request_count("/status")
            started = time.perf_counter()

            async def one() -> str:
                try:
                    return str((await shared.get(f"{origin.url}/status/503")).status_code)
                except Exception as error:  # noqa: BLE001 - the breaker's error is not an httpx one
                    return type(error).__name__

            results = await asyncio.gather(*(one() for _ in range(CALLERS)))
            outcomes: dict[str, int] = {}
            for r in results:
                outcomes[r] = outcomes.get(r, 0) + 1
            log(f"  wave {round_number} through one client: origin saw "
                f"{origin.request_count('/status') - before:>3}, "
                f"{time.perf_counter() - started:.2f}s, "
                f"{', '.join(f'{k}={v}' for k, v in sorted(outcomes.items()))}")
        await shared.aclose()

        log("")
        log("--- and when the origin recovers, how long until callers are served again")
        recovering = config_for(retry=budgeted, total=10.0, breaker=breaker)
        client = build("httpx", recovering)
        for _ in range(20):                                    # trip the breaker
            try:
                await client.get(f"{origin.url}/status/503")
            except Exception:  # noqa: BLE001, S110 - tripping it is the point
                pass
        started = time.perf_counter()
        deadline = started + 20
        while time.perf_counter() < deadline:
            try:
                response = await client.get(f"{origin.url}/status/200")
                if response.status_code == 200:
                    log(f"  the first success after the origin healed: {time.perf_counter() - started:.2f} s "
                        f"(breaker recovery_timeout is {breaker.recovery_timeout:.0f} s)")
                    break
            except Exception:  # noqa: BLE001 - CircuitBreakerOpenError while it is still open
                await asyncio.sleep(0.2)
        await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
