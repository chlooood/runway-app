from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import IncomeEvent
from app.routers.utils import get_or_404
from app.schemas import IncomeEventCreate, IncomeEventRead, IncomeEventUpdate

router = APIRouter(prefix="/income-events", tags=["income events"])


@router.get("", response_model=list[IncomeEventRead])
def list_income_events(db: Session = Depends(get_db)):
    return db.scalars(select(IncomeEvent).order_by(IncomeEvent.date)).all()


@router.get("/{event_id}", response_model=IncomeEventRead)
def get_income_event(event_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, IncomeEvent, event_id)


@router.post("", response_model=IncomeEventRead, status_code=status.HTTP_201_CREATED)
def create_income_event(body: IncomeEventCreate, db: Session = Depends(get_db)):
    event = IncomeEvent(**body.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.patch("/{event_id}", response_model=IncomeEventRead)
def update_income_event(event_id: int, body: IncomeEventUpdate, db: Session = Depends(get_db)):
    event = get_or_404(db, IncomeEvent, event_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income_event(event_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, IncomeEvent, event_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
