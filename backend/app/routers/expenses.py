from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Expense
from app.routers.utils import get_or_404
from app.schemas import ExpenseCreate, ExpenseRead, ExpenseUpdate

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("", response_model=list[ExpenseRead])
def list_expenses(
    city: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
):
    """List expenses by date, optionally filtered by city and/or category."""
    query = select(Expense).order_by(Expense.date)
    if city is not None:
        query = query.where(Expense.city == city)
    if category is not None:
        query = query.where(Expense.category == category)
    return db.scalars(query).all()


@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, Expense, expense_id)


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(body: ExpenseCreate, db: Session = Depends(get_db)):
    expense = Expense(**body.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.patch("/{expense_id}", response_model=ExpenseRead)
def update_expense(expense_id: int, body: ExpenseUpdate, db: Session = Depends(get_db)):
    expense = get_or_404(db, Expense, expense_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, Expense, expense_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
