import datetime as dt
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PlannedStay(Base):
    """A future period in a city with a planned budget (e.g. an exchange term).

    Unlike expenses, which are actuals, this is a plan: the forecast uses
    `monthly_budget` for days inside the stay instead of historical spending.
    """

    __tablename__ = "planned_stays"
    __table_args__ = (CheckConstraint("end_date >= start_date", name="ck_planned_stays_dates"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(100))
    city: Mapped[str] = mapped_column(String(50))
    start_date: Mapped[dt.date] = mapped_column(Date)
    end_date: Mapped[dt.date] = mapped_column(Date)
    monthly_budget: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    upfront_cost: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
