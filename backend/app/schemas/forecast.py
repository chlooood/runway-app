import datetime as dt
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ForecastPointRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    date: dt.date
    balance: Decimal
    projected: bool
    city: str | None


class StayWindowRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    label: str
    city: str
    start_date: dt.date
    end_date: dt.date
    monthly_budget: Decimal
    upfront_cost: Decimal


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
    stays: list[StayWindowRead]
    horizon_end: dt.date
    projected_end_balance: Decimal
    lowest_balance: Decimal
    lowest_balance_date: dt.date
    runs_out_on: dt.date | None
    points: list[ForecastPointRead]
