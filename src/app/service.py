from datetime import date

from app import storage
from app.models import Todo, TodoCreate, TodoDueDateUpdate


class TodoNotFoundError(LookupError):
    def __init__(self, todo_id: int) -> None:
        super().__init__(f"Todo {todo_id} not found")


def list_todos() -> list[Todo]:
    return storage.list_todos()


def list_overdue_todos(today: date) -> list[Todo]:
    return [
        todo for todo in storage.list_todos()
        if not todo.is_complete
        and todo.due_date is not None
        and todo.due_date < today
    ]


def create_todo(todo: TodoCreate) -> Todo:
    return storage.add(todo.title, todo.due_date)


def update_due_date(todo_id: int, update: TodoDueDateUpdate) -> Todo:
    todo = storage.get(todo_id)
    if todo is None:
        raise TodoNotFoundError(todo_id)
    todo.due_date = update.due_date
    updated = storage.update(todo)
    if updated is None:
        raise TodoNotFoundError(todo_id)
    return updated


def complete_todo(todo_id: int) -> Todo:
    todo = storage.get(todo_id)
    if todo is None:
        raise TodoNotFoundError(todo_id)
    todo.is_complete = True
    updated = storage.update(todo)
    if updated is None:
        raise TodoNotFoundError(todo_id)
    return updated


def delete_todo(todo_id: int) -> None:
    if not storage.delete(todo_id):
        raise TodoNotFoundError(todo_id)
