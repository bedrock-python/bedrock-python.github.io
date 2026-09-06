"""users.is_active

Revision ID: 0004
Revises: 0003
"""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"


def upgrade() -> None:
    op.add_column("users", sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False))


def downgrade() -> None:
    op.drop_column("users", "is_active")
