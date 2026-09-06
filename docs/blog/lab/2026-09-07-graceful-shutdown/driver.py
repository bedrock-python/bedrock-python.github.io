"""Play Kubernetes against a server: SIGTERM, then keep routing traffic for a while, and count what breaks."""

import asyncio
import os
import signal
import socket
import subprocess
import sys
import time

import httpx

LAG = 1.0            # seconds the "load balancer" keeps sending traffic after SIGTERM (endpoint propagation)
TICK = 0.02          # one request every 20 ms
READY_PATHS = {"server_plain.py": "/readyz", "server_servicewright.py": "/system/health/readyz"}


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


async def main(script: str) -> None:
    port = free_port()
    base = f"http://127.0.0.1:{port}"
    proc = subprocess.Popen([sys.executable, script, str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ready_path = READY_PATHS[script]
    async with httpx.AsyncClient(base_url=base, timeout=5.0) as client:
        for _ in range(200):
            try:
                if (await client.get(ready_path)).status_code == 200:
                    break
            except httpx.TransportError:
                await asyncio.sleep(0.05)
        else:
            raise SystemExit("server never became ready")

        events: list[tuple[float, str]] = []
        outcomes = {"ok": 0, "refused": 0, "5xx": 0, "other": 0}
        t0 = time.perf_counter()

        def stamp(text: str) -> None:
            events.append((time.perf_counter() - t0, text))

        async def one(path: str) -> str:
            try:
                r = await client.get(path)
                return "ok" if r.status_code == 200 else "5xx"
            except httpx.ConnectError:
                return "refused"
            except httpx.TransportError:
                return "other"

        async def traffic() -> None:
            """The load balancer: requests every TICK until LAG seconds after the signal."""
            while time.perf_counter() - t0 < LAG:
                asyncio.ensure_future(record(one("/work")))
                await asyncio.sleep(TICK)

        async def record(coro) -> None:
            outcomes[await coro] += 1

        async def watch_readiness() -> None:
            last = None
            while time.perf_counter() - t0 < LAG + 0.5:
                try:
                    code = (await client.get(ready_path)).status_code
                except httpx.TransportError:
                    code = "refused"
                if code != last:
                    stamp(f"readiness probe -> {code}")
                    last = code
                await asyncio.sleep(0.05)

        slow = asyncio.ensure_future(one("/slow"))
        await asyncio.sleep(0.1)
        t0 = time.perf_counter()  # the clock starts at the signal
        os.kill(proc.pid, signal.SIGTERM)
        stamp("SIGTERM sent")
        await asyncio.gather(traffic(), watch_readiness())
        stamp(f"in-flight /slow request -> {await slow}")
        await asyncio.sleep(0.5)
        while proc.poll() is None and time.perf_counter() - t0 < 15:
            await asyncio.sleep(0.05)
        stamp(f"process exited with {proc.returncode}")

    delay = os.getenv("DRAIN_DELAY")
    label = f"{script}" + (f", DRAIN_DELAY={delay}" if delay else "")
    print(f"--- {label}: SIGTERM, then {LAG:.0f} s of traffic at one request per {int(TICK * 1000)} ms ---")
    for t, text in events:
        print(f"  {t:6.2f} s  {text}")
    print(f"  requests after SIGTERM: {outcomes}")
    proc.kill()


asyncio.run(main(sys.argv[1]))
