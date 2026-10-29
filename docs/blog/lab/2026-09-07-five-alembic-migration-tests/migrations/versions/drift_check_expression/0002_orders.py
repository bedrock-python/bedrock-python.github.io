"""orders

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"

order_status = sa.Enum("new", "paid", "shipped", name="order_status")


def upgrade() -> None:
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("status", order_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_orders"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_orders_user_id_users"),
    )
    op.create_index("idx_orders_user_id", "orders", ["user_id"])


def downgrade() -> None:
    op.drop_index("idx_orders_user_id", table_name="orders")
    op.drop_table("orders")
    order_status.drop(op.get_bind())  # the table is gone; the type it used is not, unless we say so
