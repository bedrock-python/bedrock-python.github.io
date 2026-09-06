"""A per-attempt timeout times max_attempts is what the caller actually waits."""
import asyncio
import logging
import time

import httpx

from clientwright import ClientConfig, RetryConfig, TimeoutConfig, build

logging.disable(logging.CRITICAL)
requests_seen = 0


async def hang(reader, writer) -> None:
    global requests_seen
    await reader.readuntil(b"\r\n\r\n")
    requests_seen += 1
    await asyncio.sleep(30)
    writer.close()


async def timed(label, coro):
    global requests_seen
    requests_seen = 0
    started = time.perf_counter()
    try:
        await coro
        print(f"{label:<52} -> success?!")
    except Exception as error:
        print(f"{label:<52} -> {type(error).__name__} after {time.perf_counter() - started:.2f}s, {requests_seen} requests reached the server")


async def main() -> None:
    server = await asyncio.start_server(hang, "127.0.0.1", 0)
    url = f"http://127.0.0.1:{server.sockets[0].getsockname()[1]}/charge"

    async def hand_loop():
        async with httpx.AsyncClient(timeout=1.0) as client:
            last = None
            for attempt in range(3):
                try:
                    return await client.get(url)
                except httpx.TimeoutException as error:
                    last = error
            raise last
    await timed("hand-rolled loop: 3 attempts, timeout=1.0 each", hand_loop())

    retry = RetryConfig(max_attempts=3, initial_backoff=0.01)
    for label, timeout in (
        ("clientwright: total=1.0, 3 attempts allowed", TimeoutConfig(total=1.0)),
        ("clientwright: total=3.0, read=1.0, 3 attempts allowed", TimeoutConfig(total=3.0, read=1.0)),
    ):
        client = build("httpx", ClientConfig(service_name="lab", timeout=timeout, retry=retry, on_unsupported="strict"))
        await timed(label, client.get(url))
        await client.aclose()
    server.close()


asyncio.run(main())
