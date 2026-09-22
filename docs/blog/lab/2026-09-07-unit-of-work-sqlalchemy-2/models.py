"""Tables used by the article; the lab creates them in its own PostgreSQL container."""

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (CheckConstraint("delivery_cents >= 0", name="delivery_nonnegative"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str]
    delivery_cents: Mapped[int] = mapped_column(default=0)


class OrderEvent(Base):
    __tablename__ = "order_events"
    __table_args__ = (CheckConstraint("kind <> ''", name="event_kind_nonempty"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    kind: Mapped[str]


class NewsletterSubscription(Base):
    __tablename__ = "newsletter_subscriptions"
    __table_args__ = (CheckConstraint("email <> ''", name="email_nonempty"),)

    email: Mapped[str] = mapped_column(primary_key=True)
