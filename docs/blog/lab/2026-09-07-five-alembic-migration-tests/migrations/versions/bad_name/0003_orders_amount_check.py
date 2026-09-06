"""orders amount must be positive

Revision ID: 0003
Revises: 0002
"""

from alembic import op

revision = "0003"
down_revision = "0002"


def upgrade() -> None:
    # Raw DDL: the naming convention never sees this name.
    op.execute("ALTER TABLE orders ADD CONSTRAINT amount_positive CHECK (amount > 0)")


def downgrade() -> None:
    op.execute("ALTER TABLE orders DROP CONSTRAINT amount_positive")
