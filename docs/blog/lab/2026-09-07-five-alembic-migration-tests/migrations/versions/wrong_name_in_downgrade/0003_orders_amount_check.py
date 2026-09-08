"""orders amount must be positive

Revision ID: 0003
Revises: 0002
"""

from alembic import op

revision = "0003"
down_revision = "0002"


def upgrade() -> None:
    # The metadata's convention turns "amount_positive" into chk_orders_amount_positive.
    op.create_check_constraint("amount_positive", "orders", "amount > 0")


def downgrade() -> None:
    op.drop_constraint("positive_amount", "orders", type_="check")
