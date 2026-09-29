"""Rule-based savings forecast.

Everything here is a pure function over plain values: no database session, no
FastAPI. Routers load the rows and pass them in, which keeps this unit-testable.
"""

import datetime as dt
from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

CENT = Decimal("0.01")
DAYS_PER_MONTH = Decimal(365) / Decimal(12)

# Categories treated as non-negotiable when suggesting cuts. Anything else
# (dining, entertainment, misc, ...) is considered flexible.
FIXED_CATEGORIES = frozenset({"rent", "transit", "phone", "tuition", "insurance"})


class IncomeLike(Protocol):
    date: dt.date
    amount: Decimal


class ExpenseLike(Protocol):
    date: dt.date
    amount: Decimal
    category: str
    city: str


class GoalLike(Protocol):
    target_amount: Decimal
    target_date: dt.date


class UnknownCityError(ValueError):
    """Raised when a forecast is requested for a city with no expense history."""


@dataclass(frozen=True)
class ForecastPoint:
    date: dt.date
    balance: Decimal
    projected: bool  # False = actual history, True = forecast


@dataclass(frozen=True)
class Forecast:
    as_of: dt.date
    city: str | None
    current_balance: Decimal
    monthly_spend_rate: Decimal
    city_monthly_rates: dict[str, Decimal]
    category_monthly_rates: dict[str, Decimal]  # for `city`
    known_future_income: Decimal
    projected_balance: Decimal
    target_amount: Decimal
    target_date: dt.date
    gap: Decimal  # projected_balance - target_amount; negative means short
    on_track: bool
    monthly_cut_needed: Decimal  # 0 when on track or the target date has passed
    suggested_cuts: dict[str, Decimal]  # per flexible category, per month
    cuts_close_gap: bool  # False if cutting all flexible spending still falls short
    points: list[ForecastPoint]


def monthly_spend_by_city(expenses: Iterable[ExpenseLike]) -> dict[str, Decimal]:
    """Average monthly spend per city: total spent there / calendar months with spending there.

    A partially elapsed month counts as a whole month. Fixed bills like rent land
    early in the month, so this slightly understates the rate while the current
    month is still in progress; it is kept deliberately simple so it's easy to explain.
    """
    totals: dict[str, Decimal] = defaultdict(Decimal)
    months: dict[str, set[tuple[int, int]]] = defaultdict(set)
    for e in expenses:
        totals[e.city] += e.amount
        months[e.city].add((e.date.year, e.date.month))
    return {city: (totals[city] / len(months[city])).quantize(CENT) for city in totals}


def monthly_spend_by_category(expenses: Iterable[ExpenseLike], city: str) -> dict[str, Decimal]:
    """Average monthly spend per category within one city.

    Divides by the number of months with *any* spending in that city (not months with
    spending in that category), so the categories add up to that city's monthly rate,
    give or take rounding. Sorted largest first.
    """
    totals: dict[str, Decimal] = defaultdict(Decimal)
    months: set[tuple[int, int]] = set()
    for e in expenses:
        if e.city == city:
            totals[e.category] += e.amount
            months.add((e.date.year, e.date.month))
    rates = {category: (total / len(months)).quantize(CENT) for category, total in totals.items()}
    return dict(sorted(rates.items(), key=lambda item: item[1], reverse=True))


def suggest_cuts(
    category_rates: dict[str, Decimal], monthly_cut: Decimal
) -> tuple[dict[str, Decimal], bool]:
    """Split a monthly cut across flexible categories in proportion to what each costs.

    Returns (cut per category, whether the cuts cover the full amount). Fixed categories
    (FIXED_CATEGORIES) are never cut. If the cut is at least the total flexible spend,
    every flexible category is cut to zero and the second value is False.
    """
    flexible = {c: r for c, r in category_rates.items() if c not in FIXED_CATEGORIES and r > 0}
    flexible_total = sum(flexible.values(), Decimal(0))
    if monthly_cut <= 0 or flexible_total == 0:
        return {}, monthly_cut <= 0
    if monthly_cut >= flexible_total:
        return dict(flexible), monthly_cut == flexible_total
    cuts = {c: (monthly_cut * r / flexible_total).quantize(CENT) for c, r in flexible.items()}
    return cuts, True


