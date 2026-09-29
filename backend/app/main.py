"""App instantiation and router registration only."""

from fastapi import FastAPI

app = FastAPI(title="Runway")

# Routers are registered here as they are built (income_events, expenses, goals).
