from datetime import date, datetime

import pytest
from pydantic import ValidationError

from app import service
from app.models import Todo, TodoCreate, TodoDueDateUpdate


def test_list_todos_starts_empty():
    assert service.list_todos() == []


def test_create_todo():
    todo = service.create_todo(TodoCreate(title="Demo task"))

    assert todo.model_dump() == {
        "id": 1, "title": "Demo task", "is_complete": False, "due_date": None
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
        "id": todo.id, "title": todo.title, "is_complete": True, "due_date": None
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


def test_create_todo_without_due_date() -> None:
    todo = service.create_todo(TodoCreate(title="Undated"))

    assert todo.due_date is None
    assert service.list_todos()[0].due_date is None


def test_create_todo_with_due_date() -> None:
    todo = service.create_todo(
        TodoCreate(title="Dated", due_date="2026-10-27")
    )

    assert todo.due_date == date(2026, 10, 27)
    assert service.list_todos()[0].due_date == date(2026, 10, 27)


def test_set_due_date() -> None:
    todo = service.create_todo(TodoCreate(title="Set date"))

    updated = service.update_due_date(
        todo.id, TodoDueDateUpdate(due_date=date(2026, 10, 27))
    )

    assert updated.due_date == date(2026, 10, 27)
    assert service.list_todos()[0].due_date == date(2026, 10, 27)


def test_change_due_date() -> None:
    todo = service.create_todo(
        TodoCreate(title="Reschedule", due_date=date(2026, 10, 27))
    )

    updated = service.update_due_date(
        todo.id, TodoDueDateUpdate(due_date=date(2026, 10, 29))
    )

    assert updated.due_date == date(2026, 10, 29)
    assert service.list_todos()[0].due_date == date(2026, 10, 29)


def test_clear_due_date() -> None:
    todo = service.create_todo(
        TodoCreate(title="Clear date", due_date=date(2026, 10, 27))
    )

    updated = service.update_due_date(
        todo.id, TodoDueDateUpdate(due_date=None)
    )

    assert updated.due_date is None
    assert service.list_todos()[0].due_date is None


def test_update_due_date_preserves_other_fields() -> None:
    todo = service.create_todo(TodoCreate(title="Keep fields"))
    completed = service.complete_todo(todo.id)

    updated = service.update_due_date(
        todo.id, TodoDueDateUpdate(due_date=date(2026, 10, 27))
    )

    assert updated.model_dump(exclude={"due_date"}) == completed.model_dump(
        exclude={"due_date"}
    )
    assert service.list_todos() == [updated]


def test_update_due_date_unknown_todo() -> None:
    with pytest.raises(service.TodoNotFoundError, match="Todo 999 not found"):
        service.update_due_date(999, TodoDueDateUpdate(due_date=None))


def test_overdue_includes_yesterday() -> None:
    todo = service.create_todo(
        TodoCreate(title="Yesterday", due_date=date(2026, 10, 27))
    )

    assert service.list_overdue_todos(today=date(2026, 10, 28)) == [todo]


def test_overdue_excludes_today() -> None:
    service.create_todo(
        TodoCreate(title="Today", due_date=date(2026, 10, 28))
    )

    assert service.list_overdue_todos(today=date(2026, 10, 28)) == []


def test_overdue_excludes_future_dates() -> None:
    service.create_todo(
        TodoCreate(title="Tomorrow", due_date=date(2026, 10, 29))
    )

    assert service.list_overdue_todos(today=date(2026, 10, 28)) == []


def test_overdue_excludes_completed_todos() -> None:
    todo = service.create_todo(
        TodoCreate(title="Finished", due_date=date(2026, 10, 27))
    )
    service.complete_todo(todo.id)

    assert service.list_overdue_todos(today=date(2026, 10, 28)) == []


def test_overdue_excludes_undated_todos() -> None:
    service.create_todo(TodoCreate(title="Undated"))

    assert service.list_overdue_todos(today=date(2026, 10, 28)) == []


def test_overdue_preserves_insertion_order() -> None:
    first = service.create_todo(
        TodoCreate(title="First", due_date=date(2026, 10, 27))
    )
    service.create_todo(TodoCreate(title="Undated"))
    second = service.create_todo(
        TodoCreate(title="Second", due_date=date(2026, 10, 25))
    )
    service.create_todo(
        TodoCreate(title="Future", due_date=date(2026, 10, 29))
    )

    assert service.list_overdue_todos(today=date(2026, 10, 28)) == [first, second]


def test_overdue_uses_supplied_today() -> None:
    todo = service.create_todo(
        TodoCreate(title="Boundary", due_date=date(2000, 1, 1))
    )

    assert service.list_overdue_todos(today=date(2000, 1, 1)) == []
    assert service.list_overdue_todos(today=date(2000, 1, 2)) == [todo]


def test_all_view_includes_every_todo() -> None:
    overdue = service.create_todo(
        TodoCreate(title="Overdue", due_date=date(2026, 10, 27))
    )
    today = service.create_todo(
        TodoCreate(title="Today", due_date=date(2026, 10, 28))
    )
    future = service.create_todo(
        TodoCreate(title="Future", due_date=date(2026, 10, 29))
    )
    undated = service.create_todo(TodoCreate(title="Undated"))
    completed = service.complete_todo(
        service.create_todo(
            TodoCreate(title="Completed", due_date=date(2026, 10, 26))
        ).id
    )

    assert service.list_todos() == [overdue, today, future, undated, completed]


def test_complete_todo_preserves_due_date() -> None:
    todo = service.create_todo(
        TodoCreate(title="Finish dated", due_date=date(2026, 10, 27))
    )

    completed = service.complete_todo(todo.id)

    assert completed.is_complete is True
    assert completed.due_date == date(2026, 10, 27)
    assert service.list_todos()[0].due_date == date(2026, 10, 27)


def test_due_date_update_requires_field() -> None:
    with pytest.raises(ValidationError):
        TodoDueDateUpdate()


def test_due_date_update_accepts_calendar_string() -> None:
    update = TodoDueDateUpdate(due_date="2026-10-27")

    assert update.due_date == date(2026, 10, 27)


@pytest.mark.parametrize("model", [Todo, TodoCreate, TodoDueDateUpdate])
@pytest.mark.parametrize(
    "value",
    [
        "2026-02-30",
        "2026-10-27T00:00:00",
        "20261027",
        0,
        0.0,
        True,
        [],
        {},
        datetime(2026, 10, 27),
    ],
)
def test_due_date_rejects_non_calendar_dates(
    model: type[Todo] | type[TodoCreate] | type[TodoDueDateUpdate],
    value: object,
) -> None:
    fields = {"due_date": value}
    if model is not TodoDueDateUpdate:
        fields["title"] = "Invalid date"
    if model is Todo:
        fields.update(id=1, is_complete=False)

    with pytest.raises(ValidationError):
        model(**fields)