def forecast_goal(
    goal: GoalLike,
    income: Sequence[IncomeLike],
    expenses: Sequence[ExpenseLike],
    as_of: dt.date,
    city: str | None = None,
) -> Forecast:
    """Project the balance from `as_of` to the goal's target date and check it against the target.

    Rule:
        projected balance = current balance
                          + known income dated after as_of, up to and including the target date
                          - monthly spend rate for `city`, applied evenly per day

    - Current balance is income minus expenses dated on or before `as_of`, starting from $0.
    - `city` picks which city's historical spend rate to project with (the city toggle).
      It defaults to the city of the most recent expense, i.e. where the student lives now.
      In the Runway scenario each income season was spent in one city, so the city rate
      doubles as the "expense rate for this season".
    - If the projection falls short, the shortfall is spread evenly over the months left
      (monthly_cut_needed) and split across flexible categories by `suggest_cuts`.

    Does not handle:
    - A starting balance from before the first recorded transaction.
    - Future-dated expenses (e.g. a known tuition bill); they are ignored, not subtracted.
    - Spending that changes over the horizon (e.g. moving to the exchange city in January),
      inflation, interest, or taxes on income.
    - A target date on or before `as_of`: no projection is made; projected = current balance.

    Raises UnknownCityError if `city` is given but has no expense history.
    """
    past = [e for e in expenses if e.date <= as_of]
    rates = monthly_spend_by_city(past)
    if city is None:
        city = max(past, key=lambda e: e.date).city if past else None
    elif city not in rates:
        known = ", ".join(sorted(rates)) or "none"
        raise UnknownCityError(f"No expense history for city '{city}' (known cities: {known})")
    monthly_rate = rates.get(city, Decimal(0)) if city else Decimal(0)
    category_rates = monthly_spend_by_category(past, city) if city else {}
    daily_rate = monthly_rate / DAYS_PER_MONTH

    # Daily net cash flow, for both the actual history and known future income.
    net_by_day: dict[dt.date, Decimal] = defaultdict(Decimal)
    for i in income:
        net_by_day[i.date] += i.amount
    for e in expenses:
        if e.date <= as_of:
            net_by_day[e.date] -= e.amount

    points: list[ForecastPoint] = []
    balance = Decimal(0)
    history_start = min((d for d in net_by_day if d <= as_of), default=as_of)
    day = history_start
    while day <= as_of:
        balance += net_by_day.get(day, Decimal(0))
        points.append(ForecastPoint(day, balance.quantize(CENT), projected=False))
        day += dt.timedelta(days=1)
    current_balance = balance

    future_income = Decimal(0)
    day = as_of + dt.timedelta(days=1)
    while day <= goal.target_date:
        day_income = net_by_day.get(day, Decimal(0))
        future_income += day_income
        balance += day_income - daily_rate
        points.append(ForecastPoint(day, balance.quantize(CENT), projected=True))
        day += dt.timedelta(days=1)

    projected = balance.quantize(CENT)
    gap = projected - goal.target_amount

    days_left = (goal.target_date - as_of).days
    monthly_cut = Decimal(0)
    if gap < 0 and days_left > 0:
        monthly_cut = (-gap / (days_left / DAYS_PER_MONTH)).quantize(CENT)
    cuts, cuts_close_gap = suggest_cuts(category_rates, monthly_cut)

    return Forecast(
        as_of=as_of,
        city=city,
        current_balance=current_balance.quantize(CENT),
        monthly_spend_rate=monthly_rate,
        city_monthly_rates=rates,
        category_monthly_rates=category_rates,
        known_future_income=future_income.quantize(CENT),
        projected_balance=projected,
        target_amount=goal.target_amount,
        target_date=goal.target_date,
        gap=gap,
        on_track=gap >= 0,
        monthly_cut_needed=monthly_cut,
        suggested_cuts=cuts,
        cuts_close_gap=cuts_close_gap,
        points=points,
    )
