"""create income_events, expenses, goals

Revision ID: 0001
Revises:
Create Date: 2026-09-28
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "income_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("label", sa.String(100), nullable=False),
    )
    op.create_index("ix_income_events_date", "income_events", ["date"])

    op.create_table(
        "expenses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("city", sa.String(50), nullable=False),
    )
    op.create_index("ix_expenses_date", "expenses", ["date"])
    op.create_index("ix_expenses_category", "expenses", ["category"])
    op.create_index("ix_expenses_city", "expenses", ["city"])

    op.create_table(
        "goals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("target_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("goals")
    op.drop_index("ix_expenses_city", table_name="expenses")
    op.drop_index("ix_expenses_category", table_name="expenses")
    op.drop_index("ix_expenses_date", table_name="expenses")
    op.drop_table("expenses")
    op.drop_index("ix_income_events_date", table_name="income_events")
    op.drop_table("income_events")
