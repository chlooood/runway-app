import datetime as dt
from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Expense, Goal, IncomeEvent, PlannedStay
from app.routers.utils import get_or_404
from app.schemas.forecast import ForecastRead
from app.services.forecast import UnknownCityError, forecast_goal

router = APIRouter(prefix="/goals", tags=["forecast"])


@router.get("/{goal_id}/forecast", response_model=ForecastRead)
def get_goal_forecast(
    goal_id: int,
    city: str | None = None,
    as_of: dt.date | None = None,
    db: Session = Depends(get_db),
):
    """Project savings through the goal date and any planned stays.

    `city` switches the home spending baseline (days outside planned stays).
    """
    goal = get_or_404(db, Goal, goal_id)
    income = db.scalars(select(IncomeEvent)).all()
    expenses = db.scalars(select(Expense)).all()
    stays = db.scalars(select(PlannedStay)).all()
    try:
        result = forecast_goal(goal, income, expenses, as_of or dt.date.today(), city, stays)
    except UnknownCityError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc))
    return ForecastRead.model_validate({"goal_id": goal.id, **asdict(result)})
