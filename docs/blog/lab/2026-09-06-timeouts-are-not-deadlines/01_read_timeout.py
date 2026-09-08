"""A read timeout is not a wall clock: a server that drips bytes never trips it."""
import asyncio
import time

import httpx

from clientwright import ClientConfig, TimeoutConfig, build

BYTES = 8
INTERVAL = 0.5  # seconds between bytes; the response takes BYTES * INTERVAL


async def drip(reader, writer) -> None:
    await reader.readuntil(b"\r\n\r\n")
    writer.write(b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n" + f"Content-Length: {BYTES}\r\n\r\n".encode())
    await writer.drain()
    try:
        for _ in range(BYTES):
            await asyncio.sleep(INTERVAL)
            writer.write(b"x")
            await writer.drain()
    except ConnectionResetError:
        pass  # the client gave up mid-body, which is the point of one of the runs
    writer.close()


async def stall(reader, writer) -> None:
    await reader.readuntil(b"\r\n\r\n")
    await asyncio.sleep(BYTES * INTERVAL)
    writer.write(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok")
    await writer.drain()
    writer.close()


async def timed(label, coro):
    started = time.perf_counter()
    try:
        response = await coro
        print(f"{label:<44} -> {response.status_code}, {len(response.content)} bytes, {time.perf_counter() - started:.2f}s")
    except Exception as error:
        print(f"{label:<44} -> {type(error).__name__}, {time.perf_counter() - started:.2f}s")


async def main() -> None:
    drip_server = await asyncio.start_server(drip, "127.0.0.1", 0)
    stall_server = await asyncio.start_server(stall, "127.0.0.1", 0)
    drip_url = f"http://127.0.0.1:{drip_server.sockets[0].getsockname()[1]}/report"
    stall_url = f"http://127.0.0.1:{stall_server.sockets[0].getsockname()[1]}/report"

    async with httpx.AsyncClient(timeout=1.0) as client:
        await timed("httpx timeout=1.0, body drips", client.get(drip_url))
        await timed("httpx timeout=1.0, headers stall", client.get(stall_url))

        async def with_deadline():
            async with asyncio.timeout(1.0):
                return await client.get(drip_url)
        await timed("httpx + asyncio.timeout(1.0), body drips", with_deadline())

    config = ClientConfig(service_name="lab", timeout=TimeoutConfig(total=1.0), retry=None, on_unsupported="strict")
    client = build("httpx", config)
    await timed("clientwright total=1.0, headers stall", client.get(stall_url))
    await timed("clientwright total=1.0, body drips", client.get(drip_url))
    await client.aclose()
    for s in (drip_server, stall_server):
        s.close()


asyncio.run(main())
