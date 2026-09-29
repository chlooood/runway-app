from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Expense, User
from app.routers.utils import get_owned_or_404
from app.schemas import ExpenseCreate, ExpenseRead, ExpenseUpdate

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("", response_model=list[ExpenseRead])
def list_expenses(
    city: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List expenses by date, optionally filtered by city and/or category."""
    query = select(Expense).where(Expense.user_id == user.id).order_by(Expense.date)
    if city is not None:
        query = query.where(Expense.city == city)
    if category is not None:
        query = query.where(Expense.category == category)
    return db.scalars(query).all()


@router.get("/{expense_id}", response_model=ExpenseRead)
def get_expense(expense_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_owned_or_404(db, Expense, expense_id, user)


@router.post("", response_model=ExpenseRead, status_code=status.HTTP_201_CREATED)
def create_expense(
    body: ExpenseCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    expense = Expense(**body.model_dump(), user_id=user.id)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.patch("/{expense_id}", response_model=ExpenseRead)
def update_expense(
    expense_id: int,
    body: ExpenseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    expense = get_owned_or_404(db, Expense, expense_id, user)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(expense_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db.delete(get_owned_or_404(db, Expense, expense_id, user))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
