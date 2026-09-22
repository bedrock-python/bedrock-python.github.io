"""Exercise actual HTTP completion and cancellation using the public stop-event API."""
import asyncio
import logging

from routes import ReportStore, build_service


# snippet:shutdown_test
from lab_support import running, wait_until


async def check_graceful_shutdown():
    store = ReportStore(duration=0.8)
    service, api, _ = build_service('api', port=0, store=store)
    async with running(service, api) as (stop, task, client):
        request = asyncio.create_task(client.get('/reports'))
        try:
            await asyncio.wait_for(store.started.wait(), timeout=2)
            stop.set()
            await wait_until(lambda: not service.spec.health.ready, task)
            assert (await client.get('/system/health/readyz')).status_code == 503
            assert (await request).status_code == 200
        finally:
            await asyncio.gather(request, return_exceptions=True)
    assert store.events.index('http:done') < store.events.index('store:close')
# /snippet:shutdown_test


async def check_expired_request():
    store = ReportStore(duration=30)
    service, api, _ = build_service('api', port=0, store=store)
    async with running(service, api) as (stop, task, client):
        request = asyncio.create_task(client.get('/reports'))
        try:
            await asyncio.wait_for(store.started.wait(), timeout=2)
            stop.set()
            response = await request
            assert response.status_code == 500
        finally:
            await asyncio.gather(request, return_exceptions=True)
    assert 'http:done' not in store.events
    assert store.events.index('http:cancelled') < store.events.index('store:close')
    assert store.active == 0 and not store.opened


async def main():
    await check_graceful_shutdown()
    print('PASS HTTP: readiness withdrawn, accepted report returns 200 before resource closes')
    await check_expired_request()
    print('PASS HTTP timeout: unfinished report cancelled; resource closes after cancellation')


if __name__ == '__main__':
    logging.basicConfig(level=logging.CRITICAL)
    asyncio.run(main())
