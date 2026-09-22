"""Both entrypoints work; their application lifecycle is configured twice."""
import asyncio
from fastapi.testclient import TestClient
from lifespan_api import build_app
from lifespan_worker import worker
from report_store import ReportStore


def check_api():
    store = ReportStore()
    with TestClient(build_app(store)) as client:
        assert client.get('/reports').json() == {'rows': 42}
        assert store.opened
    assert store.events == ['store:open', 'warmup:done', 'http:started', 'http:done', 'store:close']
    print('PASS FastAPI lifespan: startup, report, cleanup')
    store = ReportStore(fail_warmup=True)
    try:
        with TestClient(build_app(store)):
            raise AssertionError('failed warmup reached serving')
    except ConnectionError:
        pass
    assert not store.opened and store.events[-1] == 'store:close'
    print('PASS FastAPI lifespan: resource closes after startup failure')


async def check_worker():
    store = ReportStore()
    stop = asyncio.Event()
    task = asyncio.create_task(worker(store, stop))
    try:
        await asyncio.wait_for(store.started.wait(), timeout=2)
    finally:
        stop.set()
        await asyncio.wait_for(task, timeout=3)
    assert store.events == ['store:open', 'warmup:done', 'worker:started', 'worker:done', 'store:close']
    print('PASS worker: finishes report before closing resource')
    store = ReportStore(fail_warmup=True)
    try:
        await worker(store, asyncio.Event())
    except ConnectionError:
        pass
    else:
        raise AssertionError('failed warmup reached serving')
    assert not store.opened
    print('PASS worker: resource closes after startup failure')


if __name__ == '__main__':
    check_api()
    asyncio.run(check_worker())
