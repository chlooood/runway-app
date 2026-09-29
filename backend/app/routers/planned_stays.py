from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PlannedStay
from app.routers.utils import get_or_404
from app.schemas import PlannedStayCreate, PlannedStayRead, PlannedStayUpdate

router = APIRouter(prefix="/planned-stays", tags=["planned stays"])


@router.get("", response_model=list[PlannedStayRead])
def list_planned_stays(db: Session = Depends(get_db)):
    return db.scalars(select(PlannedStay).order_by(PlannedStay.start_date)).all()


@router.get("/{stay_id}", response_model=PlannedStayRead)
def get_planned_stay(stay_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, PlannedStay, stay_id)


@router.post("", response_model=PlannedStayRead, status_code=status.HTTP_201_CREATED)
def create_planned_stay(body: PlannedStayCreate, db: Session = Depends(get_db)):
    stay = PlannedStay(**body.model_dump())
    db.add(stay)
    db.commit()
    db.refresh(stay)
    return stay


@router.patch("/{stay_id}", response_model=PlannedStayRead)
def update_planned_stay(stay_id: int, body: PlannedStayUpdate, db: Session = Depends(get_db)):
    stay = get_or_404(db, PlannedStay, stay_id)
    changes = body.model_dump(exclude_unset=True)
    # Check dates against the merged result, since a PATCH may send only one of them.
    start = changes.get("start_date", stay.start_date)
    end = changes.get("end_date", stay.end_date)
    if end < start:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="end_date cannot be before start_date",
        )
    for field, value in changes.items():
        setattr(stay, field, value)
    db.commit()
    db.refresh(stay)
    return stay


@router.delete("/{stay_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_planned_stay(stay_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, PlannedStay, stay_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
