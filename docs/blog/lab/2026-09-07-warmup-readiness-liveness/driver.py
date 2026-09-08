"""Poll the two probes and a route through a whole lifecycle: warmup, a dependency outage, SIGTERM."""

from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import threading
import time
from importlib.metadata import version

import httpx
from testcontainers.redis import RedisContainer

WARMUP_SECONDS = 3.0
DRAIN_DELAY = 2.0
INTERVAL = 0.1


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Poller(threading.Thread):
    """Ask livez, readyz and a route every 100 ms and keep the transitions."""

    def __init__(self, base: str) -> None:
        super().__init__(daemon=True)
        self.base = base
        self.samples: list[tuple[float, str, str, str]] = []
        self.started = time.perf_counter()
        self.stop = threading.Event()

    def probe(self, client: httpx.Client, path: str) -> str:
        try:
            return str(client.get(f"{self.base}{path}", timeout=1.0).status_code)
        except httpx.HTTPError as error:
            return type(error).__name__

    def run(self) -> None:
        with httpx.Client() as client:
            while not self.stop.is_set():
                at = time.perf_counter() - self.started
                self.samples.append(
                    (at, self.probe(client, "/system/health/livez"), self.probe(client, "/system/health/readyz"),
                     self.probe(client, "/cached"))
                )
                time.sleep(INTERVAL)

    def transitions(self) -> list[tuple[float, str, str, str]]:
        out: list[tuple[float, str, str, str]] = []
        for sample in self.samples:
            if not out or sample[1:] != out[-1][1:]:
                out.append(sample)
        return out

    def first(self, index: int, value: str) -> float | None:
        return next((s[0] for s in self.samples if s[index] == value), None)


def log(msg: str) -> None:
    print(msg, flush=True)


def main() -> None:
    with RedisContainer("redis:7-alpine") as redis:
        port = free_port()
        env = {
            **os.environ,
            "WARMUP_SECONDS": str(WARMUP_SECONDS),
            "DRAIN_DELAY": str(DRAIN_DELAY),
            "REDIS_URL": f"redis://{redis.get_container_host_ip()}:{redis.get_exposed_port(6379)}/0",
        }
        log(f"servicewright {version('servicewright')}, warmup {WARMUP_SECONDS:.0f} s, "
            f"drain delay {DRAIN_DELAY:.0f} s")
        poller = Poller(f"http://127.0.0.1:{port}")
        proc = subprocess.Popen([sys.executable, "service.py", str(port)], env=env)
        poller.start()

        time.sleep(WARMUP_SECONDS + 3)
        log("--- 1. startup")
        live = poller.first(1, "200")
        ready = poller.first(2, "200")
        route = poller.first(3, "200")
        log(f"    first 200 from livez:  {live:.1f} s" if live else "    livez never answered")
        log(f"    first 200 from readyz: {ready:.1f} s" if ready else "    readyz never answered")
        log(f"    first 200 from the route: {route:.1f} s" if route else "    the route never answered")

        log("--- 2. the dependency goes away (Redis paused)")
        redis.get_wrapped_container().pause()
        paused_at = time.perf_counter() - poller.started
        time.sleep(3)
        after = [s for s in poller.samples if s[0] > paused_at + 1.0][:1]
        if after:
            at, livez, readyz, route_code = after[0]
            log(f"    at {at:.1f} s: livez={livez}  readyz={readyz}  the route that does not need Redis={route_code}")
        redis.get_wrapped_container().unpause()
        time.sleep(2)
        back = [s for s in poller.samples if s[0] > time.perf_counter() - poller.started - 0.5][:1]
        if back:
            at, livez, readyz, route_code = back[0]
            log(f"    Redis back, at {at:.1f} s: livez={livez}  readyz={readyz}  route={route_code}")

        log(f"--- 3. SIGTERM, with drain_delay_seconds={DRAIN_DELAY:.0f}")
        sigterm_at = time.perf_counter() - poller.started
        proc.send_signal(signal.SIGTERM)
        code = proc.wait(timeout=30)
        exited_at = time.perf_counter() - poller.started
        time.sleep(0.5)
        poller.stop.set()
        poller.join(timeout=2)

        after_term = [s for s in poller.samples if s[0] >= sigterm_at]
        ready_false = next((s[0] for s in after_term if s[2] != "200"), None)
        route_gone = next((s[0] for s in after_term if s[3] != "200"), None)
        log(f"    SIGTERM at {sigterm_at:.1f} s, process exited at {exited_at:.1f} s with code {code}")
        if ready_false:
            log(f"    readyz stopped saying 200 at {ready_false:.1f} s ({ready_false - sigterm_at:.1f} s after SIGTERM)")
        if route_gone:
            log(f"    the route stopped answering at {route_gone:.1f} s "
                f"({route_gone - sigterm_at:.1f} s after SIGTERM)")
        if ready_false and route_gone:
            log(f"    requests kept succeeding for {route_gone - ready_false:.1f} s after readiness went false")

        log("--- the transitions the poller saw")
        for at, livez, readyz, route_code in poller.transitions():
            log(f"    {at:5.1f} s  livez={livez:<20} readyz={readyz:<20} /cached={route_code}")


if __name__ == "__main__":
    main()
