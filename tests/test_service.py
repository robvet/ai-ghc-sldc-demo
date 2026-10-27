import pytest

from app import service
from app.models import TodoCreate


def test_list_todos_starts_empty():
    assert service.list_todos() == []


def test_create_todo():
    todo = service.create_todo(TodoCreate(title="Demo task"))

    assert todo.model_dump() == {
        "id": 1, "title": "Demo task", "is_complete": False
    }
    assert service.list_todos() == [todo]


def test_list_todos():
    first = service.create_todo(TodoCreate(title="First"))
    second = service.create_todo(TodoCreate(title="Second"))

    assert service.list_todos() == [first, second]
    assert first.id != second.id


def test_complete_todo():
    todo = service.create_todo(TodoCreate(title="Finish demo"))

    completed = service.complete_todo(todo.id)

    assert completed.model_dump() == {
        "id": todo.id, "title": todo.title, "is_complete": True
    }
    assert service.list_todos() == [completed]


def test_complete_todo_is_idempotent():
    todo = service.create_todo(TodoCreate(title="Finish once"))
    completed = service.complete_todo(todo.id)

    assert service.complete_todo(todo.id) == completed


def test_complete_unknown_todo():
    with pytest.raises(service.TodoNotFoundError, match="Todo 999 not found"):
        service.complete_todo(999)


def test_delete_todo():
    todo = service.create_todo(TodoCreate(title="Remove me"))
    remaining = service.create_todo(TodoCreate(title="Keep me"))

    service.delete_todo(todo.id)

    assert service.list_todos() == [remaining]


def test_delete_unknown_todo():
    with pytest.raises(service.TodoNotFoundError, match="Todo 999 not found"):
        service.delete_todo(999)


def test_deleted_todo_cannot_be_completed():
    todo = service.create_todo(TodoCreate(title="Remove me"))
    service.delete_todo(todo.id)

    with pytest.raises(service.TodoNotFoundError):
        service.complete_todo(todo.id)


def test_deleted_ids_are_not_reused():
    first = service.create_todo(TodoCreate(title="First"))
    service.delete_todo(first.id)
    second = service.create_todo(TodoCreate(title="Second"))

    assert second.id != first.id
