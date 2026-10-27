from app import storage
from app.models import Todo, TodoCreate


class TodoNotFoundError(LookupError):
    def __init__(self, todo_id: int) -> None:
        super().__init__(f"Todo {todo_id} not found")


def list_todos() -> list[Todo]:
    return storage.list_todos()


def create_todo(todo: TodoCreate) -> Todo:
    return storage.add(todo.title)


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
