from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field, model_validator

# Money: positive, at most 10 digits with 2 decimal places (matches Numeric(10, 2)).
Money = Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]


def normalize_city(name: str) -> str:
    """Canonical spelling of a city name: ' toronto ' -> 'Toronto', 'NEW  york' -> 'New York'.

    City is free text, and the forecast groups spending by exact string, so a
    differently typed name would silently become a second city. Trimming, collapsing
    spaces and capitalizing each word makes the common variants match. It can't fix
    real misspellings ("Toronot"); a `cities` table to pick from would.
    """
    return " ".join(word.capitalize() for word in name.split())


# Normalized before the length check, so "   " is rejected as empty.
City = Annotated[
    str,
    BeforeValidator(lambda v: normalize_city(v) if isinstance(v, str) else v),
    Field(min_length=1, max_length=50),
]


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
