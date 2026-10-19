"""index expenses and income events by (user_id, date)

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-19

Written by hand. Every query on these tables starts with `WHERE user_id = ?`: the
forecast reads all of a user's rows, and the list endpoints add `ORDER BY date`.
One (user_id, date) index serves both, and also covers the user_id foreign key
for ON DELETE CASCADE. The old single-column indexes go:
- user_id: a prefix of the new index, so redundant.
- date: nothing filters on date without user_id.
- expenses.category / expenses.city: only ever filtered alongside user_id, and with
  a handful of distinct values each matches a large share of the table.

Measured with EXPLAIN ANALYZE (warm, 3 runs each). On the seed alone (69 expenses)
every plan is well under 0.1 ms either way. With 500 extra synthetic users at 1,000
expenses each (500k rows):
- category filter: the planner ANDed ix_expenses_category in, reading ~125k index
  entries to keep 34 rows: 3.5-4.3 ms -> 0.04-0.06 ms for the demo user.
- 1,000-row user by date: 1.6-2.3 ms -> 1.2-1.4 ms. The planner still picks a bitmap
  scan + sort over reading the index in order (0.36 ms when forced), because these
  synthetic rows are spread across 1,000 heap pages.
"""
from typing import Sequence, Union

from alembic import op

revision: str = '0004'
down_revision: Union[str, None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index("ix_expenses_user_id_date", "expenses", ["user_id", "date"])
    op.drop_index("ix_expenses_user_id", table_name="expenses")
    op.drop_index("ix_expenses_date", table_name="expenses")
    op.drop_index("ix_expenses_category", table_name="expenses")
    op.drop_index("ix_expenses_city", table_name="expenses")

    op.create_index("ix_income_events_user_id_date", "income_events", ["user_id", "date"])
    op.drop_index("ix_income_events_user_id", table_name="income_events")
    op.drop_index("ix_income_events_date", table_name="income_events")


def downgrade() -> None:
    op.create_index("ix_income_events_date", "income_events", ["date"])
    op.create_index("ix_income_events_user_id", "income_events", ["user_id"])
    op.drop_index("ix_income_events_user_id_date", table_name="income_events")

    op.create_index("ix_expenses_city", "expenses", ["city"])
    op.create_index("ix_expenses_category", "expenses", ["category"])
    op.create_index("ix_expenses_date", "expenses", ["date"])
    op.create_index("ix_expenses_user_id", "expenses", ["user_id"])
    op.drop_index("ix_expenses_user_id_date", table_name="expenses")
