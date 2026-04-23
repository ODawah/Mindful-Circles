"""add asked_date to questions

Revision ID: 9b8d7a6c4f21
Revises: 83b1ebd4d9d6
Create Date: 2026-04-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9b8d7a6c4f21"
down_revision: Union[str, None] = "83b1ebd4d9d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if op.get_context().dialect.name in {"sqlite", "libsql"}:
        with op.batch_alter_table("questions") as batch_op:
            batch_op.add_column(
                sa.Column("asked_date", sa.Date(), server_default=sa.text("CURRENT_DATE"), nullable=False),
            )
    else:
        op.add_column(
            "questions",
            sa.Column("asked_date", sa.Date(), server_default=sa.text("CURRENT_DATE"), nullable=False),
        )
    op.create_index(op.f("ix_questions_asked_date"), "questions", ["asked_date"], unique=False)
    if op.get_context().dialect.name not in {"sqlite", "libsql"}:
        op.alter_column("questions", "asked_date", server_default=None)


def downgrade() -> None:
    op.drop_index(op.f("ix_questions_asked_date"), table_name="questions")
    op.drop_column("questions", "asked_date")
