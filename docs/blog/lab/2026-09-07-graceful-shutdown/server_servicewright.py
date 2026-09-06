"""The same routes under servicewright's lifecycle."""

import contextlib
import sys
from dataclasses import dataclass
from typing import Any

from servicewright import AppSpec, Service, run_sync
from servicewright.adapters.fastapi import FastApiEntrypoint, HttpConfig

from routes import router


@dataclass(frozen=True)
class Settings:
    logging: object | None = None
    metrics: object | None = None
    tracing: object | None = None
    error_tracking: object | None = None

    def get_app_version(self) -> str:
        return "1.0.0"


class Scope:
    async def get(self, dependency_key: Any) -> Any:
        raise KeyError(dependency_key)


class Container:
    @contextlib.asynccontextmanager
    async def app_scope(self):
        yield Scope()

    @contextlib.asynccontextmanager
    async def unit_scope(self, context=None):
        yield Scope()


spec = AppSpec(
    service_name="shutdown-lab",
    create_container=lambda settings: Container(),
    drain_grace_seconds=10.0,
    cleanup_timeout_seconds=5.0,
)
service = Service(
    spec,
    entrypoints=[FastApiEntrypoint(config=HttpConfig(host="127.0.0.1", port=int(sys.argv[1])), routers=(router,))],
)

if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.WARNING)
    run_sync(service, Settings())
