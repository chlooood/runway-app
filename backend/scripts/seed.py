"""Seed the database with synthetic demo data. Never real financial data.

Scenario: a student on a Toronto co-op term (May-Aug 2026, biweekly pay) who
moves back to Vancouver for a school term (Sept-Dec, no work income) and is
saving for an exchange term that starts in January 2027. Housing, groceries,
and phone are covered (e.g. living with family), so spending is transit plus
discretionary categories. The student starts May with some savings.

Generation is deterministic: the same --seed and --as-of always produce the
same rows. Expenses are only generated up to --as-of (they are "actuals");
the only future-dated rows are known scheduled income (GST/HST credits).

Usage, from backend/:
    python -m scripts.seed               # refuses if the tables already have data
    python -m scripts.seed --reset       # wipes income_events, expenses, goals first
    python -m scripts.seed --as-of 2026-09-28 --seed 7
"""

import argparse
import datetime as dt
from calendar import monthrange
from decimal import Decimal

from faker import Faker
from sqlalchemy import delete, func, select

from app.database import SessionLocal
from app.models import Expense, Goal, IncomeEvent

DATA_START = dt.date(2026, 5, 1)

# There's no separate balance table, so savings carried into May are recorded as
# an income event on the first day. The forecast treats it like any other inflow.
STARTING_SAVINGS = Decimal("2000.00")

COOP_FIRST_PAYDAY = dt.date(2026, 5, 8)
COOP_LAST_DAY = dt.date(2026, 8, 31)
COOP_NET_PAY = Decimal("1700.00")  # per biweekly paycheck, after tax

# Quarterly GST/HST credit: one past payment plus known future ones.
GST_CREDIT = Decimal("130.25")
GST_CREDIT_DATES = [dt.date(2026, 7, 3), dt.date(2026, 10, 5), dt.date(2027, 1, 5)]

GOAL = {"name": "Exchange fund", "target_amount": Decimal("5000.00"), "target_date": dt.date(2027, 1, 4)}

# Monthly spending baseline per city, by category. No rent, groceries, or phone:
# those are covered. Toronto has a monthly TTC pass; Vancouver has a U-Pass.
CITY_BASELINES = {
    "Toronto": {"transit": 156, "dining": 220, "entertainment": 110, "misc": 100},
    "Vancouver": {"transit": 60, "dining": 160, "entertainment": 80, "misc": 80},
}

# Fixed bills: (category, day of month). Charged at exactly the baseline amount.
FIXED_BILLS = [("transit", 1)]

# Variable spending: (category, min, max) transactions per month, amounts jittered.
VARIABLE_SPEND = [("dining", 4, 8), ("entertainment", 2, 4), ("misc", 1, 3)]


def city_for(day: dt.date) -> str:
    """Toronto during the co-op term, Vancouver otherwise."""
    return "Toronto" if day <= COOP_LAST_DAY else "Vancouver"


def _money(value: float) -> Decimal:
    return Decimal(str(round(value, 2)))


def build_seed_data(as_of: dt.date, seed: int) -> tuple[list[IncomeEvent], list[Expense], list[Goal]]:
    """Build (but do not save) the demo rows. Pure apart from the seeded RNG."""
    fake = Faker("en_CA")
    fake.seed_instance(seed)
    rng = fake.random

    employer = fake.company()
    income = [IncomeEvent(date=DATA_START, amount=STARTING_SAVINGS, label="Starting savings")]
    payday = COOP_FIRST_PAYDAY
    while payday <= COOP_LAST_DAY:
        income.append(IncomeEvent(date=payday, amount=COOP_NET_PAY, label=f"Co-op paycheck ({employer})"))
        payday += dt.timedelta(days=14)
    income += [IncomeEvent(date=d, amount=GST_CREDIT, label="GST/HST credit") for d in GST_CREDIT_DATES]

    expenses = []
    year, month = DATA_START.year, DATA_START.month
    while dt.date(year, month, 1) <= as_of:
        days_in_month = monthrange(year, month)[1]
        city = city_for(dt.date(year, month, 1))
        baseline = CITY_BASELINES[city]

        planned = [(dt.date(year, month, day), category, Decimal(baseline[category]))
                   for category, day in FIXED_BILLS]
        for category, low, high in VARIABLE_SPEND:
            count = rng.randint(low, high)
            for _ in range(count):
                day = dt.date(year, month, rng.randint(1, days_in_month))
                amount = _money(baseline[category] / count * rng.uniform(0.6, 1.4))
                planned.append((day, category, amount))

        expenses += [Expense(date=day, amount=amount, category=category, city=city)
                     for day, category, amount in planned if day <= as_of]
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)

    goals = [Goal(**GOAL)]
    return income, expenses, goals


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--reset", action="store_true", help="delete existing rows before seeding")
    parser.add_argument("--as-of", type=dt.date.fromisoformat, default=dt.date.today(),
                        help="last date to generate expenses for (default: today)")
    parser.add_argument("--seed", type=int, default=42, help="RNG seed (default: 42)")
    args = parser.parse_args()

    income, expenses, goals = build_seed_data(args.as_of, args.seed)
    # Totals are read before commit, which expires the ORM objects.
    earned = sum(e.amount for e in income if e.date <= args.as_of)
    spent = sum(e.amount for e in expenses)
    counts = (len(income), len(expenses), len(goals))

    with SessionLocal() as db:
        tables = (IncomeEvent, Expense, Goal)
        existing = sum(db.scalar(select(func.count()).select_from(t)) for t in tables)
        if existing and not args.reset:
            raise SystemExit(f"Database already has {existing} rows; rerun with --reset to replace them.")
        for table in tables:
            db.execute(delete(table))
        db.add_all([*income, *expenses, *goals])
        db.commit()

    print(f"Seeded {counts[0]} income events, {counts[1]} expenses, {counts[2]} goal(s) "
          f"(as of {args.as_of}, seed {args.seed}).")
    print(f"Balance to date: ${earned - spent:,.2f} (earned ${earned:,.2f}, spent ${spent:,.2f})")


if __name__ == "__main__":
    main()
