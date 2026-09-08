"""One AppSpec, three kinds of work. ROLE decides which entrypoints this process runs: all, api or worker."""

import asyncio
import contextlib
import os
import sys
import time
from dataclasses import dataclass

from apscheduler.triggers.interval import IntervalTrigger
from fastapi import APIRouter
from servicewright import AppSpec, DaemonEntrypoint, Service, run_sync
from servicewright.adapters.apscheduler4 import ScheduledJob, SchedulerEntrypoint
from servicewright.adapters.fastapi import FastApiEntrypoint, HttpConfig, UnitScopeDep

T0 = time.perf_counter()


def log(text: str) -> None:
    print(f"{time.perf_counter() - T0:6.2f} s  {text}", flush=True)


@dataclass(frozen=True)
class Settings:
    logging: object | None = None
    metrics: object | None = None
    tracing: object | None = None
    error_tracking: object | None = None

    def get_app_version(self) -> str:
        return "1.0.0"


class Pool:  # stands in for the database pool every entrypoint shares
    def __init__(self) -> None:
        self.uses = 0
        log("pool opened")

    async def use(self, who: str) -> None:
        self.uses += 1
        log(f"{who} used the pool (use #{self.uses})")

    async def close(self) -> None:
        log("pool closed")


class Scope:
    def __init__(self, pool: Pool) -> None:
        self.pool = pool

    async def get(self, key):
        return getattr(self, key)


class Container:
    def __init__(self) -> None:
        self.pool = Pool()

    @contextlib.asynccontextmanager
    async def app_scope(self):
        try:
            yield Scope(self.pool)
        finally:
            await self.pool.close()

    @contextlib.asynccontextmanager
    async def unit_scope(self, context=None):
        yield Scope(self.pool)


class Traced:  # the same four calls the Host makes on every entrypoint, with a line each
    def __init__(self, inner, name: str) -> None:
        self._inner, self.name = inner, name
        self.kind, self.essential = inner.kind, inner.essential

    async def bind(self, ctx) -> None:
        log(f"bind    {self.name}")
        await self._inner.bind(ctx)

    async def serve(self, *, stop) -> None:
        log(f"serve   {self.name}")
        await self._inner.serve(stop=stop)
        log(f"serve   {self.name} returned (still accepting)")

    async def drain(self, grace: float) -> None:
        log(f"drain   {self.name}")
        await self._inner.drain(grace)

    async def stop(self) -> None:
        log(f"stop    {self.name}")
        await self._inner.stop()


router = APIRouter()


@router.get("/work")
async def work(unit: UnitScopeDep) -> dict[str, str]:
    await (await unit.get("pool")).use("http request")
    return {"status": "ok"}


async def nightly_report(scope) -> None:  # a cron job, every 0.5 s here so it shows
    await (await scope.get("pool")).use("scheduled job")


async def consume(scope, stop: asyncio.Event) -> None:  # a worker loop: a consumer, a poller
    pool = await scope.get("pool")
    while not stop.is_set():
        await pool.use("worker loop")
        with contextlib.suppress(TimeoutError):
            await asyncio.wait_for(stop.wait(), timeout=0.4)
    log("worker loop saw the stop event and finished its batch")


api = Traced(FastApiEntrypoint(config=HttpConfig(host="127.0.0.1", port=int(os.environ.get("PORT", "8000"))), routers=(router,)), "http")
cron = Traced(SchedulerEntrypoint(jobs=[ScheduledJob(id="report", func=nightly_report, trigger=IntervalTrigger(seconds=0.5))]), "scheduler")
worker = Traced(DaemonEntrypoint(consume), "daemon")

ENTRYPOINTS = {"all": [api, cron, worker], "api": [api], "worker": [cron, worker]}

spec = AppSpec(service_name="orders", create_container=lambda settings: Container(), drain_delay_seconds=0.3, drain_grace_seconds=5.0)
async def announce_ready() -> None:
    log("ready = true, post_start hook")


async def flush_before_close() -> None:
    log("pre_shutdown hook, app scope still open")


spec.lifecycle.add_post_start_hook(announce_ready)
spec.lifecycle.add_pre_shutdown_hook(flush_before_close)

if __name__ == "__main__":
    role = sys.argv[1] if len(sys.argv) > 1 else "all"
    log(f"starting as role={role}")
    run_sync(Service(spec, entrypoints=ENTRYPOINTS[role]), Settings())
    log("run_sync returned")
