"""App instantiation, middleware, and router registration only."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.routers import expenses, forecast, goals, income_events

app = FastAPI(title="Runway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(income_events.router)
app.include_router(expenses.router)
app.include_router(goals.router)
app.include_router(forecast.router)
