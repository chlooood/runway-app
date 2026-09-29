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

