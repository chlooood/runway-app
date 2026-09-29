import datetime as dt

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import Money, PartialUpdate


class GoalBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    target_amount: Money
    target_date: dt.date


class GoalCreate(GoalBase):
    pass


class GoalUpdate(PartialUpdate):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    target_amount: Money | None = None
    target_date: dt.date | None = None


class GoalRead(GoalBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
