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

## 2026-09-28 — Config module, CORS, typed frontend API client
- **Built:** `backend/app/config.py` (single place for env config; `database.py`, Alembic, `main.py` import from it); CORS middleware in `main.py` from `CORS_ORIGINS`; frontend `strict` TS, `src/env.d.ts`, `.env.example` (`VITE_API_BASE_URL`), `src/api/types.ts` (wire + app types), `src/api/client.ts` (`getGoals`, `getIncomeEvents`, `getExpenses`, `getForecast`).
- **Concepts:** Principle of Least Privilege (CORS allow-list, not `*`), Environment-Based Configuration, Type Safety (`strict`, typed responses), Adapter Pattern (wire → app types at one boundary).
- **Why:** convert money strings to numbers once in the client instead of in each component — the alternative scatters `Number(...)` calls through the UI, and one missed call quietly turns `+` into string concatenation.
- **Verified:** preflight from `localhost:5173` → 200, other origin → 400; `tsc -b` and `oxlint` clean; 8/8 pytest still pass; Alembic still resolves config.

## 2026-09-29 — Per-category breakdown + suggested cuts; seed scenario update
- **Built:** `services/forecast.py` adds `monthly_spend_by_category` and `suggest_cuts` (shortfall ÷ months left, split across flexible categories in proportion to spend; fixed categories like transit never cut; flags when cutting all flexible spend still isn't enough). Forecast response gains `category_monthly_rates`, `monthly_cut_needed`, `suggested_cuts`, `cuts_close_gap`; frontend types/adapter updated. Seed: $2,000 starting savings, $1,700 biweekly pay, no rent/groceries/phone.
- **Concepts:** Single Responsibility (`suggest_cuts` is its own tested function), Testability (4 new cases, 12 total).
- **Why:** compute cuts in the backend service instead of the React component — the alternative puts business rules where pytest can't reach them and would need re-implementing for any other client.
- **Verified:** 12/12 pytest pass; `tsc -b` clean. Seeded forecast: $13,576.38 projected vs $5,000 (on track, no cuts); Toronto toggle $13,001.97.

## 2026-09-29 — Frontend: goal card, cash flow chart, category breakdown, city toggle
- **Built:** `frontend/src/components/{CityToggle,GoalProgressCard,CashFlowChart,CategoryBreakdown}.tsx` (+ co-located CSS), `hooks/useRunwayData.ts` (fetching + discriminated-union state), `utils/format.ts`, `App.tsx` (city state + layout only), warm palette tokens in `index.css`, Nunito font; removed Vite template assets.
- **Concepts:** Component Composition (small typed-prop components), Separation of Concerns (data hook vs presentational components), Race Condition handling (stale responses ignored on city switch), Accessibility (`aria-pressed` toggle, `role="progressbar"`).
- **Why:** a `useRunwayData` hook returning a discriminated union instead of fetching inside each component — the alternative duplicates loading/error logic per component and lets them disagree about which city is shown.
- **Verified:** `tsc -b` + `oxlint` clean; ran API + Vite locally and checked in browser: goal card, chart (actual/projected/goal/today lines), breakdown, and city toggle updating all three.

## 2026-09-29 — Planned stays (Lyon exchange) + forecast through the exchange term
- **Built:** `models/planned_stay.py` + Alembic `0002_add_planned_stays.py` (autogenerated, reviewed; DB check `end_date >= start_date`), `schemas/planned_stay.py`, `routers/planned_stays.py` (CRUD; PATCH validates merged dates). `forecast_goal` takes `stays`: horizon runs to the last stay's end, stay days use its `monthly_budget`, `upfront_cost` charged on day one; new `horizon_end`, `projected_end_balance`, `lowest_balance(_date)`, `runs_out_on`, per-point `city`. Seed: Lyon Jan 5–Apr 30 2027, C$1,480/mo + C$2,120 upfront (synthetic EUR estimates at 1.5 CAD/EUR). Frontend types/adapter updated.
- **Concepts:** Domain Modeling (plans vs actuals as separate tables), Database Migrations (second revision via autogenerate), Defense in Depth (date rule in Pydantic, router, and a DB CHECK), Testability (3 new cases, 15 total).
- **Why:** a `planned_stays` table instead of fake future expenses for Lyon — future expenses would be mixed into "actuals", skew historical averages, and be ignored by the forecast anyway.
- **Verified:** 15/15 pytest; `alembic check` clean + downgrade/upgrade round trip; CRUD smoke (201/422/422/200/204/404); seeded forecast ends Apr 30 at $5,942.36 (Vancouver) / $5,367.95 (Toronto), never below $0.

## 2026-09-29 — Lyon in the UI; API latency fix
- **Built:** `CashFlowChart` shades each planned stay (`ReferenceArea`), marks departure with a `ReferenceDot`, and uses a custom typed tooltip ("Flights + deposit −$2,120", stay budget); `GoalProgressCard` adds a `StayOutlook` line (end-of-exchange balance, or "you'd run out around …" in coral); `CategoryBreakdown` notes the planned Lyon budget. Frontend now calls the API at `127.0.0.1` (`.env.example` documents why).
- **Concepts:** Component Composition (`StayOutlook` sub-component), Measure Before Optimizing (timed `localhost` vs `127.0.0.1`: 2,167 ms vs 48 ms).
- **Why:** fixed the slow load by changing the API host rather than adding a loading spinner or caching — the timing showed the API was already fast and the 2 s was an IPv6→IPv4 fallback on every request, so anything else would have hidden the cause.
- **Verified:** `tsc -b` + `oxlint` clean; browser: Lyon band, departure tooltip, end-of-exchange line; temporarily set goal $15k + Lyon $5k/mo to confirm short badge, capped cuts + warning, and "run out around Mar 16 in Lyon", then restored; API calls now 13–26 ms.

