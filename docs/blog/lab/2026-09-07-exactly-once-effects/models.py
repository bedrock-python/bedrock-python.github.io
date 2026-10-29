"""Minimal order and billing tables for the event-delivery labs."""

from uuid import UUID

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from omni_box.infra.storage.postgres import InboxEventDBBase, OutboxEventDBBase


class Base(DeclarativeBase):
    pass


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(primary_key=True)


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Deliberately not unique: the lab must prove that Inbox suppresses repeats.
    order_id: Mapped[UUID]


class OutboxEventDB(Base, OutboxEventDBBase):
    pass


class InboxEventDB(Base, InboxEventDBBase):
    pass
