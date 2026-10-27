import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


def test_list_todos_starts_empty(client):
    response = client.get("/api/todos")

    assert response.status_code == 200
    assert response.json() == []


def test_create_todo(client):
    response = client.post("/api/todos", json={"title": "Demo task"})

    assert response.status_code == 201
    assert response.json() == {
        "id": 1, "title": "Demo task", "is_complete": False
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


def test_static_ui(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "To-Do Demo App" in response.text
    assert 'id="todo-form"' in response.text
    assert 'id="todo-list"' in response.text


def test_static_javascript(client):
    response = client.get("/app.js")

    assert response.status_code == 200
    assert "/api/todos" in response.text
