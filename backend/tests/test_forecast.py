"""Unit tests for the forecast service. No database: inputs are plain dataclasses."""

import datetime as dt
from dataclasses import dataclass
from decimal import Decimal as D

import pytest

from app.services.forecast import (
    UnknownCityError,
    forecast_goal,
    monthly_spend_by_category,
    monthly_spend_by_city,
)


@dataclass
class Income:
    date: dt.date
    amount: D


@dataclass
class Expense:
    date: dt.date
    amount: D
    city: str
    category: str = "misc"


@dataclass
class Goal:
    target_amount: D
    target_date: dt.date


def day(month: int, d: int, year: int = 2026) -> dt.date:
    return dt.date(year, month, d)


def test_monthly_rate_is_total_over_months_with_spending_per_city():
    expenses = [
        Expense(day(1, 1), D("1000"), "Toronto"),
        Expense(day(1, 15), D("200"), "Toronto"),
        Expense(day(2, 1), D("800"), "Toronto"),
        Expense(day(3, 3), D("500"), "Vancouver"),  # a lone partial month counts as one month
    ]
    assert monthly_spend_by_city(expenses) == {"Toronto": D("1000.00"), "Vancouver": D("500.00")}


def test_without_future_income_balance_spends_down_at_the_city_rate():
    income = [Income(day(1, 5), D("3000"))]
    expenses = [Expense(day(1, 10), D("300"), "Vancouver")]  # $300/month
    goal = Goal(D("1000"), day(1, 31, 2027))  # exactly 365 days after as_of

    result = forecast_goal(goal, income, expenses, as_of=day(1, 31))

    assert result.current_balance == D("2700.00")
    assert result.monthly_spend_rate == D("300.00")
    assert result.projected_balance == D("-900.00")  # 2700 - 12 months * 300
    assert result.gap == D("-1900.00")
    assert result.on_track is False
    assert result.points[-1].date == goal.target_date and result.points[-1].projected


def test_known_future_income_counts_only_up_to_the_target_date():
    income = [
        Income(day(1, 5), D("3000")),
        Income(day(3, 1), D("500")),   # future, before target: counted
        Income(day(6, 1), D("999")),   # future, after target: ignored
    ]
    expenses = [Expense(day(1, 10), D("300"), "Vancouver")]
    goal = Goal(D("2000"), day(3, 31))  # 59 days after as_of

    result = forecast_goal(goal, income, expenses, as_of=day(1, 31))

    assert result.known_future_income == D("500.00")
    # 2700 + 500 - (300 * 12 / 365) * 59 days = 3200 - 581.92
    assert result.projected_balance == D("2618.08")
    assert result.on_track is True


def test_meeting_the_target_exactly_counts_as_on_track():
    income = [Income(day(1, 1), D("1000"))]
    result = forecast_goal(Goal(D("1000"), day(6, 1)), income, [], as_of=day(1, 31))

    assert result.city is None and result.monthly_spend_rate == D("0")
    assert result.gap == D("0.00")
    assert result.on_track is True


def test_city_defaults_to_most_recent_and_toggle_switches_the_rate():
    income = [Income(day(1, 1), D("10000"))]
    expenses = [
        Expense(day(1, 20), D("600"), "Toronto"),
        Expense(day(2, 10), D("300"), "Vancouver"),  # most recent: the default city
    ]
    goal = Goal(D("5000"), day(2, 28, 2027))  # 365 days after as_of
    as_of = day(2, 28)

    default = forecast_goal(goal, income, expenses, as_of)
    toronto = forecast_goal(goal, income, expenses, as_of, city="Toronto")

    assert default.city == "Vancouver"
    assert default.projected_balance == D("5500.00")  # 9100 - 12 * 300
    assert toronto.projected_balance == D("1900.00")  # 9100 - 12 * 600
    assert default.current_balance == toronto.current_balance  # toggle only affects the future


