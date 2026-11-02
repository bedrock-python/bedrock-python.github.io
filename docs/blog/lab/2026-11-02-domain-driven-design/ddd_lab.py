"""Run the article's own code blocks: the domain ones in memory, the Unit of Work ones on PostgreSQL.

The blocks are read from the article itself, so what this lab checks is exactly what readers see.
"""

from __future__ import annotations

import asyncio
import re
import tempfile
from collections.abc import Sequence, Set
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from enum import Enum, StrEnum
from importlib.metadata import version
from pathlib import Path
from typing import NewType, Protocol
from unittest.mock import Mock
from uuid import UUID, uuid4

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy_foundation_kit.uow import AsyncSQLAlchemyUnitOfWork
from testcontainers.community.postgres import PostgresContainer

import support
from support import Base, CompanyRow, Email, OutboxEventDB, UserRow

HERE = Path(__file__).resolve().parent
ARTICLES = [
    HERE.parents[1] / "posts/2026-11-02-domain-driven-design.md",
    HERE.parents[3] / "translations/ru/blog/posts/2026-11-02-domain-driven-design.md",
]
FENCE = re.compile(r"(?ms)^```(python|sql)\n(.*?)^```")


def load_blocks() -> list[tuple[str, str]]:
    english, russian = (FENCE.findall(path.read_text(encoding="utf-8")) for path in ARTICLES)
    assert english == russian, "the English and Russian editions must show the same code"
    return english


BLOCKS = load_blocks()


def block(marker: str) -> str:
    found = [code for _, code in BLOCKS if marker in code]
    assert len(found) == 1, f"{marker!r} matches {len(found)} blocks"
    return found[0]


def run(marker: str, namespace: dict) -> dict:
    exec(compile(block(marker), f"<article: {marker}>", "exec"), namespace)
    return namespace


# Names the snippets take for granted. Each snippet runs in a fresh copy of this namespace.
class Status(Enum):
    REGULAR = "regular"
    ADVANCED = "advanced"

    def discount(self) -> Decimal:
        return Decimal("0.01") if self is Status.ADVANCED else Decimal(0)


class Currency(StrEnum):
    RUB = "RUB"
    USD = "USD"


class OrderStatus(Enum):
    NEW = "new"
    PAID = "paid"


@dataclass(frozen=True)
class PlacedOrder:
    product: str
    qty: int


@dataclass
class Voyage:
    capacity: int
    booked: int = 0

    def add(self, cargo: "Cargo") -> None:
        self.booked += cargo.size


@dataclass(frozen=True)
class Cargo:
    size: int


class BookingError(Exception):
    pass


class NegativeMoney(ValueError):
    pass


class CurrencyMismatch(ValueError):
    pass


class OrderIsClosed(Exception):
    pass


class EmailTaken(Exception):
    pass


def prelude() -> dict:
    return {
        "dataclass": dataclass, "field": field, "Decimal": Decimal, "date": date, "datetime": datetime,
        "timedelta": timedelta, "Sequence": Sequence, "Set": Set, "NewType": NewType, "Protocol": Protocol,
        "UUID": UUID, "Path": Path, "Email": Email, "Status": Status, "Discount": Decimal, "Currency": Currency,
        "OrderStatus": OrderStatus, "OrderId": NewType("OrderId", UUID), "Order": PlacedOrder, "Product": str,
        "Cargo": Cargo, "Voyage": Voyage, "BookingError": BookingError, "NegativeMoney": NegativeMoney,
        "CurrencyMismatch": CurrencyMismatch, "OrderIsClosed": OrderIsClosed, "EmailTaken": EmailTaken,
        "EmailChangeNotAllowed": support.EmailChangeNotAllowed, "Company": support.Company,
        "UserRepository": object, "Customer": object,
    }


def bare(cls, **attributes):
    """Snippets show behavior and skip __init__; give an instance the fields it reads."""
    instance = object.__new__(cls)
    instance.__dict__.update(attributes)
    return instance


class FakeUsers:
    def __init__(self, *users) -> None:
        self.users = {user.id: user for user in users}
        self.saved = []

    async def get(self, user_id):
        return self.users[user_id]

    async def get_by_email(self, email):
        return next((user for user in self.users.values() if user.email == email), None)

    async def save(self, user) -> None:
        self.saved.append(user)


@dataclass
class PlainUser:
    id: UUID
    email: Email

    def change_email(self, email: Email) -> None:
        self.email = email


