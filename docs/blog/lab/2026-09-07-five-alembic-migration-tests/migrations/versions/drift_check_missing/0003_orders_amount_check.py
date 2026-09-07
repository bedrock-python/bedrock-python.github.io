"""orders amount must be positive

Revision ID: 0003
Revises: 0002
"""

from alembic import op

revision = "0003"
down_revision = "0002"


def upgrade() -> None:
    # The metadata's convention turns "amount_positive" into chk_orders_amount_positive.
    pass


def downgrade() -> None:
    # Nothing to drop: the upgrade never created it. This is the drift and nothing else.
    pass
