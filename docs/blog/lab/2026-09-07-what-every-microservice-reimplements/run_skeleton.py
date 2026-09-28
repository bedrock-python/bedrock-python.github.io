"""Run real PostgreSQL and HTTP scenarios, then verify orderly shutdown."""

import asyncio
import logging
from importlib.metadata import version

from servicewright import WarmupError
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy_foundation_kit import AsyncSessionManager
from testcontainers.community.postgres import PostgresContainer

from adapters import HttpStockReader, stock_client
from lab_support import Warehouse, running, wait_until
from orders import Order, OrderView
from service import Settings, build_service


async def seed(database_url):
    async with AsyncSessionManager(database_url) as db:
        async with db.get_transaction() as session:
            await session.execute(
                text(
                    "CREATE TABLE orders (id int PRIMARY KEY, sku text NOT NULL, quantity int NOT NULL)"
                )
            )
            await session.execute(
                text("INSERT INTO orders VALUES (1, 'sku-42', 2), (2, 'sku-42', 5)")
            )


async def check_closed(container):
    assert container.http.is_closed
    assert container.events.count("resources:open") == 1
    assert container.events.count("resources:closed") == 1
    assert container.events[-1] == "resources:closed"
    try:
        async with container.db.get_session():
            raise AssertionError("Closed manager handed out a session")
    except RuntimeError as error:
        assert "closed" in str(error)


async def scenarios(database_url, warehouse_url, warehouse):
    settings = Settings(database_url, warehouse_url)
    service, api, container = build_service(settings)
    async with running(service, api, settings) as (stop, task, client):
        assert container.events.count("resources:open") == 1
        assert "resources:closed" not in container.events
        response = await client.get("/orders/1")
        assert response.status_code == 200, response.text
        assert response.json() == {"order_id": 1, "available": 3, "can_fulfill": True}
        await warehouse.settle()
        assert warehouse.calls[0]["path"] == "/stock/sku-42"
        assert 0 < warehouse.calls[0]["budget"] <= 800
        response = await client.get("/orders/2")
        assert response.status_code == 200 and not response.json()["can_fulfill"]
        await warehouse.settle()
        print(
            "PASS orders: database rows, stock by SKU, application decision and default 800ms budget",
            flush=True,
        )

        warehouse.reset("ok")
        response = await client.get("/orders/999")
        assert response.status_code == 404 and warehouse.calls == []
        for value in ("0", "-1", "2001", "not-a-number"):
            response = await client.get("/orders/1", headers={"X-Deadline-Ms": value})
            assert response.status_code == 422
        assert warehouse.calls == []
        print(
            "PASS input policy: missing order skips stock; invalid or excessive budgets are rejected",
            flush=True,
        )

        warehouse.reset("once")
        response = await client.get("/orders/1", headers={"X-Deadline-Ms": "1500"})
        assert response.status_code == 200, response.text
        await warehouse.settle()
        budgets = [call["budget"] for call in warehouse.calls]
        assert len(budgets) == 2 and 0 < budgets[1] < budgets[0] <= 1500, budgets
        print(
            "PASS retry: one 503, then success; two GET attempts share a decreasing deadline",
            flush=True,
        )

        warehouse.reset("down")
        response = await client.get("/orders/1")
        assert response.status_code == 503, response.text
        await warehouse.settle()
        assert len(warehouse.calls) == 2
        assert (await client.get("/system/health/readyz")).status_code == 200
        warehouse.reset("invalid")
        response = await client.get("/orders/1")
        assert response.status_code == 503, response.text
        await warehouse.settle()
        assert len(warehouse.calls) == 1
        print(
            "PASS unavailable stock: exhausted retries or an invalid payload return 503, not a stock count",
            flush=True,
        )

        warehouse.reset("hold")
        try:
            response = await client.get("/orders/1", headers={"X-Deadline-Ms": "400"})
            assert response.status_code == 504, response.text
            assert warehouse.started.is_set()
            assert len(warehouse.calls) == 1
            assert 0 < warehouse.calls[0]["budget"] <= 400
        finally:
            warehouse.release.set()
            await warehouse.settle()
        print(
            "PASS timeout: stalled stock request returns 504 under the operation budget",
            flush=True,
        )

        warehouse.reset("hold")
        request = asyncio.create_task(
            client.get("/orders/1", headers={"X-Deadline-Ms": "2000"})
        )
        try:
            await asyncio.wait_for(warehouse.started.wait(), timeout=5)
            assert container.db.engine.pool.checkedout() == 0
            stop.set()
            await wait_until(lambda: not service.spec.health.ready, task)
            assert not request.done() and not container.http.is_closed
            warehouse.release.set()
            response = await request
            assert response.status_code == 200, response.text
            await asyncio.wait_for(task, timeout=10)
        finally:
            warehouse.release.set()
            if not request.done():
                request.cancel()
            await asyncio.gather(request, return_exceptions=True)
            await warehouse.settle()
    await check_closed(container)
    assert container.events[-2:] == ["unit:closed", "resources:closed"]
    print(
        "PASS shutdown: SQL connection returned before HTTP; readiness drops; active work finishes before shared clients close",
        flush=True,
    )


async def failed_startup(database_url, warehouse_url):
    bad_url = (
        make_url(database_url)
        .set(database="missing_lab_database")
        .render_as_string(hide_password=False)
    )
    settings = Settings(bad_url, warehouse_url)
    service, api, container = build_service(settings)
    try:
        await service.run(settings, stop=asyncio.Event())
    except WarmupError:
        pass
    else:
        raise AssertionError("Database warmup failure was swallowed")
    assert not service.spec.health.ready and api.bound_port is None
    await check_closed(container)
    print(
        "PASS failed startup: PostgreSQL warmup fails, no HTTP listener, opened resources close",
        flush=True,
    )


async def independent_pieces(warehouse_url, warehouse):
    class MemoryOrders:
        async def find(self, order_id):
            return Order(order_id, "sku-42", 2)

    class FixedStock:
        async def available(self, sku):
            return 1

    result = await OrderView(MemoryOrders(), FixedStock()).get(7)
    assert result == {"order_id": 7, "available": 1, "can_fulfill": False}
    warehouse.reset("ok")
    async with stock_client(warehouse_url) as client:
        assert await HttpStockReader(client).available("sku-42") == 3
    await warehouse.settle()
    assert 0 < warehouse.calls[0]["budget"] <= 5000
    print(
        "PASS independent pieces: application policy with plain objects; HTTP client without a runtime or API",
        flush=True,
    )


async def main(database_url):
    print(
        {
            name: version(name)
            for name in (
                "servicewright",
                "sqlalchemy-foundation-kit",
                "clientwright",
                "deadline-budget",
            )
        },
        flush=True,
    )
    await seed(database_url)
    warehouse = Warehouse()
    async with warehouse.running() as warehouse_url:
        async with asyncio.timeout(60):
            await scenarios(database_url, warehouse_url, warehouse)
            await failed_startup(database_url, warehouse_url)
            await independent_pieces(warehouse_url, warehouse)
    print("PASS: all composition scenarios", flush=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.CRITICAL)
    print("Starting temporary PostgreSQL 17 container...", flush=True)
    with PostgresContainer("postgres:17-alpine", driver="asyncpg") as postgres:
        asyncio.run(main(postgres.get_connection_url()))
