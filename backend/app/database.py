"""Engine, session factory, and the FastAPI session dependency."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Declarative base shared by every model."""


def get_db() -> Generator[Session, None, None]:
    """Yield a session per request and always close it (used with Depends)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
