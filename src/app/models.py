from datetime import date
from typing import Annotated

from pydantic import BaseModel, BeforeValidator


def _parse_due_date(value: object) -> date:
    if type(value) is date:
        return value
    if isinstance(value, str):
        parsed = date.fromisoformat(value)
        if parsed.isoformat() == value:
            return parsed
    raise ValueError("Due date must be a calendar date in YYYY-MM-DD format")


DueDate = Annotated[date, BeforeValidator(_parse_due_date)]


class Todo(BaseModel):
    id: int
    title: str
    is_complete: bool
    due_date: DueDate | None = None


class TodoCreate(BaseModel):
    title: str
    due_date: DueDate | None = None


class TodoDueDateUpdate(BaseModel):
    due_date: DueDate | None