async def check_domain() -> None:
    ns = run("class PersonService", prelude())
    person = ns["Person"]("Ann", "ann@mycorp.com", is_employee=True)
    ns["PersonService"]().set_email(person, "ann@gmail.com")
    assert person.is_employee, "the anemic version leaves the flag stale, as the article says"

    run("# Before: every service checks the rules", prelude())

    ns = run("class CustomerService", prelude())

    @dataclass
    class MutableCustomer:
        orders: list = field(default_factory=list)
        status: Status = Status.REGULAR

    customer = MutableCustomer()
    for _ in range(11):
        ns["CustomerService"]().add_order(customer, "tea", 1)
    assert customer.status is Status.ADVANCED

    ns = run("return tuple(self._orders)", prelude())
    customer = ns["Customer"]("Ann", Email("ann@example.com"))
    for _ in range(10):
        customer.add_order("tea", 1)
    assert customer.status is Status.REGULAR
    customer.add_order("tea", 1)
    assert customer.status is Status.ADVANCED and len(customer.orders) == 11
    print("rich model: the 11th order makes the customer Advanced; orders are read-only")

    ns = run("voyage.capacity * 1.1:", prelude())
    voyage = Voyage(capacity=100, booked=105)
    try:
        ns["book"](Cargo(6), voyage)
        raise AssertionError("111% must be refused")
    except BookingError:
        pass
    ns = run("class OverbookingPolicy", prelude())
    policy = ns["OverbookingPolicy"]()
    assert policy.allows(Cargo(5), voyage) and not policy.allows(Cargo(6), voyage)
    ns["book"](Cargo(5), voyage, policy)
    assert voyage.booked == 110
    print("overbooking: 110% accepted, 111% refused by the named policy")

    ns = run('self._directory.glob("audit_*.txt")', prelude())
    with tempfile.TemporaryDirectory() as directory:
        manager = bare(ns["AuditManager"], _directory=Path(directory), _max_entries=2)
        for visitor in ("Peter", "Jane", "Alice"):
            manager.add_record(visitor, datetime(2026, 4, 6, 16, 30))
        assert sorted(path.name for path in Path(directory).iterdir()) == ["audit_0001.txt", "audit_0002.txt"]

    ns = run("class FileUpdate", prelude())
    run("def test_new_file_is_created_when_the_last_one_is_full", ns)
    ns["test_new_file_is_created_when_the_last_one_is_full"]()
    manager = ns["AuditManager"](max_entries=3)
    assert manager.add_record([], "Bob", datetime(2026, 1, 1)) == ns["FileUpdate"]("audit_0001.txt", "Bob;2026-01-01T00:00:00")
    persister = Mock()
    persister.read_directory.return_value = []
    service = bare(ns["AuditService"], _persister=persister, _manager=manager, _directory="audit")
    service.add_record("Bob", datetime(2026, 1, 1))
    persister.apply_update.assert_called_once_with("audit", ns["FileUpdate"]("audit_0001.txt", "Bob;2026-01-01T00:00:00"))
    print("functional core: the decision is tested without a disk; the shell applies it")

    ann, bob = PlainUser(uuid4(), Email("ann@example.com")), PlainUser(uuid4(), Email("bob@example.com"))
    ns = run("other = await self._users.get_by_email(email)", prelude())
    users = FakeUsers(ann, bob)
    controller = bare(ns["UserController"], _users=users)
    assert await controller.change_email(ann.id, Email("bob@example.com")) == "Email is taken" and not users.saved
    assert await controller.change_email(ann.id, Email("ann@new.example")) == "OK"

    ns = run("users: UserRepository", prelude())
    user = bare(ns["User"], id=ann.id, _email=Email("ann@example.com"))
    try:
        await user.change_email(Email("bob@example.com"), FakeUsers(ann, bob))
        raise AssertionError("taken address accepted")
    except EmailTaken:
        pass

    ns = run("taken: Set[Email]", prelude())
    user = bare(ns["User"], _email=Email("ann@example.com"))
    user.change_email(Email("ann@example.com"), {Email("ann@example.com")})
    try:
        user.change_email(Email("bob@example.com"), {Email("ann@example.com"), Email("bob@example.com")})
        raise AssertionError("taken address accepted")
    except EmailTaken:
        pass
    print("trilemma: the three options behave as described")

    source = block("def can_change_email")
    assert "assert " not in source
    ns = run("def can_change_email", prelude())
    company = support.Company(1, "mycorp.com", employees=1)
    user = bare(ns["User"], id=uuid4(), _email=Email("ann@gmail.com"), _is_employee=False, _is_email_confirmed=False)
    users = FakeUsers(user)
    companies = Mock()
    companies.get = Mock(side_effect=lambda: asyncio.sleep(0, company))
    companies.save = Mock(side_effect=lambda c: asyncio.sleep(0))
    controller = bare(ns["UserController"], _users=users, _companies=companies)
    assert await controller.change_email(user.id, Email("ann@mycorp.com")) == "OK"
    assert company.employees == 2 and user._is_employee
    user._is_email_confirmed = True
    assert await controller.change_email(user.id, Email("ann@gmail.com")) == "Email is already confirmed"
    try:
        user.change_email(Email("ann@gmail.com"), company)
        raise AssertionError("change_email ran around the check")
    except support.EmailChangeNotAllowed:
        pass
    print("CanExecute / Execute: the controller asks first; calling around the check raises")

    ns = run("class Money:", prelude())
    Money = ns["Money"]
    rub = lambda amount: Money(Decimal(amount), Currency.RUB)
    assert rub(5) == rub(5) and hash(rub(5)) == hash(rub(5))
    assert rub(2) + rub(3) == rub(5) and rub(2) * 3 == rub(6) and rub(7) > rub(6)
    for bad in (lambda: rub(-1), lambda: rub(1) + Money(Decimal(1), Currency.USD)):
        try:
            bad()
            raise AssertionError("invalid money accepted")
        except (NegativeMoney, CurrencyMismatch):
            pass

    entity = dict(prelude(), Money=Money)
    ns = run("def __hash__(self) -> int:", entity)
    order_id = uuid4()
    first, second = ns["Order"](order_id, Currency.RUB), ns["Order"](order_id, Currency.RUB)
    second.add_item(rub(10))
    assert first == second and len({first, second}) == 1 and first != ns["Order"](uuid4(), Currency.RUB)
    print("value object and entity: equal by value, equal by id, both hashable")

    @dataclass
    class Account:
        currency: Currency
        balance: Decimal

        def withdraw(self, amount) -> None:
            self.balance -= amount.amount

        def deposit(self, amount) -> None:
            self.balance += amount.amount

    ns = run("def transfer(", prelude())
    source, target = Account(Currency.RUB, Decimal(100)), Account(Currency.RUB, Decimal(0))
    ns["transfer"](source, target, rub(30))
    assert (source.balance, target.balance) == (70, 30)

    @dataclass(frozen=True)
    class InvoiceCustomer:
        payment_grace_period: timedelta

    @dataclass(frozen=True)
    class Invoice:
        due_date: date
        customer: InvoiceCustomer

    ns = run("class DelinquentInvoice", prelude())
    invoice = Invoice(date(2026, 10, 1), InvoiceCustomer(timedelta(days=14)))
    assert ns["DelinquentInvoice"](date(2026, 10, 16)).is_satisfied_by(invoice)
    assert not ns["DelinquentInvoice"](date(2026, 10, 15)).is_satisfied_by(invoice)

    ns = run("class MessageBus", prelude())
    bus = Mock(spec=ns["Bus"])
    user_id = uuid4()
    ns["MessageBus"](bus).send_email_changed(user_id, Email("new@example.com"))
    bus.send.assert_called_once_with(f"Type: USER EMAIL CHANGED; Id: {user_id}; NewEmail: new@example.com")
    print("domain service, specification and the bus wrapper behave as described")