def test_unknown_city_is_rejected():
    expenses = [Expense(day(1, 10), D("300"), "Vancouver")]
    with pytest.raises(UnknownCityError, match="Montreal"):
        forecast_goal(Goal(D("1"), day(6, 1)), [], expenses, as_of=day(1, 31), city="Montreal")


def test_target_date_already_passed_returns_current_balance_without_projection():
    income = [Income(day(1, 1), D("1000"))]
    expenses = [Expense(day(1, 10), D("300"), "Vancouver")]
    result = forecast_goal(Goal(D("500"), day(1, 15)), income, expenses, as_of=day(1, 31))

    assert result.projected_balance == result.current_balance == D("700.00")
    assert not any(p.projected for p in result.points)


def test_future_dated_expenses_are_ignored():
    income = [Income(day(1, 1), D("1000"))]
    expenses = [
        Expense(day(1, 10), D("300"), "Vancouver"),
        Expense(day(3, 1), D("5000"), "Vancouver"),  # after as_of: not in balance or rate
    ]
    result = forecast_goal(Goal(D("500"), day(1, 31)), income, expenses, as_of=day(1, 31))

    assert result.current_balance == D("700.00")
    assert result.monthly_spend_rate == D("300.00")


def test_category_rates_use_the_citys_month_count_so_they_sum_to_the_city_rate():
    expenses = [
        Expense(day(1, 1), D("100"), "Vancouver", "transit"),
        Expense(day(1, 20), D("300"), "Vancouver", "dining"),
        Expense(day(2, 1), D("100"), "Vancouver", "transit"),
        Expense(day(2, 9), D("50"), "Toronto", "dining"),  # other city: excluded
    ]
    rates = monthly_spend_by_category(expenses, "Vancouver")

    # dining only happened in January but is averaged over both Vancouver months
    assert rates == {"dining": D("150.00"), "transit": D("100.00")}
    assert list(rates) == ["dining", "transit"]  # largest first
    assert sum(rates.values()) == monthly_spend_by_city(expenses)["Vancouver"]


def _short_scenario(target: str):
    """$2,500 now, $500/month spend ($100 fixed transit, $400 flexible), 12 months to go."""
    income = [Income(day(1, 5), D("3000"))]
    expenses = [
        Expense(day(1, 1), D("100"), "Vancouver", "transit"),
        Expense(day(1, 10), D("300"), "Vancouver", "dining"),
        Expense(day(1, 20), D("100"), "Vancouver", "misc"),
    ]
    return forecast_goal(Goal(D(target), day(1, 31, 2027)), income, expenses, as_of=day(1, 31))


def test_shortfall_is_spread_per_month_and_split_across_flexible_categories_only():
    result = _short_scenario("1000")  # projected -3500, so $4,500 short over 12 months

    assert result.monthly_cut_needed == D("375.00")
    assert result.suggested_cuts == {"dining": D("281.25"), "misc": D("93.75")}  # 3:1, like spend
    assert "transit" not in result.suggested_cuts
    assert result.cuts_close_gap is True


def test_cuts_are_capped_at_flexible_spend_and_flagged_when_not_enough():
    result = _short_scenario("5000")  # $8,500 short: $708.33/month, but only $400 is flexible

    assert result.monthly_cut_needed == D("708.33")
    assert result.suggested_cuts == {"dining": D("300.00"), "misc": D("100.00")}
    assert result.cuts_close_gap is False


def test_no_cuts_suggested_when_on_track():
    income = [Income(day(1, 5), D("3000"))]
    expenses = [Expense(day(1, 10), D("300"), "Vancouver", "dining")]
    result = forecast_goal(Goal(D("100"), day(3, 31)), income, expenses, as_of=day(1, 31))

    assert result.on_track is True
    assert result.monthly_cut_needed == D("0")
    assert result.suggested_cuts == {}
    assert result.cuts_close_gap is True
