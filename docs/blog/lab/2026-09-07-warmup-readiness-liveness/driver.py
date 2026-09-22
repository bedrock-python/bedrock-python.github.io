"""Real Redis outage: assert readiness changes independently of liveness."""
import asyncio
import logging

import httpx
from testcontainers.community.redis import RedisContainer
from servicewright import WarmupError
from service import build_health_service
from one_lifecycle import Settings
from report_store import ReportStore
from lab_support import wait_until, wait_http


async def exercise(redis):
    url = f'redis://{redis.get_container_host_ip()}:{redis.get_exposed_port(6379)}/0'
    store = ReportStore()
    store.allow_warmup.clear()
    service, api, container = build_health_service(url, store)
    stop = asyncio.Event()
    task = asyncio.create_task(service.run(Settings(), stop=stop))
    paused = False
    try:
        await asyncio.wait_for(store.warming.wait(), timeout=5)
        assert api.bound_port is None and not service.spec.health.ready
        store.allow_warmup.set()
        await wait_until(lambda: api.bound_port is not None, task)
        async with httpx.AsyncClient(
            base_url=f'http://127.0.0.1:{api.bound_port}', timeout=3, trust_env=False,
        ) as client:
            await wait_http(client, task)
            assert (await client.get('/system/health/livez')).status_code == 200
            print('PASS warmup: no listener before initialization; both probes then return 200')

            await asyncio.to_thread(redis.get_wrapped_container().pause)
            paused = True
            assert (await client.get('/system/health/readyz')).status_code == 503
            assert (await client.get('/system/health/livez')).status_code == 200
            assert (await client.get('/reports')).status_code == 200
            print('PASS Redis paused: readyz=503, livez=200; direct route without Redis still works')

            await asyncio.to_thread(redis.get_wrapped_container().unpause)
            paused = False
            await wait_http(client, task)
            print('PASS Redis restored: readiness recovers without service restart')

            stop.set()
            await wait_until(lambda: not service.spec.health.ready, task)
            assert (await client.get('/system/health/readyz')).status_code == 503
            assert (await client.get('/system/health/livez')).status_code == 200
            assert (await client.get('/reports')).status_code == 200
            print('PASS stop: readiness withdrawn while HTTP still accepts during drain delay')
    finally:
        if paused:
            await asyncio.to_thread(redis.get_wrapped_container().unpause)
        stop.set()
        await asyncio.wait_for(task, timeout=10)
    assert container.closed and not store.opened
    print('PASS cleanup: Redis client and report store closed')

    failed_store = ReportStore()
    failed_service, failed_api, failed_container = build_health_service(url, failed_store)
    await asyncio.to_thread(redis.get_wrapped_container().pause)
    try:
        try:
            await asyncio.wait_for(
                failed_service.run(Settings(), stop=asyncio.Event()), timeout=5,
            )
        except WarmupError:
            pass
        else:
            raise AssertionError('startup succeeded without mandatory Redis')
    finally:
        await asyncio.to_thread(redis.get_wrapped_container().unpause)
    assert failed_container.closed and not failed_store.opened
    assert failed_api.bound_port is None and not failed_service.spec.health.ready
    print('PASS Redis unavailable at startup: warmup fails, both resources close, no HTTP bind')


if __name__ == '__main__':
    logging.basicConfig(level=logging.CRITICAL)
    with RedisContainer('redis:7-alpine') as redis:
        asyncio.run(exercise(redis))
