# Runway Build Log

Working log of what was built, which software engineering concepts it demonstrates, and why. Entries are short on purpose.

## 2026-09-28 — Backend structure, models, Alembic
- **Built:** `backend/app/{models,schemas,routers,services}/`, `database.py`, `main.py`; models `IncomeEvent`, `Expense`, `Goal` (one file each in `app/models/`); Alembic config (`alembic.ini`, `alembic/env.py`) and migration `0001_create_core_tables.py`.
- **Concepts:** Layered Architecture, Separation of Concerns, Dependency Injection (`get_db`), Database Migrations, Environment-Based Configuration.
- **Why:** Alembic migrations instead of `create_all` — the alternative creates tables silently with no history, so schema changes can't be reviewed, versioned, or rolled back.
- **Status:** `alembic upgrade head` applied to Docker Postgres; `alembic check` reports no drift between models and migration; downgrade/upgrade round trip verified. `.env` loaded via `python-dotenv`.

