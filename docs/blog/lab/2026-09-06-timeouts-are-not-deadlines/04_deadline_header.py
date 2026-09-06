"""What an HTTP upstream receives when the caller carries a request budget."""
import asyncio
import logging
import time

from deadline_budget import BudgetContext

from clientwright import AdapterDeps, ClientConfig, RetryConfig, TimeoutConfig, build
from clientwright.contrib.deadline import AmbientDeadlineSource, use_budget

logging.disable(logging.CRITICAL)
seen: list[str] = []
fail_first = {"left": 1}


async def echo(reader, writer) -> None:
    head = (await reader.readuntil(b"\r\n\r\n")).decode()
    line = next((l for l in head.split("\r\n") if l.lower().startswith("x-deadline-ms")), "no X-Deadline-Ms header")
    seen.append(line)
    if fail_first["left"]:
        fail_first["left"] -= 1
        writer.write(b"HTTP/1.1 503 Service Unavailable\r\nContent-Length: 0\r\n\r\n")
    else:
        writer.write(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok")
    await writer.drain()
    writer.close()


async def main() -> None:
    server = await asyncio.start_server(echo, "127.0.0.1", 0)
    url = f"http://127.0.0.1:{server.sockets[0].getsockname()[1]}/inventory"

    config = ClientConfig(
        service_name="orders",
        timeout=TimeoutConfig(total=10.0),           # the client's own opinion
        retry=RetryConfig(max_attempts=3, initial_backoff=0.3, jitter=0.0),
        deadline_header="X-Deadline-Ms",
        on_unsupported="strict",
    )
    client = build("httpx", config, AdapterDeps(deadline_source=AmbientDeadlineSource()))

    started = time.perf_counter()
    with use_budget(BudgetContext.create(total_seconds=2.0)):
        await client.get(url)           # first attempt gets a 503, the retry succeeds
        await asyncio.sleep(0.5)        # some work of our own
        await client.get(url)
    elapsed = time.perf_counter() - started

    for i, line in enumerate(seen, 1):
        print(f"attempt {i}: {line}")
    print(f"client config says total=10.0; the request budget was 2.0; the whole thing took {elapsed:.2f}s")
    await client.aclose()
    server.close()


asyncio.run(main())
