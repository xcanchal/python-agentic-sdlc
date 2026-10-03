"""create projects

Revision ID: 0693e55bc2b9
Revises:
Create Date: 2026-10-03 22:26:53.085426

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0693e55bc2b9"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("projects")
