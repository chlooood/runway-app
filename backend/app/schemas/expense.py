import datetime as dt

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import Money, PartialUpdate


class ExpenseBase(BaseModel):
    date: dt.date
    amount: Money
    category: str = Field(min_length=1, max_length=50)
    city: str = Field(min_length=1, max_length=50)


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(PartialUpdate):
    date: dt.date | None = None
    amount: Money | None = None
    category: str | None = Field(default=None, min_length=1, max_length=50)
    city: str | None = Field(default=None, min_length=1, max_length=50)


class ExpenseRead(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
