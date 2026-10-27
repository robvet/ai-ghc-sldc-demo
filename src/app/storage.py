from itertools import count

from app.models import Todo

_todos: dict[int, Todo] = {}
_ids = count(1)


def list_todos() -> list[Todo]:
    return [todo.model_copy() for todo in _todos.values()]


def get(todo_id: int) -> Todo | None:
    todo = _todos.get(todo_id)
    return todo.model_copy() if todo is not None else None


def add(title: str) -> Todo:
    todo = Todo(id=next(_ids), title=title, is_complete=False)
    _todos[todo.id] = todo.model_copy()
    return todo


def update(todo: Todo) -> Todo | None:
    if todo.id not in _todos:
        return None
    _todos[todo.id] = todo.model_copy()
    return todo


def delete(todo_id: int) -> bool:
    return _todos.pop(todo_id, None) is not None


def clear() -> None:
    global _ids
    _todos.clear()
    _ids = count(1)
