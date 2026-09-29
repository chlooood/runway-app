import datetime as dt
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ForecastPointRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: dt.date
    balance: Decimal
    projected: bool


class ForecastRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    goal_id: int
    as_of: dt.date
    city: str | None
    current_balance: Decimal
    monthly_spend_rate: Decimal
    city_monthly_rates: dict[str, Decimal]
    category_monthly_rates: dict[str, Decimal]
    known_future_income: Decimal
    projected_balance: Decimal
    target_amount: Decimal
    target_date: dt.date
    gap: Decimal
    on_track: bool
    monthly_cut_needed: Decimal
    suggested_cuts: dict[str, Decimal]
    cuts_close_gap: bool
    points: list[ForecastPointRead]
