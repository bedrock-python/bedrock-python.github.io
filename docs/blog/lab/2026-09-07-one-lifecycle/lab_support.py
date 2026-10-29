"""Bounded helpers for driving real localhost HTTP without installing signal handlers."""
import asyncio
from contextlib import asynccontextmanager

import httpx
from one_lifecycle import Settings


async def wait_until(predicate, task, *, timeout=5):
    async with asyncio.timeout(timeout):
        while not predicate():
            if task.done():
                await task
                raise AssertionError('service exited before the expected transition')
            await asyncio.sleep(0.01)


async def wait_http(client, task):
    async with asyncio.timeout(5):
        while True:
            if task.done():
                await task
                raise AssertionError('service exited before HTTP became ready')
            try:
                if (await client.get('/system/health/readyz')).status_code == 200:
                    return
            except httpx.TransportError:
                pass
            await asyncio.sleep(0.02)


@asynccontextmanager
async def running(service, api=None):
    # SSL context creation can block on some hosts; do it before starting the service.
    client = httpx.AsyncClient(timeout=5, trust_env=False) if api is not None else None
    stop = asyncio.Event()
    task = asyncio.create_task(service.run(Settings(), stop=stop))
    try:
        if api is None:
            await wait_until(lambda: service.spec.health.ready, task)
            yield stop, task, None
        else:
            await wait_until(lambda: api.bound_port is not None, task)
            client.base_url = f'http://127.0.0.1:{api.bound_port}'
            async with client:
                await wait_http(client, task)
                yield stop, task, client
    finally:
        stop.set()
        try:
            await asyncio.wait_for(task, timeout=10)
        finally:
            if client is not None:
                await client.aclose()
