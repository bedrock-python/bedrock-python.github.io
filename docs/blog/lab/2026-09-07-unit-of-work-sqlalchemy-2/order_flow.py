"""Executable article snippets. Each context gets its own session."""

# snippet:setup
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


def open_database(url):
    engine = create_async_engine(
        url, pool_size=2, max_overflow=0, pool_timeout=0.5,
    )
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    return engine, sessions
# /snippet:setup


# snippet:broken
from models import Order, OrderEvent


async def place_order_broken(sessions, sku, *, event_kind="created"):
    async with sessions() as session:
        order = Order(sku=sku, delivery_cents=0)
        session.add(order)
        await session.commit()

        session.add(OrderEvent(order_id=order.id, kind=event_kind))
        await session.commit()
        return {"order_id": order.id}
# /snippet:broken


# snippet:native
async def place_order_native(sessions, sku, *, event_kind="created"):
    async with sessions.begin() as session:
        order = Order(sku=sku, delivery_cents=0)
        session.add(order)
        await session.flush()
        session.add(OrderEvent(order_id=order.id, kind=event_kind))
        result = {"order_id": order.id}
    return result
# /snippet:native


# snippet:repositories
class OrderRepository:
    def __init__(self, session):
        self.session = session

    async def add(self, sku, delivery_cents=0):
        order = Order(sku=sku, delivery_cents=delivery_cents)
        self.session.add(order)
        await self.session.flush()
        return order


class EventRepository:
    def __init__(self, session):
        self.session = session

    async def add(self, order_id, kind="created"):
        self.session.add(OrderEvent(order_id=order_id, kind=kind))
        await self.session.flush()
# /snippet:repositories


# snippet:uow
from sqlalchemy_foundation_kit import (
    AsyncSQLAlchemyUnitOfWork,
    AsyncSQLAlchemyUowTransaction,
)


class OrderTransaction(AsyncSQLAlchemyUowTransaction):
    @property
    def orders(self):
        return OrderRepository(self.session)

    @property
    def events(self):
        return EventRepository(self.session)


def make_uow(sessions):
    return AsyncSQLAlchemyUnitOfWork(
        sessions, transaction_factory=OrderTransaction,
    )


async def place_order(uow, sku, *, delivery_cents=0, event_kind="created"):
    async with uow.transaction() as tx:
        order = await tx.orders.add(sku, delivery_cents)
        await tx.events.add(order.id, event_kind)
        result = {"order_id": order.id}
    return result
# /snippet:uow


# snippet:external
async def place_order_after_quote(uow, quote_shipping, sku):
    delivery_cents = await quote_shipping(sku)
    return await place_order(uow, sku, delivery_cents=delivery_cents)
# /snippet:external


# snippet:parallel
import asyncio


async def place_independent_orders(uow, skus):
    async with asyncio.TaskGroup() as group:
        tasks = [group.create_task(place_order(uow, sku)) for sku in skus]
    return [task.result() for task in tasks]
# /snippet:parallel


# snippet:savepoint
from sqlalchemy.exc import IntegrityError

from models import NewsletterSubscription


async def place_order_with_subscription(uow, sku, email):
    async with uow.transaction() as tx:
        order = await tx.orders.add(sku)
        await tx.events.add(order.id)
        try:
            async with tx.savepoint():
                tx.session.add(NewsletterSubscription(email=email))
                await tx.session.flush()
        except IntegrityError as error:
            if getattr(error.orig, "sqlstate", None) != "23505":
                raise
        result = {"order_id": order.id}
    return result
# /snippet:savepoint


# snippet:readonly
from sqlalchemy import text


async def read_order(uow, order_id):
    async with uow.query() as tx:
        await tx.session.execute(text("SET TRANSACTION READ ONLY"))
        order = await tx.session.get(Order, order_id)
        if order is None:
            raise LookupError(order_id)
        return {
            "order_id": order.id,
            "sku": order.sku,
            "delivery_cents": order.delivery_cents,
        }
# /snippet:readonly


# snippet:verify
from sqlalchemy import func, select


async def verify_rollback(uow, sessions):
    # Run against an empty lab database.
    try:
        await place_order(uow, "sku-1", event_kind="")
    except IntegrityError as error:
        assert error.orig.sqlstate == "23514"
    else:
        raise AssertionError("The CHECK constraint should reject the event")

    async with sessions() as observer:
        assert await observer.scalar(select(func.count()).select_from(Order)) == 0
        assert await observer.scalar(select(func.count()).select_from(OrderEvent)) == 0
# /snippet:verify
