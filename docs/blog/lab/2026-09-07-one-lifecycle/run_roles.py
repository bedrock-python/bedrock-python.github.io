"""Assert shared resource ownership, startup rollback and essential worker failure."""
import asyncio
import logging

from servicewright import DaemonEntrypoint, Service, WarmupError
from one_lifecycle import Settings, build_service
from lab_support import running, wait_until
from report_store import ReportStore


async def main():
    for role in ('all', 'api', 'worker'):
        store = ReportStore()
        service, api, _ = build_service(role, port=0, store=store)
        async with running(service, api if role != 'worker' else None) as (_, task, client):
            if client is not None:
                response = await client.get('/reports')
                assert response.status_code == 200
                assert response.json() == {'rows': 42}
            if role != 'api':
                await wait_until(lambda: 'worker:done' in store.events, task)
        assert store.events[0] == 'store:open'
        assert store.events.count('store:open') == 1
        assert store.events[-1] == 'store:close'
        assert not store.opened and store.active == 0
        assert ('http:done' in store.events) == (role != 'worker')
        assert ('worker:done' in store.events) == (role != 'api')
        print(f'PASS role={role}: warmup, work, one resource open/close')

    store = ReportStore(fail_warmup=True)
    service, api, _ = build_service('api', port=0, store=store)
    try:
        await service.run(Settings(), stop=asyncio.Event())
    except WarmupError:
        pass
    else:
        raise AssertionError('warmup failure was swallowed')
    assert not service.spec.health.ready and api.bound_port is None
    assert store.events == ['store:open', 'store:close']
    print('PASS failed warmup: no HTTP listener, opened resource closed')

    store = ReportStore()
    store.allow_warmup.clear()
    service, api, _ = build_service('api', port=0, store=store)
    stop = asyncio.Event()
    task = asyncio.create_task(service.run(Settings(), stop=stop))
    try:
        await asyncio.wait_for(store.warming.wait(), timeout=5)
        assert api.bound_port is None and not service.spec.health.ready
    finally:
        stop.set()
        await asyncio.wait_for(task, timeout=5)
    assert not store.opened and api.bound_port is None
    print('PASS stop during warmup: no late bind or readiness, resource closed')

    async def broken_worker(scope, stop):
        await scope.get(ReportStore)
        raise RuntimeError('worker failed')

    base, _, container = build_service('worker')
    service = Service(base.spec, entrypoints=[DaemonEntrypoint(broken_worker)])
    try:
        await service.run(Settings(), stop=asyncio.Event())
    except RuntimeError as error:
        assert str(error) == 'worker failed'
    else:
        raise AssertionError('essential worker failure was swallowed')
    assert not container.store.opened and not service.spec.health.ready
    print('PASS essential worker: failure reaches caller after cleanup')


if __name__ == '__main__':
    logging.basicConfig(level=logging.CRITICAL)
    asyncio.run(main())
