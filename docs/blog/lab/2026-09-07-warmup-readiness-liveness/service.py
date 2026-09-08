"""One service with a slow warmup, a readiness check on Redis, and a route that needs neither."""

from __future__ import annotations

import asyncio
import contextlib
import os
import sys
import time
from dataclasses import dataclass
from typing import Any

from fastapi import APIRouter
from redis.asyncio import Redis
from servicewright import AppSpec, AsyncWarmer, HealthRegistry, Service, run_sync
from servicewright.adapters.fastapi import FastApiEntrypoint, HttpConfig

WARMUP_SECONDS = float(os.getenv("WARMUP_SECONDS", "3"))
REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
PORT = int(sys.argv[1])

router = APIRouter()
started = time.time()


@router.get("/cached")
async def cached() -> dict[str, float]:
    """A route the warm cache serves; it never touches Redis."""
    return {"served_at": time.time() - started}


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
    def __init__(self) -> None:
        self.redis = Redis.from_url(REDIS_URL, socket_timeout=0.5, socket_connect_timeout=0.5)

    @contextlib.asynccontextmanager
    async def app_scope(self):
        yield Scope()

    @contextlib.asynccontextmanager
    async def unit_scope(self, context=None):
        yield Scope()


class CacheWarmer(AsyncWarmer):
    """Priming the in-process cache: this is what readiness is waiting for."""

    async def warmup(self) -> None:
        print(f"warmup started at {time.time() - started:.2f} s", flush=True)
        await asyncio.sleep(WARMUP_SECONDS)
        print(f"warmup finished at {time.time() - started:.2f} s", flush=True)


container = Container()


class RedisReachable:
    """A readiness check: an object with `check()`, answering True or False, never raising."""

    async def check(self) -> bool:
        try:
            return bool(await container.redis.ping())
        except Exception:  # noqa: BLE001 - a health check answers, it does not raise
            return False


health = HealthRegistry()
health.add_check("redis", RedisReachable())

spec = AppSpec(
    service_name="probe-lab",
    create_container=lambda settings: container,
    health=health,
    warmers=[CacheWarmer()],
    drain_delay_seconds=float(os.getenv("DRAIN_DELAY", "2")),
    drain_grace_seconds=10.0,
    cleanup_timeout_seconds=5.0,
)
service = Service(
    spec,
    entrypoints=[FastApiEntrypoint(config=HttpConfig(host="127.0.0.1", port=PORT), routers=(router,))],
)

if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.WARNING)
    run_sync(service, Settings())
