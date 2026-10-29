from collections.abc import Iterator
from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import routes
from app.main import app


INVALID_DUE_DATES = [
    "2026-02-30",
    "not-a-date",
    "20261027",
    "2026-10-27T00:00:00",
    "2026-10-27T12:30:00Z",
    0,
    1793059200,
    1793059200.0,
    True,
    [],
    {},
]


@pytest.fixture
def client() -> Iterator[TestClient]:
    def fixed_today() -> date:
        return date(2026, 10, 28)

    overrides = app.dependency_overrides.copy()
    app.dependency_overrides[routes.get_today] = fixed_today
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(overrides)


@pytest.fixture
def all_todos(client: TestClient) -> list[dict[str, object]]:
    todos = []
    for title, due_date in [
        ("Yesterday", "2026-10-27"),
        ("Today", "2026-10-28"),
        ("Future", "2026-10-29"),
        ("Undated", None),
        ("Completed", "2026-10-26"),
    ]:
        response = client.post(
            "/api/todos", json={"title": title, "due_date": due_date}
        )
        assert response.status_code == 201
        todos.append(response.json())
    completed = client.patch(f"/api/todos/{todos[-1]['id']}/complete")
    assert completed.status_code == 200
    todos[-1] = completed.json()
    return todos


def test_list_todos_starts_empty(client):
    response = client.get("/api/todos")

    assert response.status_code == 200
    assert response.json() == []


def test_create_todo(client):
    response = client.post("/api/todos", json={"title": "Demo task"})

    assert response.status_code == 201
    assert response.json() == {
        "id": 1, "title": "Demo task", "is_complete": False, "due_date": None
    }


def test_list_todos(client):
    first = client.post("/api/todos", json={"title": "First"}).json()
    second = client.post("/api/todos", json={"title": "Second"}).json()

    response = client.get("/api/todos")

    assert response.status_code == 200
    assert response.json() == [first, second]


def test_create_todo_requires_title(client):
    response = client.post("/api/todos", json={})

    assert response.status_code == 422
    assert client.get("/api/todos").json() == []


def test_complete_todo(client):
    todo = client.post("/api/todos", json={"title": "Finish demo"}).json()

    response = client.patch(f"/api/todos/{todo['id']}/complete")

    assert response.status_code == 200
    assert response.json() == {**todo, "is_complete": True}
    assert client.get("/api/todos").json() == [response.json()]


def test_complete_todo_is_idempotent(client):
    todo = client.post("/api/todos", json={"title": "Finish once"}).json()
    first = client.patch(f"/api/todos/{todo['id']}/complete")

    response = client.patch(f"/api/todos/{todo['id']}/complete")

    assert response.status_code == 200
    assert response.json() == first.json()


def test_complete_unknown_todo(client):
    response = client.patch("/api/todos/999/complete")

    assert response.status_code == 404
    assert response.json() == {"detail": "Todo 999 not found"}


def test_delete_todo(client):
    todo = client.post("/api/todos", json={"title": "Remove me"}).json()
    remaining = client.post("/api/todos", json={"title": "Keep me"}).json()

    response = client.delete(f"/api/todos/{todo['id']}")

    assert response.status_code == 204
    assert response.content == b""
    assert client.get("/api/todos").json() == [remaining]


def test_delete_unknown_todo(client):
    response = client.delete("/api/todos/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Todo 999 not found"}


def test_delete_already_deleted_todo(client):
    todo = client.post("/api/todos", json={"title": "Remove once"}).json()
    client.delete(f"/api/todos/{todo['id']}")

    response = client.delete(f"/api/todos/{todo['id']}")

    assert response.status_code == 404


