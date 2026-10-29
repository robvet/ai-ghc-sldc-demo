from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app import service
from app.models import Todo, TodoCreate, TodoDueDateUpdate

router = APIRouter(prefix="/api")


def get_today() -> date:
    return date.today()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/todos")
def list_todos(
    today: Annotated[date, Depends(get_today)], overdue: bool = False
) -> list[Todo]:
    if overdue:
        return service.list_overdue_todos(today=today)
    return service.list_todos()


@router.post("/todos", status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate) -> Todo:
    return service.create_todo(todo)


@router.patch("/todos/{id}/complete")
def complete_todo(id: int) -> Todo:
    try:
        return service.complete_todo(id)
    except service.TodoNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.patch("/todos/{id}/due-date")
def update_due_date(id: int, update: TodoDueDateUpdate) -> Todo:
    try:
        return service.update_due_date(id, update)
    except service.TodoNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.delete("/todos/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(id: int) -> Response:
    try:
        service.delete_todo(id)
    except service.TodoNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
