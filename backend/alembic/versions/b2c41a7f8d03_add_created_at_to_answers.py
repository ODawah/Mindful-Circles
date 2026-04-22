"""add created_at to answers

Revision ID: b2c41a7f8d03
Revises: 9b8d7a6c4f21
Create Date: 2026-04-22 16:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c41a7f8d03"
down_revision: Union[str, None] = "9b8d7a6c4f21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "answers",
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("answers", "created_at")
