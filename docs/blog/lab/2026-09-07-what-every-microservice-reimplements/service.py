"""Compose four libraries around a small orders application."""

import asyncio
import os
from contextlib import AsyncExitStack, asynccontextmanager
from dataclasses import dataclass

import httpx
from clientwright.contrib.deadline import use_budget
from deadline_budget import BudgetContext
from fastapi import APIRouter, Header, HTTPException
from servicewright import AppSpec, Service, run_sync
from servicewright.adapters.fastapi import FastApiEntrypoint, HttpConfig, UnitScopeDep
from servicewright.adapters.health.postgres import PostgresHealthCheck
from servicewright.adapters.warmers import PostgresWarmer
from sqlalchemy_foundation_kit import AsyncSessionManager

from adapters import HttpStockReader, SqlOrderStore, stock_client
from orders import OrderMissing, OrderView, StockUnavailable


@dataclass(frozen=True)
class Settings:
    database_url: str
    warehouse_url: str
    logging: object | None = None
    metrics: object | None = None
    tracing: object | None = None
    error_tracking: object | None = None

    def get_app_version(self):
        return "1.0.0"


class Scope:
    def __init__(self, db, view):
        self.db, self.view = db, view

    async def get(self, key):
        if key is OrderView:
            return self.view
        raise KeyError(key)


class Container:
    def __init__(self, settings):
        self.settings = settings
        self.events = []
        self.db = None
        self.http = None
        self.scope = None

    @asynccontextmanager
    async def app_scope(self):
        try:
            async with AsyncExitStack() as stack:
                self.db = await stack.enter_async_context(
                    AsyncSessionManager(
                        self.settings.database_url,
                        poolclass="async_adapted_queue",
                    )
                )
                self.http = await stack.enter_async_context(
                    stock_client(self.settings.warehouse_url)
                )
                view = OrderView(SqlOrderStore(self.db), HttpStockReader(self.http))
                self.scope = Scope(self.db, view)
                self.events.append("resources:open")
                yield self.scope
        finally:
            self.events.append("resources:closed")

    @asynccontextmanager
    async def unit_scope(self, context=None):
        self.events.append("unit:open")
        try:
            yield Scope(self.db, self.scope.view)
        finally:
            self.events.append("unit:closed")


router = APIRouter()


@router.get("/orders/{order_id}")
async def get_order(
    order_id: int,
    unit: UnitScopeDep,
    x_deadline_ms: int = Header(default=800, ge=50, le=2000),
):
    budget = BudgetContext.create(total_seconds=x_deadline_ms / 1000)
    try:
        with use_budget(budget):
            async with asyncio.timeout(budget.remaining()):
                view = await unit.get(OrderView)
                return await view.get(order_id)
    except OrderMissing as error:
        raise HTTPException(404, "Order not found") from error
    except StockUnavailable as error:
        raise HTTPException(503, "Stock is temporarily unavailable") from error
    except (TimeoutError, httpx.TimeoutException) as error:
        raise HTTPException(504, "Order lookup deadline exceeded") from error


def build_service(settings, *, port=0):
    container = Container(settings)
    spec = AppSpec(
        service_name="orders",
        create_container=lambda _: container,
        warmers_factory=lambda ctx: [PostgresWarmer(ctx.container.db, timeout=2)],
        drain_delay_seconds=0.2,
        drain_grace_seconds=3,
        cleanup_timeout_seconds=2,
    )

    async def register_health(scope):
        spec.health.add_check(
            "postgres", PostgresHealthCheck(scope.db.session_maker, timeout=1)
        )

    spec.lifecycle.add_pre_start_hook(register_health)
    api = FastApiEntrypoint(
        config=HttpConfig(host="127.0.0.1", port=port, graceful_timeout=2),
        routers=(router,),
    )
    return Service(spec, entrypoints=[api]), api, container


if __name__ == "__main__":
    settings = Settings(os.environ["DATABASE_URL"], os.environ["WAREHOUSE_URL"])
    service, _, _ = build_service(settings, port=int(os.environ.get("PORT", "8080")))
    run_sync(service, settings)
