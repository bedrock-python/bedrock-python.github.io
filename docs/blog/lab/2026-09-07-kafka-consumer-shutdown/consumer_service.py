"""The same consumer under a lifecycle: SIGTERM sets a stop event, the batch in flight finishes, its offsets are committed, the group is left cleanly."""

import asyncio
import contextlib
from dataclasses import dataclass

from aiokafka_foundation_kit import consumer_lifecycle
from servicewright import AppSpec, DaemonEntrypoint, Service, run_sync

from consumer_common import TOPIC, log, process, settings


@dataclass(frozen=True)
class Settings:
    logging: object | None = None
    metrics: object | None = None
    tracing: object | None = None
    error_tracking: object | None = None

    def get_app_version(self) -> str:
        return "1.0.0"


class Scope:
    async def get(self, key):
        raise KeyError(key)


class Container:
    @contextlib.asynccontextmanager
    async def app_scope(self):
        yield Scope()

    @contextlib.asynccontextmanager
    async def unit_scope(self, context=None):
        yield Scope()


async def consume(scope, stop: asyncio.Event) -> None:
    async with consumer_lifecycle(settings(), topics=(TOPIC,)) as consumer:   # stop() on exit: the group is left cleanly
        log("consuming")
        while not stop.is_set():
            batches = await consumer.getmany(timeout_ms=500, max_records=5)
            for records in batches.values():
                for message in records:                                       # the batch in flight is finished, stop or not
                    await process(message)
            if batches:
                await consumer.commit()
                log("committed")
        log("stop seen between batches: leaving")


spec = AppSpec(service_name="billing", create_container=lambda settings: Container(), drain_grace_seconds=10.0, cleanup_timeout_seconds=5.0)
run_sync(Service(spec, entrypoints=[DaemonEntrypoint(consume)]), Settings())
