"""Import every model so Base.metadata is fully populated (needed by Alembic)."""

from app.models.expense import Expense
from app.models.goal import Goal
from app.models.income_event import IncomeEvent
from app.models.planned_stay import PlannedStay
from app.models.user import User

__all__ = ["Expense", "Goal", "IncomeEvent", "PlannedStay", "User"]
