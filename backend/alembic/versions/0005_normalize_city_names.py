"""normalize existing city names

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-19

Data migration. The API now normalizes city on write (app.schemas.common.normalize_city),
so rows written before that may still say "toronto" or " Toronto". Rewrite them to the
same canonical form so they merge with the rest of their city in the forecast.

The rule is copied here rather than imported: a migration must keep doing what it did
when it was written, even if the app's rule changes later.

Downgrade is a no-op: the original spellings aren't kept, and they were the bug.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '0005'
down_revision: Union[str, None] = '0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES = ("expenses", "planned_stays")


def _normalize(name: str) -> str:
    return " ".join(word.capitalize() for word in name.split())


def upgrade() -> None:
    conn = op.get_bind()
    for table in TABLES:
        cities = conn.execute(sa.text(f"SELECT DISTINCT city FROM {table}")).scalars().all()
        for city in cities:
            if _normalize(city) != city:
                conn.execute(
                    sa.text(f"UPDATE {table} SET city = :fixed WHERE city = :city"),
                    {"fixed": _normalize(city), "city": city},
                )


def downgrade() -> None:
    pass
