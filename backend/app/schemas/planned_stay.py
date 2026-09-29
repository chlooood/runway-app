import datetime as dt
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.common import Money, PartialUpdate

# Upfront cost may be zero (e.g. flights already paid), unlike other money fields.
NonNegativeMoney = Annotated[Decimal, Field(ge=0, max_digits=10, decimal_places=2)]


class PlannedStayBase(BaseModel):
    label: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=50)
    start_date: dt.date
    end_date: dt.date
    monthly_budget: Money
    upfront_cost: NonNegativeMoney = Decimal("0")


class PlannedStayCreate(PlannedStayBase):
    @model_validator(mode="after")
    def _end_not_before_start(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date")
        return self


class PlannedStayUpdate(PartialUpdate):
    label: str | None = Field(default=None, min_length=1, max_length=100)
    city: str | None = Field(default=None, min_length=1, max_length=50)
    start_date: dt.date | None = None
    end_date: dt.date | None = None
    monthly_budget: Money | None = None
    upfront_cost: NonNegativeMoney | None = None


class PlannedStayRead(PlannedStayBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
