# Runway Build Log

Working log of what was built, which software engineering concepts it demonstrates, and why. Entries are short on purpose.

## 2026-09-28 — Backend structure, models, Alembic
- **Built:** `backend/app/{models,schemas,routers,services}/`, `database.py`, `main.py`; models `IncomeEvent`, `Expense`, `Goal` (one file each in `app/models/`); Alembic config (`alembic.ini`, `alembic/env.py`) and migration `0001_create_core_tables.py`.
- **Concepts:** Layered Architecture, Separation of Concerns, Dependency Injection (`get_db`), Database Migrations, Environment-Based Configuration.
- **Why:** Alembic migrations instead of `create_all` — the alternative creates tables silently with no history, so schema changes can't be reviewed, versioned, or rolled back.
- **Status:** `alembic upgrade head` applied to Docker Postgres; `alembic check` reports no drift between models and migration; downgrade/upgrade round trip verified. `.env` loaded via `python-dotenv`.

## 2026-09-28 — Pydantic schemas + CRUD endpoints
- **Built:** `app/schemas/{common,income_event,expense,goal}.py` (Create/Update/Read per resource, shared `Money` type and `PartialUpdate` base); `app/routers/{income_events,expenses,goals}.py` with list/get/POST/PATCH/DELETE; `routers/utils.py` (`get_or_404`); routers registered in `main.py`. `GET /expenses` filters by `city`/`category`.
- **Concepts:** Separation of Concerns (ORM models vs API schemas), Input Validation, RESTful API Design, Dependency Injection (`Depends(get_db)` on every route).
- **Why:** separate `Read` schemas rather than returning ORM objects directly — the alternative couples the API contract to the table layout, so any new column would silently leak into responses.
- **Verified:** smoke test of all 3 resources (201/200/204/404/422 paths) against Postgres; 33/33 checks pass, and no rows are left behind. Money serializes as JSON strings (e.g. `"9000.00"`) to keep decimal precision.

## 2026-09-28 — Synthetic seed script
- **Built:** `backend/scripts/seed.py` (`python -m scripts.seed [--reset] [--as-of] [--seed]`): Toronto co-op May–Aug (biweekly $2,300 net, Faker employer name), no work income from Sept, quarterly GST/HST credits (incl. future Oct/Jan), city-tagged expenses (Toronto ≈ $2,360/mo, Vancouver ≈ $1,955/mo), "Exchange fund" goal $5,000 by 2027-01-04.
- **Concepts:** Reproducibility (seeded Faker, explicit `--as-of`), Idempotency (`--reset` in one transaction; refuses to overwrite without it), Separation of Concerns (pure `build_seed_data` vs DB-writing `main`).
- **Why:** seeded, date-pinned generation rather than plain `random` + `date.today()` — the alternative gives different data every run, so forecast numbers and screenshots can't be reproduced or compared.
- **Verified:** same seed produces identical rows, different seed differs, no future-dated expenses; balance to date $9,427.02.

## 2026-09-28 — Forecast service, endpoint, unit tests
- **Built:** `app/services/forecast.py` (`forecast_goal`, `monthly_spend_by_city`), `app/schemas/forecast.py`, `app/routers/forecast.py` → `GET /goals/{id}/forecast?city=&as_of=`, `tests/test_forecast.py` (8 cases), `pytest.ini`. Rule: current balance + known future income up to target date − per-city monthly spend rate, applied daily; returns daily actual + projected points for the chart.
- **Concepts:** Testability, Pure Functions (functional core / imperative shell), Layered Architecture, Structural Typing (`Protocol` inputs).
- **Why:** pure service taking plain values instead of logic inline in the route — the alternative can only be tested through HTTP with a live database, making the one piece of real business logic the hardest to prove correct.
- **Verified:** 8/8 pytest pass (0.3s). Seeded data: Vancouver projects $3,257.20 vs $5,000 (−$1,742.80); Toronto toggle $1,947.23; unknown city → 422, missing goal → 404.

