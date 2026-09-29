from typing import Protocol, TypeVar

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User


class Owned(Protocol):
    user_id: int


OwnedT = TypeVar("OwnedT", bound=Owned)


def get_owned_or_404(db: Session, model: type[OwnedT], obj_id: int, user: User) -> OwnedT:
    """Fetch a row by primary key that belongs to `user`, or raise a 404.

    Another user's row gets the same 404 as a missing one, so ids can't be
    probed to learn what exists.
    """
    obj = db.get(model, obj_id)
    if obj is None or obj.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{model.__name__} {obj_id} not found",
        )
    return obj
