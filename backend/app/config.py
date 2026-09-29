"""All runtime configuration, read from environment variables (backend/.env locally)."""

import os

from dotenv import load_dotenv

load_dotenv()  # picks up backend/.env locally; real env vars take precedence


def _required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} environment variable is not set")
    return value


DATABASE_URL = _required("DATABASE_URL")

# Comma-separated browser origins allowed to call the API (e.g. the Vite dev server).
CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()]
