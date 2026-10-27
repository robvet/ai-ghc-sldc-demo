from pydantic import BaseModel


class Todo(BaseModel):
    id: int
    title: str
    is_complete: bool


class TodoCreate(BaseModel):
    title: str