async def counts(session_factory) -> tuple[int, int]:
    async with session_factory() as session:
        employees = await session.scalar(select(CompanyRow.employees))
        outbox = await session.scalar(select(func.count()).select_from(OutboxEventDB))
        return employees, outbox


async def email_of(session_factory, user_id) -> str:
    async with session_factory() as session:
        return (await session.get(UserRow, user_id)).email


async def check_postgres(url: str) -> None:
    engine = create_async_engine(url)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
            await connection.execute(text(block("ALTER TABLE users")))
            print("PostgreSQL", await connection.scalar(text("SHOW server_version")))
        print(", ".join(f"{name} {version(name)}" for name in ("sqlalchemy-foundation-kit", "omni-box", "SQLAlchemy", "asyncpg")))

        ann, bob, cid, dan = (uuid4() for _ in range(4))
        async with session_factory.begin() as session:
            session.add(CompanyRow(id=1, domain="mycorp.com", employees=1))
            session.add_all([
                UserRow(id=ann, email="ann@gmail.com", is_employee=False),
                UserRow(id=bob, email="bob@gmail.com", is_employee=False),
                UserRow(id=cid, email="cid@gmail.com", is_employee=False, is_email_confirmed=True),
                UserRow(id=dan, email="dan@gmail.com", is_employee=False),
            ])

        namespace = run("class IdentityTransaction(AsyncSQLAlchemyUowTransaction):\n    \"\"\"Repositories", {
            "session_factory": session_factory,
            "UserRepository": support.UserRepository,
            "CompanyRepository": support.CompanyRepository,
        })
        assembled = run("def to_outbox", {
            # "users and companies, as above": the second class extends the first one.
            "AsyncSQLAlchemyUowTransaction": namespace["IdentityTransaction"],
            "AsyncSQLAlchemyUnitOfWork": AsyncSQLAlchemyUnitOfWork,
            "OutboxEventDB": OutboxEventDB, "EmailChanged": support.EmailChanged,
            "is_unique_violation": support.is_unique_violation, "UUID": UUID, "Email": Email,
        })
        change_email = assembled["change_email"]
        uow = AsyncSQLAlchemyUnitOfWork(session_factory, assembled["IdentityTransaction"])

        assert await change_email(uow, ann, Email("Ann@MyCorp.com")) == "OK"
        assert await email_of(session_factory, ann) == "ann@mycorp.com"
        assert await counts(session_factory) == (2, 1)
        async with session_factory() as session:
            event = await session.scalar(select(OutboxEventDB))
            assert (event.aggregate_type, event.aggregate_id, event.event_type) == ("user", ann, "user.email_changed")
            assert event.payload == {"user_id": str(ann), "email": "ann@mycorp.com"}
        print("change_email: user, company and the outbox row committed together")

        assert await change_email(uow, cid, Email("cid@example.com")) == "Email is already confirmed"
        assert await change_email(uow, bob, Email("ann@mycorp.com")) == "Email is taken"
        assert await email_of(session_factory, bob) == "bob@gmail.com" and await counts(session_factory) == (2, 1)
        print("confirmed email and a taken address: nothing written")

        def broken_outbox(event):
            raise RuntimeError("outbox write failed")

        assembled["to_outbox"], to_outbox = broken_outbox, assembled["to_outbox"]
        try:
            await change_email(uow, bob, Email("bob@mycorp.com"))
            raise AssertionError("the failure must propagate")
        except RuntimeError:
            pass
        finally:
            assembled["to_outbox"] = to_outbox
        assert await email_of(session_factory, bob) == "bob@gmail.com" and await counts(session_factory) == (2, 1)
        print("a failed outbox write rolls the user and the company back")

        # Both transactions read before either writes: no check in code can see the other one.
        support.BarrierUserRepository.barrier = asyncio.Barrier(2)

        class RacingTransaction(assembled["IdentityTransaction"]):
            @property
            def users(self):
                return support.BarrierUserRepository(self.session)

        racing = AsyncSQLAlchemyUnitOfWork(session_factory, RacingTransaction)
        results = await asyncio.gather(
            change_email(racing, bob, Email("shared@gmail.com")),
            change_email(racing, dan, Email("shared@gmail.com")),
        )
        assert sorted(results) == ["Email is taken", "OK"], results
        emails = {await email_of(session_factory, bob), await email_of(session_factory, dan)}
        assert "shared@gmail.com" in emails and len(emails) == 2
        assert await counts(session_factory) == (2, 2)
        print("race: both read the address as free; the constraint let one commit:", results)

        class DeferredTransaction(assembled["IdentityTransaction"]):
            @property
            def users(self):
                return support.DeferredUserRepository(self.session)

            @property
            def companies(self):
                return support.DeferredCompanyRepository(self.session)

        deferred = AsyncSQLAlchemyUnitOfWork(session_factory, DeferredTransaction)
        before = await email_of(session_factory, bob), await counts(session_factory)
        assert await change_email(deferred, bob, Email("ann@mycorp.com")) == "Email is taken"
        assert (await email_of(session_factory, bob), await counts(session_factory)) == before
        print("ORM-tracked saves: the violation surfaces at the flush before commit, as IntegrityError")
    finally:
        await engine.dispose()


async def main() -> None:
    print("article code blocks:", len(BLOCKS))
    await check_domain()
    with PostgresContainer("postgres:17-alpine", driver="asyncpg") as postgres:
        await check_postgres(postgres.get_connection_url())
    print("PASS: article snippets")


if __name__ == "__main__":
    asyncio.run(main())
