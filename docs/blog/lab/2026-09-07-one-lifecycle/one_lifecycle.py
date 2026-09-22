"""One application lifecycle for an HTTP report and a periodic report worker."""
import sys
from dataclasses import dataclass

from servicewright import run_sync


@dataclass(frozen=True)
class Settings:
    logging: object | None = None
    metrics: object | None = None
    tracing: object | None = None
    error_tracking: object | None = None

    def get_app_version(self) -> str:
        return '1.0.0'


# snippet:resources
from contextlib import asynccontextmanager
from report_store import ReportStore, open_store


class Scope:
    def __init__(self, store):
        self.store = store

    async def get(self, key):
        if key is ReportStore:
            return self.store
        raise KeyError(key)


class Container:
    def __init__(self, store):
        self.store = store

    @asynccontextmanager
    async def app_scope(self):
        async with open_store(self.store):
            yield Scope(self.store)

    @asynccontextmanager
    async def unit_scope(self, context=None):
        yield Scope(self.store)
# /snippet:resources


# snippet:warmer
import asyncio
from servicewright import AsyncWarmer


class StoreWarmer(AsyncWarmer):
    def __init__(self, store):
        super().__init__()
        self.store = store

    async def warmup(self):
        async with asyncio.timeout(2):
            await self.store.ping()
# /snippet:warmer


# snippet:http
from fastapi import APIRouter
from servicewright.adapters.fastapi import UnitScopeDep

router = APIRouter()


@router.get('/reports')
async def report(unit: UnitScopeDep) -> dict[str, int]:
    store = await unit.get(ReportStore)
    return await store.report('http')
# /snippet:http


# snippet:worker
async def periodic_report(scope, stop: asyncio.Event):
    store = await scope.get(ReportStore)
    while not stop.is_set():
        try:
            await asyncio.wait_for(stop.wait(), timeout=0.5)
            return
        except TimeoutError:
            pass
        if stop.is_set():
            return
        async with asyncio.timeout(1):
            await store.report('worker')
# /snippet:worker


# snippet:spec
from servicewright import AppSpec


def make_spec(container):
    return AppSpec(
        service_name='reports',
        create_container=lambda settings: container,
        warmers=[StoreWarmer(container.store)],
        drain_delay_seconds=0.5,
        drain_grace_seconds=3,
        cleanup_timeout_seconds=2,
    )
# /snippet:spec


# snippet:roles
from servicewright import DaemonEntrypoint, Service
from servicewright.adapters.fastapi import FastApiEntrypoint, HttpConfig


def build_service(role, *, port=8080, store=None):
    container = Container(store if store is not None else ReportStore())
    api = FastApiEntrypoint(
        config=HttpConfig(host='127.0.0.1', port=port, graceful_timeout=1),
        routers=(router,),
    )
    worker = DaemonEntrypoint(periodic_report)
    roles = {'api': [api], 'worker': [worker], 'all': [api, worker]}
    service = Service(make_spec(container), entrypoints=roles[role])
    return service, api, container
# /snippet:roles


if __name__ == '__main__':
    role = sys.argv[1] if len(sys.argv) > 1 else 'all'
    service, _, _ = build_service(role)
    run_sync(service, Settings())
