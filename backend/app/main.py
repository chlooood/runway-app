"""App instantiation and router registration only."""

from fastapi import FastAPI

from app.routers import expenses, goals, income_events

app = FastAPI(title="Runway")

app.include_router(income_events.router)
app.include_router(expenses.router)
app.include_router(goals.router)
