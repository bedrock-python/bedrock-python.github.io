"""The parts the article leaves out: tables, repositories and the full User the snippets rely on."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from omni_box.infra.storage.postgres import OutboxEventDBBase


class Base(DeclarativeBase):
    pass


class UserRow(Base):
    # No unique constraint here: the lab adds it with the article's ALTER TABLE.
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    email: Mapped[str]
    is_employee: Mapped[bool]
    is_email_confirmed: Mapped[bool] = mapped_column(default=False)


class CompanyRow(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    domain: Mapped[str]
    employees: Mapped[int]


class OutboxEventDB(Base, OutboxEventDBBase):
    pass


@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self) -> None:
        # Normalized here, so the unique index sees one spelling per address.
        object.__setattr__(self, "value", self.value.strip().casefold())
        if "@" not in self.value:
            raise ValueError(f"not an email: {self.value!r}")

    @property
    def domain(self) -> str:
        return self.value.rsplit("@", 1)[1]

    def __str__(self) -> str:
        return self.value


class EmailChangeNotAllowed(Exception):
    pass


@dataclass(frozen=True)
class EmailChanged:
    user_id: UUID
    email: Email


class Company:
    def __init__(self, company_id: int, domain: str, employees: int) -> None:
        self.id = company_id
        self._domain = domain
        self.employees = employees

    def is_corporate(self, email: Email) -> bool:
        return email.domain == self._domain

    def change_number_of_employees(self, delta: int) -> None:
        if self.employees + delta < 0:
            raise ValueError("the number of employees cannot go negative")
        self.employees += delta


class User:
    """CanExecute / Execute from the article plus the events from its Domain Events section."""

    def __init__(self, user_id: UUID, email: Email, is_employee: bool, is_email_confirmed: bool = False) -> None:
        self.id = user_id
        self._email = email
        self._is_employee = is_employee
        self._is_email_confirmed = is_email_confirmed
        self._events: list[EmailChanged] = []

    @property
    def email(self) -> Email:
        return self._email

    @property
    def is_employee(self) -> bool:
        return self._is_employee

    def can_change_email(self) -> str | None:
        if self._is_email_confirmed:
            return "Email is already confirmed"
        return None

    def change_email(self, email: Email, company: Company) -> None:
        if (reason := self.can_change_email()) is not None:
            raise EmailChangeNotAllowed(reason)
        if email == self._email:
            return
        is_employee = company.is_corporate(email)
        if is_employee != self._is_employee:
            company.change_number_of_employees(1 if is_employee else -1)
        self._email = email
        self._is_employee = is_employee
        self._events.append(EmailChanged(self.id, email))

    def pull_events(self) -> list[EmailChanged]:
        events, self._events = self._events, []
        return events


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, user_id: UUID) -> User:
        row = await self._session.get(UserRow, user_id)
        return User(row.id, Email(row.email), row.is_employee, row.is_email_confirmed)

    async def save(self, user: User) -> None:
        # The UPDATE runs now, so a unique violation surfaces right here as IntegrityError.
        await self._session.execute(
            update(UserRow).where(UserRow.id == user.id).values(email=str(user.email), is_employee=user.is_employee)
        )


class DeferredUserRepository(UserRepository):
    """ORM-style save: the change waits in the session until the flush before commit."""

    async def save(self, user: User) -> None:
        row = await self._session.get(UserRow, user.id)
        row.email = str(user.email)
        row.is_employee = user.is_employee


class BarrierUserRepository(UserRepository):
    """Holds each transaction after its read until the other one has read too."""

    barrier: asyncio.Barrier

    async def get(self, user_id: UUID) -> User:
        user = await super().get(user_id)
        await self.barrier.wait()
        return user


class CompanyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self) -> Company:
        row = await self._session.scalar(select(CompanyRow).order_by(CompanyRow.id).limit(1))
        return Company(row.id, row.domain, row.employees)

    async def save(self, company: Company) -> None:
        await self._session.execute(update(CompanyRow).where(CompanyRow.id == company.id).values(employees=company.employees))


class DeferredCompanyRepository(CompanyRepository):
    async def save(self, company: Company) -> None:
        row = await self._session.get(CompanyRow, company.id)
        row.employees = company.employees


def is_unique_violation(error: IntegrityError, constraint: str) -> bool:
    """True when PostgreSQL rejected the statement because of this unique constraint.

    SQLAlchemy's asyncpg adapter exposes the SQLSTATE; the constraint name lives on the
    original asyncpg exception it wraps.
    """
    original = error.orig
    return (
        getattr(original, "sqlstate", None) == "23505"
        and getattr(original.__cause__, "constraint_name", None) == constraint
    )
