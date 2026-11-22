"""Add language to users; migrate timestamps to timestamptz.

Revision ID: 0002
Revises: d894f41bfb7c
"""

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str = "d894f41bfb7c"


def upgrade() -> None:
    op.add_column("users", sa.Column("language", sa.String(10), nullable=False, server_default="en"))

    op.create_index("ix_users_language", "users", ["language"])

    # Migrate plain DateTime columns to timestamptz so timezone-aware datetimes work correctly.
    op.alter_column("users", "created_at", type_=sa.DateTime(timezone=True), existing_nullable=False)
    op.alter_column("users", "updated_at", type_=sa.DateTime(timezone=True), existing_nullable=False)
    op.alter_column("downloads", "created_at", type_=sa.DateTime(timezone=True), existing_nullable=False)


def downgrade() -> None:
    op.alter_column("downloads", "created_at", type_=sa.DateTime(), existing_nullable=False)
    op.alter_column("users", "updated_at", type_=sa.DateTime(), existing_nullable=False)
    op.alter_column("users", "created_at", type_=sa.DateTime(), existing_nullable=False)

    op.drop_index("ix_users_language", table_name="users")

    op.drop_column("users", "language")
