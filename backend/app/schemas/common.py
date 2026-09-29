from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field, model_validator

# Money: positive, at most 10 digits with 2 decimal places (matches Numeric(10, 2)).
Money = Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]


class PartialUpdate(BaseModel):
    """Base for PATCH bodies: every field is optional, but none may be sent as null.

    Omitting a field leaves it unchanged; sending `null` would violate the
    NOT NULL columns, so it is rejected here as a 422 instead of a DB error.
    """

    @model_validator(mode="after")
    def _reject_explicit_nulls(self):
        nulls = [name for name in self.model_fields_set if getattr(self, name) is None]
        if nulls:
            raise ValueError(f"fields cannot be null: {', '.join(sorted(nulls))}")
        return self