def test_static_ui(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "To-Do Demo App" in response.text
    assert 'id="todo-form"' in response.text
    assert 'id="todo-list"' in response.text
    assert '<label for="todo-due-date">Due date (optional)</label>' in response.text
    assert '<input id="todo-due-date" name="due_date" type="date">' in response.text
    assert 'role="group" aria-label="To-do views"' in response.text
    assert 'data-view="all" aria-pressed="true">All</button>' in response.text
    assert 'data-view="overdue" aria-pressed="false">Overdue</button>' in response.text


def test_static_javascript(client: TestClient) -> None:
    response = client.get("/app.js")

    assert response.status_code == 200
    assert "/api/todos" in response.text
    assert "/api/todos?overdue=true" in response.text
    assert "/due-date" in response.text
    assert response.text == (
        Path(__file__).resolve().parents[1] / "src/ux/app.js"
    ).read_text()


@pytest.mark.parametrize("date_fields", [{}, {"due_date": None}])
def test_create_todo_without_due_date(
    client: TestClient, date_fields: dict[str, None]
) -> None:
    response = client.post(
        "/api/todos", json={"title": "Undated", **date_fields}
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1, "title": "Undated", "is_complete": False, "due_date": None
    }
    assert client.get("/api/todos").json() == [response.json()]


def test_create_todo_with_due_date(client: TestClient) -> None:
    response = client.post(
        "/api/todos", json={"title": "Dated", "due_date": "2026-10-27"}
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1, "title": "Dated", "is_complete": False,
        "due_date": "2026-10-27",
    }
    assert client.get("/api/todos").json() == [response.json()]


@pytest.mark.parametrize("due_date", INVALID_DUE_DATES)
def test_create_todo_rejects_invalid_due_date(
    client: TestClient, due_date: object
) -> None:
    existing = client.post("/api/todos", json={"title": "Keep me"}).json()

    response = client.post(
        "/api/todos", json={"title": "Invalid", "due_date": due_date}
    )

    assert response.status_code == 422
    assert client.get("/api/todos").json() == [existing]


def test_set_due_date(client: TestClient) -> None:
    todo = client.post("/api/todos", json={"title": "Set date"}).json()

    response = client.patch(
        f"/api/todos/{todo['id']}/due-date", json={"due_date": "2026-10-27"}
    )

    assert response.status_code == 200
    assert response.json() == {**todo, "due_date": "2026-10-27"}
    assert client.get("/api/todos").json() == [response.json()]


def test_change_due_date(client: TestClient) -> None:
    todo = client.post(
        "/api/todos", json={"title": "Reschedule", "due_date": "2026-10-27"}
    ).json()

    response = client.patch(
        f"/api/todos/{todo['id']}/due-date", json={"due_date": "2026-10-29"}
    )

    assert response.status_code == 200
    assert response.json() == {**todo, "due_date": "2026-10-29"}
    assert client.get("/api/todos").json() == [response.json()]


def test_clear_due_date(client: TestClient) -> None:
    todo = client.post(
        "/api/todos", json={"title": "Clear date", "due_date": "2026-10-27"}
    ).json()

    response = client.patch(
        f"/api/todos/{todo['id']}/due-date", json={"due_date": None}
    )

    assert response.status_code == 200
    assert response.json() == {**todo, "due_date": None}
    assert client.get("/api/todos").json() == [response.json()]


def test_due_date_update_requires_field(client: TestClient) -> None:
    todo = client.post(
        "/api/todos", json={"title": "Keep date", "due_date": "2026-10-27"}
    ).json()

    response = client.patch(f"/api/todos/{todo['id']}/due-date", json={})

    assert response.status_code == 422
    assert client.get("/api/todos").json() == [todo]


@pytest.mark.parametrize("due_date", INVALID_DUE_DATES)
def test_due_date_update_rejects_invalid_date(
    client: TestClient, due_date: object
) -> None:
    todo = client.post(
        "/api/todos", json={"title": "Keep date", "due_date": "2026-10-27"}
    ).json()

    response = client.patch(
        f"/api/todos/{todo['id']}/due-date", json={"due_date": due_date}
    )

    assert response.status_code == 422
    assert client.get("/api/todos").json() == [todo]


@pytest.mark.parametrize("due_date", ["2026-10-27", None])
def test_due_date_update_unknown_todo(
    client: TestClient, due_date: str | None
) -> None:
    response = client.patch(
        "/api/todos/999/due-date", json={"due_date": due_date}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Todo 999 not found"}
    assert client.get("/api/todos").json() == []


@pytest.mark.parametrize("is_complete", [False, True])
def test_due_date_update_preserves_other_fields(
    client: TestClient, is_complete: bool
) -> None:
    todo = client.post("/api/todos", json={"title": "Keep fields"}).json()
    if is_complete:
        todo = client.patch(f"/api/todos/{todo['id']}/complete").json()
    other = client.post("/api/todos", json={"title": "Unchanged"}).json()

    response = client.patch(
        f"/api/todos/{todo['id']}/due-date", json={"due_date": "2026-10-27"}
    )

    assert response.status_code == 200
    assert response.json() == {**todo, "due_date": "2026-10-27"}
    assert client.get("/api/todos").json() == [response.json(), other]


def test_overdue_uses_server_date_dependency(client: TestClient) -> None:
    calls = []

    def fixed_today() -> date:
        calls.append(True)
        return date(2000, 1, 1)

    app.dependency_overrides[routes.get_today] = fixed_today
    yesterday = client.post(
        "/api/todos", json={"title": "Yesterday", "due_date": "1999-12-31"}
    ).json()
    client.post(
        "/api/todos", json={"title": "Today", "due_date": "2000-01-01"}
    )

    response = client.get("/api/todos?overdue=true")

    assert response.status_code == 200
    assert response.json() == [yesterday]
    assert calls == [True]


def test_overdue_includes_yesterday(client: TestClient) -> None:
    todo = client.post(
        "/api/todos", json={"title": "Yesterday", "due_date": "2026-10-27"}
    ).json()

    response = client.get("/api/todos?overdue=true")

    assert response.status_code == 200
    assert response.json() == [todo]


def test_overdue_excludes_today(client: TestClient) -> None:
    client.post(
        "/api/todos", json={"title": "Today", "due_date": "2026-10-28"}
    )

    response = client.get("/api/todos?overdue=true")

    assert response.status_code == 200
    assert response.json() == []


def test_overdue_excludes_future_dates(client: TestClient) -> None:
    client.post(
        "/api/todos", json={"title": "Tomorrow", "due_date": "2026-10-29"}
    )

    response = client.get("/api/todos?overdue=true")

    assert response.status_code == 200
    assert response.json() == []


def test_overdue_excludes_completed_todos(client: TestClient) -> None:
    todo = client.post(
        "/api/todos", json={"title": "Finished", "due_date": "2026-10-27"}
    ).json()
    client.patch(f"/api/todos/{todo['id']}/complete")

    response = client.get("/api/todos?overdue=true")

    assert response.status_code == 200
    assert response.json() == []


def test_overdue_excludes_undated_todos(client: TestClient) -> None:
    client.post("/api/todos", json={"title": "Undated"})

    response = client.get("/api/todos?overdue=true")

    assert response.status_code == 200
    assert response.json() == []


def test_unfiltered_list_includes_every_todo(
    client: TestClient, all_todos: list[dict[str, object]]
) -> None:
    response = client.get("/api/todos")

    assert response.status_code == 200
    assert response.json() == all_todos


def test_overdue_false_returns_all_todos(
    client: TestClient, all_todos: list[dict[str, object]]
) -> None:
    response = client.get("/api/todos?overdue=false")

    assert response.status_code == 200
    assert response.json() == all_todos


@pytest.mark.parametrize(
    ("due_date", "is_overdue"),
    [
        ("2026-10-28", False),
        ("2026-10-29", False),
        (None, False),
        ("2026-10-26", True),
    ],
)
def test_due_date_update_changes_overdue_membership(
    client: TestClient, due_date: str | None, is_overdue: bool
) -> None:
    todo = client.post("/api/todos", json={"title": "Reschedule"}).json()
    assert client.get("/api/todos?overdue=true").json() == []
    dated = client.patch(
        f"/api/todos/{todo['id']}/due-date", json={"due_date": "2026-10-27"}
    )
    assert dated.status_code == 200
    assert client.get("/api/todos?overdue=true").json() == [dated.json()]

    updated = client.patch(
        f"/api/todos/{todo['id']}/due-date", json={"due_date": due_date}
    )
    response = client.get("/api/todos?overdue=true")

    assert updated.status_code == 200
    assert response.status_code == 200
    assert response.json() == ([updated.json()] if is_overdue else [])


def test_completing_todo_removes_it_from_overdue(client: TestClient) -> None:
    todo = client.post(
        "/api/todos", json={"title": "Finish", "due_date": "2026-10-27"}
    ).json()
    assert client.get("/api/todos?overdue=true").json() == [todo]

    completed = client.patch(f"/api/todos/{todo['id']}/complete")
    response = client.get("/api/todos?overdue=true")

    assert completed.status_code == 200
    assert completed.json() == {**todo, "is_complete": True}
    assert response.status_code == 200
    assert response.json() == []
    assert client.get("/api/todos").json() == [completed.json()]


def test_deleting_todo_removes_it_from_overdue(client: TestClient) -> None:
    todo = client.post(
        "/api/todos", json={"title": "Remove", "due_date": "2026-10-27"}
    ).json()
    assert client.get("/api/todos?overdue=true").json() == [todo]

    deleted = client.delete(f"/api/todos/{todo['id']}")
    response = client.get("/api/todos?overdue=true")

    assert deleted.status_code == 204
    assert response.status_code == 200
    assert response.json() == []
    assert client.get("/api/todos").json() == []
