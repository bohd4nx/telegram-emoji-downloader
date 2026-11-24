"""Add archive cache table.

Revision ID: 0004
Revises: 0003
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

from alembic import op

revision: str = "0004"
down_revision: str = "0003"


def upgrade() -> None:
    op.create_table(
        "archive_cache",
        sa.Column("key", sa.String(64), nullable=False),
        sa.Column("file_ids", JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("key"),
    )


def downgrade() -> None:
    op.drop_table("archive_cache")
