"""Circuit breakers: keyed on the client, keyed on the origin, and what should trip them."""

import asyncio
import collections
import socket
import time

import httpx

from clientwright import AdapterDeps, CircuitBreakerConfig, CircuitOpenError, ClientConfig, RetryConfig, TimeoutConfig, build
from clientwright.core.testing import OriginServer, RecordingMetrics


class ClientBreaker:
    """The breaker most codebases write first: one window of outcomes for the whole client."""

    def __init__(self, threshold: int = 5, window: int = 20, recovery: float = 30.0) -> None:
        self.recent: collections.deque[bool] = collections.deque(maxlen=window)
        self.open_until = 0.0
        self.threshold, self.recovery = threshold, recovery

    def allow(self) -> bool:
        return time.monotonic() >= self.open_until

    def record(self, ok: bool) -> None:
        self.recent.append(ok)
        if sum(1 for r in self.recent if not r) >= self.threshold:
            self.open_until = time.monotonic() + self.recovery
            self.recent.clear()


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


async def round_robin(label: str, call, origins: dict[str, str], rounds: int = 10) -> None:
    outcome: dict[str, collections.Counter] = {name: collections.Counter() for name in origins}
    for _ in range(rounds):
        for name, url in origins.items():
            outcome[name][await call(url)] += 1
    print(f"  {label}")
    for name, counts in outcome.items():
        print(f"      {name:<10} {dict(counts)}")


async def main() -> None:
    with OriginServer() as a, OriginServer() as b, OriginServer() as c:
        origins = {"stock": f"{a.url}/echo", "pricing": f"{b.url}/echo", "reviews": f"{c.url}/status/503"}

        print("--- three upstreams behind one client, reviews is down, 10 rounds ---")
        naive = ClientBreaker()
        async with httpx.AsyncClient(timeout=2.0) as client:
            async def naive_call(url: str) -> str:
                if not naive.allow():
                    return "refused by breaker"
                response = await client.get(url)
                naive.record(response.status_code < 500)
                return str(response.status_code)
            await round_robin("breaker keyed on the client (hand-rolled)", naive_call, origins)

        metrics = RecordingMetrics()
        client = build("httpx", ClientConfig(service_name="orders", timeout=TimeoutConfig(total=2.0), retry=None,
                                             circuit_breaker=CircuitBreakerConfig(fail_threshold=5)), AdapterDeps(metrics=metrics))

        async def per_origin_call(url: str) -> str:
            try:
                return str((await client.get(url)).status_code)
            except CircuitOpenError:
                return "refused by breaker"
        await round_robin("breaker keyed on the origin (clientwright)", per_origin_call, origins)
        await client.aclose()

        print("\n--- what trips a breaker: 10 calls each, fail_threshold=5 ---")
        dead_port = free_port()
        for label, url in (("429 Too Many Requests", f"{a.url}/status/429"), ("503 Service Unavailable", f"{a.url}/status/503"),
                           ("connection refused", f"http://127.0.0.1:{dead_port}/echo"), ("404 Not Found", f"{a.url}/status/404")):
            client = build("httpx", ClientConfig(service_name="orders", timeout=TimeoutConfig(total=2.0), retry=None,
                                                 circuit_breaker=CircuitBreakerConfig(fail_threshold=5)))
            counts = collections.Counter()
            for _ in range(10):
                try:
                    counts[str((await client.get(url)).status_code)] += 1
                except CircuitOpenError:
                    counts["refused by breaker"] += 1
                except httpx.HTTPError as error:
                    counts[type(error).__name__] += 1
            await client.aclose()
            print(f"  {label:<26} {dict(counts)}")

        print("\n--- one signal per logical call: an upstream that fails twice, then answers ---")
        for label, cfg in (("attempts counted (hand-rolled)", None), ("logical calls counted (clientwright)", "cw")):
            if cfg is None:
                breaker = ClientBreaker()
                refused = ok = 0
                async with httpx.AsyncClient(timeout=2.0) as raw:
                    for n in range(10):
                        result = None
                        for attempt in range(3):
                            if not breaker.allow():
                                result = "refused"; break
                            r = await raw.get(f"{a.url}/flaky/naive{n}/2")
                            breaker.record(r.status_code < 500)
                            if r.status_code < 500:
                                result = "ok"; break
                        refused += result == "refused"; ok += result == "ok"
                print(f"  {label:<38} calls ok={ok} refused by breaker={refused}")
            else:
                m = RecordingMetrics()
                client = build("httpx", ClientConfig(service_name="orders", timeout=TimeoutConfig(total=5.0),
                                                     retry=RetryConfig(max_attempts=3, initial_backoff=0.01, jitter=0.0, budget_ratio=None),
                                                     circuit_breaker=CircuitBreakerConfig(fail_threshold=5)), AdapterDeps(metrics=m))
                refused = ok = 0
                for n in range(10):
                    try:
                        ok += (await client.get(f"{a.url}/flaky/cw{n}/2")).status_code == 200
                    except CircuitOpenError:
                        refused += 1
                await client.aclose()
                print(f"  {label:<38} calls ok={ok} refused by breaker={refused}  attempts={len(m.attempts)} circuit transitions={len(m.circuit_states)}")

        print("\n--- half-open: the first call after recovery_timeout is the probe ---")
        m = RecordingMetrics()
        client = build("httpx", ClientConfig(service_name="orders", timeout=TimeoutConfig(total=2.0), retry=None,
                                             circuit_breaker=CircuitBreakerConfig(fail_threshold=3, recovery_timeout=0.5)), AdapterDeps(metrics=m))
        t0 = time.perf_counter()
        log = []
        for i in range(4):
            try:
                log.append((time.perf_counter() - t0, str((await client.get(f"{c.url}/status/503")).status_code)))
            except CircuitOpenError as e:
                log.append((time.perf_counter() - t0, f"refused, probe in {e.retry_after:.2f}s"))
        await asyncio.sleep(0.6)
        for i in range(2):
            log.append((time.perf_counter() - t0, str((await client.get(f"{c.url}/echo")).status_code)))  # the upstream recovered
        await client.aclose()
        for t, text in log:
            print(f"  {t:5.2f} s  {text}")
        print(f"  circuit state records: {[s for s in m.circuit_states]}")


asyncio.run(main())
