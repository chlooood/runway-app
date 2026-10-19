"""Unit tests for request validation. No database: these only build Pydantic models."""

import datetime as dt

import pytest
from pydantic import ValidationError

from app.schemas import ExpenseCreate, ExpenseUpdate, PlannedStayCreate, PlannedStayUpdate
from app.schemas.common import normalize_city


@pytest.mark.parametrize(
    ("typed", "stored"),
    [
        ("Toronto", "Toronto"),
        ("toronto", "Toronto"),
        ("  TORONTO ", "Toronto"),
        ("new   york", "New York"),
    ],
)
def test_normalize_city_makes_common_variants_match(typed, stored):
    assert normalize_city(typed) == stored


def test_expense_city_is_normalized_on_create_and_update():
    expense = ExpenseCreate(date=dt.date(2026, 10, 1), amount="12.50", category="dining", city=" toronto")
    assert expense.city == "Toronto"
    assert ExpenseUpdate(city="VANCOUVER").city == "Vancouver"


def test_planned_stay_city_is_normalized_on_create_and_update():
    stay = PlannedStayCreate(
        label="Exchange", city="lyon ", start_date=dt.date(2027, 1, 5),
        end_date=dt.date(2027, 4, 30), monthly_budget="1480.00",
    )
    assert stay.city == "Lyon"
    assert PlannedStayUpdate(city="LYON").city == "Lyon"


def test_blank_city_is_rejected_after_trimming():
    with pytest.raises(ValidationError):
        ExpenseCreate(date=dt.date(2026, 10, 1), amount="12.50", category="dining", city="   ")


def test_city_null_is_still_rejected_on_update():
    with pytest.raises(ValidationError):
        ExpenseUpdate(city=None)
