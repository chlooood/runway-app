import datetime as dt

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import Money, PartialUpdate


class IncomeEventBase(BaseModel):
    date: dt.date
    amount: Money
    label: str = Field(min_length=1, max_length=100)


class IncomeEventCreate(IncomeEventBase):
    pass


class IncomeEventUpdate(PartialUpdate):
    date: dt.date | None = None
    amount: Money | None = None
    label: str | None = Field(default=None, min_length=1, max_length=100)


class IncomeEventRead(IncomeEventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
