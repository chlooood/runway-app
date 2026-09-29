from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Goal
from app.routers.utils import get_or_404
from app.schemas import GoalCreate, GoalRead, GoalUpdate

router = APIRouter(prefix="/goals", tags=["goals"])


@router.get("", response_model=list[GoalRead])
def list_goals(db: Session = Depends(get_db)):
    return db.scalars(select(Goal).order_by(Goal.target_date)).all()


@router.get("/{goal_id}", response_model=GoalRead)
def get_goal(goal_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Goal, goal_id)


@router.post("", response_model=GoalRead, status_code=status.HTTP_201_CREATED)
def create_goal(body: GoalCreate, db: Session = Depends(get_db)):
    goal = Goal(**body.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.patch("/{goal_id}", response_model=GoalRead)
def update_goal(goal_id: int, body: GoalUpdate, db: Session = Depends(get_db)):
    goal = get_or_404(db, Goal, goal_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
    db.commit()
    db.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, Goal, goal_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
