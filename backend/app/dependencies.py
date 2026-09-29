"""Request-scoped dependencies shared by routers."""

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User


def get_current_user(db: Session = Depends(get_db)) -> User:
    """The user every request acts as.

    Runway is a single-user demo with no login, so this returns the demo user
    (the lowest id). It is the one place to swap in real authentication later:
    routes already depend on it instead of assuming who the user is.
    """
    user = db.scalars(select(User).order_by(User.id).limit(1)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No user exists yet; run the migrations or the seed script.",
        )
    return user
