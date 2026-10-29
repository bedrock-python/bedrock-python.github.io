"""Local HTTP fixture and bounded runtime controls; no OS-specific signals."""

import asyncio
import json
from contextlib import asynccontextmanager

import httpx


class Warehouse:
    def __init__(self):
        self.mode = "ok"
        self.calls = []
        self.started = asyncio.Event()
        self.release = asyncio.Event()
        self.tasks = set()

    def reset(self, mode):
        assert not self.tasks
        self.mode = mode
        self.calls.clear()
        self.started.clear()
        self.release.clear()

    async def handle(self, reader, writer):
        task = asyncio.current_task()
        self.tasks.add(task)
        try:
            head = (await reader.readuntil(b"\r\n\r\n")).decode("ascii")
            lines = head.split("\r\n")
            headers = dict(
                line.lower().split(": ", 1) for line in lines[1:] if ": " in line
            )
            self.calls.append(
                {"path": lines[0].split()[1], "budget": int(headers["x-deadline-ms"])}
            )
            if self.mode == "hold":
                self.started.set()
                await self.release.wait()
            failed = self.mode == "down" or (
                self.mode == "once" and len(self.calls) == 1
            )
            status = "503 Service Unavailable" if failed else "200 OK"
            data = {"error": "warehouse unavailable"} if failed else {"available": 3}
            if self.mode == "invalid":
                data = {"available": True}
            body = json.dumps(data).encode()
            writer.write(
                (
                    f"HTTP/1.1 {status}\r\nContent-Type: application/json\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n"
                ).encode()
                + body
            )
            await writer.drain()
        except (ConnectionError, asyncio.IncompleteReadError):
            pass
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except ConnectionError:
                pass
            self.tasks.discard(task)

    async def settle(self):
        async with asyncio.timeout(5):
            while self.tasks:
                await asyncio.sleep(0.01)

    @asynccontextmanager
    async def running(self):
        server = await asyncio.start_server(self.handle, "127.0.0.1", 0)
        try:
            yield f"http://127.0.0.1:{server.sockets[0].getsockname()[1]}"
        finally:
            server.close()
            await server.wait_closed()
            for task in list(self.tasks):
                task.cancel()
            await asyncio.gather(*self.tasks, return_exceptions=True)


async def wait_until(predicate, task):
    async with asyncio.timeout(10):
        while not predicate():
            if task.done():
                await task
                raise AssertionError("Runtime stopped before the expected transition")
            await asyncio.sleep(0.01)


@asynccontextmanager
async def running(service, api, settings):
    stop = asyncio.Event()
    client = httpx.AsyncClient(timeout=5, trust_env=False)
    task = asyncio.create_task(service.run(settings, stop=stop))
    try:
        await wait_until(
            lambda: api.bound_port is not None and service.spec.health.ready, task
        )
        client.base_url = f"http://127.0.0.1:{api.bound_port}"
        async with client:
            async with asyncio.timeout(5):
                while True:
                    try:
                        if (
                            await client.get("/system/health/readyz")
                        ).status_code == 200:
                            break
                    except httpx.TransportError:
                        pass
                    await asyncio.sleep(0.01)
            yield stop, task, client
    finally:
        stop.set()
        try:
            await asyncio.wait_for(task, timeout=10)
        finally:
            await client.aclose()
