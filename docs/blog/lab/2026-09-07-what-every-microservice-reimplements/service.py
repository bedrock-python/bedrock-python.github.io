"""One service, four libraries, no framework: lifecycle, sessions, an outbound client and a request deadline."""

import contextlib
import os
from dataclasses import dataclass

from clientwright import AdapterDeps, ClientConfig, RetryConfig, TimeoutConfig, build
from clientwright.contrib.deadline import AmbientDeadlineSource, use_budget
from deadline_budget import BudgetContext
from fastapi import APIRouter, Header
from servicewright import AppSpec, Service, run_sync
from servicewright.adapters.fastapi import FastApiEntrypoint, HttpConfig, UnitScopeDep
from servicewright.adapters.health.postgres import PostgresHealthCheck
from servicewright.adapters.warmers import PostgresWarmer
from sqlalchemy import text
from sqlalchemy_foundation_kit import AsyncSessionManager


@dataclass(frozen=True)
class Settings:  # the shape the runtime reads; nothing to inherit
    logging: object | None = None
    metrics: object | None = None
    tracing: object | None = None
    error_tracking: object | None = None

    def get_app_version(self) -> str:
        return "1.0.0"


class Scope:  # what the runtime asks of a scope: `await scope.get(key)`
    def __init__(self, **provides) -> None:
        self.__dict__.update(provides)

    async def get(self, key):
        return getattr(self, key)


class Container:  # your DI, in twelve lines: one app scope for singletons, one unit scope per request
    def __init__(self, db: AsyncSessionManager, http) -> None:
        self.db, self.http = db, http

    @contextlib.asynccontextmanager
    async def app_scope(self):
        try:
            yield Scope(db=self.db, http=self.http)
        finally:  # pools close here, after every entrypoint has drained
            await self.http.aclose()
            await self.db.aclose()

    @contextlib.asynccontextmanager
    async def unit_scope(self, context=None):
        async with self.db.get_session() as session:
            yield Scope(session=session, http=self.http)


def create_container(settings: Settings) -> Container:
    db = AsyncSessionManager(os.environ["DATABASE_URL"], poolclass="async_adapted_queue")
    http = build("httpx", ClientConfig(
        service_name="orders",
        base_url=os.environ["WAREHOUSE_URL"],
        timeout=TimeoutConfig(total=5.0),
        retry=RetryConfig(max_attempts=3),
        deadline_header="X-Deadline-Ms",       # what is left of the request, on the wire
        on_unsupported="strict",
    ), AdapterDeps(deadline_source=AmbientDeadlineSource()))
    return Container(db, http)


router = APIRouter()


@router.get("/orders/{order_id}")
async def get_order(order_id: int, unit: UnitScopeDep, x_deadline_ms: int | None = Header(default=None)):
    budget = BudgetContext.create(total_seconds=x_deadline_ms / 1000, safety_margin=0.1) if x_deadline_ms else None
    with use_budget(budget):                    # every outbound call below is trimmed to it
        session, http = await unit.get("session"), await unit.get("http")
        known = (await session.execute(text("SELECT count(*) FROM orders WHERE id = :id"), {"id": order_id})).scalar()
        stock = (await http.get(f"/stock/{order_id}")).json()
    return {"order_id": order_id, "known": bool(known), "stock": stock}


async def register_health(app_scope: Scope) -> None:
    spec.health.add_check("postgres", PostgresHealthCheck(app_scope.db.session_maker))


spec = AppSpec(
    service_name="orders",
    create_container=create_container,
    warmers_factory=lambda ctx: [PostgresWarmer(ctx.container.db)],   # readiness waits for a real query
    drain_delay_seconds=1.0,                                          # keep serving while endpoints propagate
    drain_grace_seconds=10.0,
    cleanup_timeout_seconds=5.0,
)
spec.lifecycle.add_pre_start_hook(register_health)
service = Service(spec, entrypoints=[
    FastApiEntrypoint(config=HttpConfig(host="127.0.0.1", port=int(os.environ.get("PORT", "8000"))), routers=(router,)),
])

if __name__ == "__main__":
    run_sync(service, Settings())
