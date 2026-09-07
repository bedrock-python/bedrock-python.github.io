"""Who owns the transaction: repositories that commit for themselves, against a unit of work that commits once."""

import asyncio
import time

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from testcontainers.postgres import PostgresContainer

from sqlalchemy_foundation_kit import AsyncSessionManager, AsyncSQLAlchemyUnitOfWork, AsyncSQLAlchemyUowTransaction


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (CheckConstraint("amount > 0", name="chk_orders_amount_positive"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[int] = mapped_column(Integer)


# --- the shape most codebases start with: every repository commits its own work ---


class SelfCommittingUserRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, email: str) -> User:
        user = User(email=email)
        self.session.add(user)
        await self.session.commit()          # "so the id is there"
        return user


class SelfCommittingOrderRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, user_id: int, amount: int) -> Order:
        order = Order(user_id=user_id, amount=amount)
        self.session.add(order)
        await self.session.commit()
        return order


# --- the unit of work: repositories write, the use case owns the transaction ---


class UserRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, email: str) -> User:
        user = User(email=email)
        self.session.add(user)
        await self.session.flush()           # the id is there; nothing is committed
        return user


class OrderRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, user_id: int, amount: int) -> Order:
        order = Order(user_id=user_id, amount=amount)
        self.session.add(order)
        await self.session.flush()
        return order


class Transaction(AsyncSQLAlchemyUowTransaction):
    @property
    def users(self) -> UserRepo:
        return UserRepo(self.session)

    @property
    def orders(self) -> OrderRepo:
        return OrderRepo(self.session)


class PlaceOrder:
    """The use case. It owns the boundary; it never sees a session."""

    def __init__(self, uow: AsyncSQLAlchemyUnitOfWork[Transaction]) -> None:
        self.uow = uow

    async def execute(self, email: str, amount: int) -> int:
        async with self.uow.transaction() as tx:   # commits on exit, rolls back on exception
            user = await tx.users.add(email)
            order = await tx.orders.add(user.id, amount)
            return order.id


async def counts(manager: AsyncSessionManager) -> str:
    async with manager.get_session() as s:
        users = (await s.execute(select(func.count()).select_from(User))).scalar_one()
        orders = (await s.execute(select(func.count()).select_from(Order))).scalar_one()
    return f"users={users} orders={orders}"


async def reset(manager: AsyncSessionManager) -> None:
    async with manager.get_transaction() as s:
        await s.execute(text("TRUNCATE orders, users RESTART IDENTITY"))


async def main(url: str) -> None:
    manager = AsyncSessionManager(url, poolclass="async_adapted_queue")
    async with manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("--- a use case that fails on its second write (amount must be positive) ---")
    async with manager.get_session() as session:
        try:
            user = await SelfCommittingUserRepo(session).add("a@example.com")
            await SelfCommittingOrderRepo(session).add(user.id, amount=-5)
        except IntegrityError:
            await session.rollback()
    print(f"  repositories commit for themselves -> {await counts(manager)}   (a user with no order: half a use case)")
    await reset(manager)

    uow = AsyncSQLAlchemyUnitOfWork(manager.session_maker, transaction_factory=Transaction)
    try:
        await PlaceOrder(uow).execute("a@example.com", amount=-5)
    except IntegrityError:
        pass
    print(f"  the use case owns the transaction  -> {await counts(manager)}   (nothing happened)")

    print("\n--- the same use case, succeeding ---")
    order_id = await PlaceOrder(uow).execute("a@example.com", amount=10)
    print(f"  order {order_id} -> {await counts(manager)}   (one commit, both rows)")

    print("\n--- a write inside a read-only block ---")
    async with uow.query() as qx:
        await qx.users.add("sneaky@example.com")
    print(f"  after uow.query() -> {await counts(manager)}   (the write was discarded)")

    print("\n--- a savepoint: one failed step, the rest of the transaction survives ---")
    async with uow.transaction() as tx:
        user = await tx.users.add("b@example.com")
        try:
            async with tx.savepoint():
                await tx.orders.add(user.id, amount=-1)
        except IntegrityError:
            pass
        await tx.orders.add(user.id, amount=20)   # would fail without the savepoint: the transaction would be aborted
    print(f"  -> {await counts(manager)}   (the bad order rolled back, the good one and the user committed)")

    print("\n--- the use case under test, with no database ---")

    class FakeTx:
        def __init__(self) -> None:
            self.users, self.orders = self, self
            self.rows: list[tuple] = []

        async def add(self, *args):
            self.rows.append(args)
            return type("Row", (), {"id": len(self.rows)})()

    class FakeUow:
        def __init__(self) -> None:
            self.tx = FakeTx()
            self.committed = 0

        def transaction(self):
            uow = self

            class Block:
                async def __aenter__(self_):
                    return uow.tx

                async def __aexit__(self_, exc_type, *_):
                    uow.committed += exc_type is None
                    return False

            return Block()

    fake = FakeUow()
    started = time.perf_counter()
    result = await PlaceOrder(fake).execute("t@example.com", amount=7)
    print(f"  order {result}, rows written={fake.tx.rows}, commits={fake.committed}, {1000 * (time.perf_counter() - started):.1f} ms, no PostgreSQL")
    await manager.aclose()


with PostgresContainer("postgres:17-alpine") as pg:
    asyncio.run(main(pg.get_connection_url().replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)))
