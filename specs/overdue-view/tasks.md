# Implementation tasks

Execute these three tasks in order. Extend existing files; do not rewrite the app. Test names below are planned additions unless already present. Run commands with the existing `.venv`; no new dependencies or server startup.

## 1. Add due-date persistence and deterministic service logic

**Files to change:** `src/app/models.py`, `src/app/storage.py`, `src/app/service.py`, `tests/test_service.py`.

**Acceptance criteria**

- `Todo` and `TodoCreate` have optional `due_date`, defaulting to `None`; an update model requires a nullable date field.
- Creation persists dates; date updates set, change, or clear them without altering other fields.
- Existing storage get/update methods are reused; storage contains no overdue business logic.
- Overdue service logic takes explicit `today: date`, includes only incomplete dated items before that date, and preserves order.
- Service functions never read the clock or import HTTP/FastAPI behavior.
- Missing IDs raise the existing domain exception. Existing creation, listing, completion, and deletion still work.

**Pytest tests proving completion**

In `tests/test_service.py`, add one test per behavior:

- `test_create_todo_without_due_date`
- `test_create_todo_with_due_date`
- `test_set_due_date`
- `test_change_due_date`
- `test_clear_due_date`
- `test_update_due_date_preserves_other_fields`
- `test_update_due_date_unknown_todo`
- `test_overdue_includes_yesterday`
- `test_overdue_excludes_today`
- `test_overdue_excludes_future_dates`
- `test_overdue_excludes_completed_todos`
- `test_overdue_excludes_undated_todos`
- `test_overdue_preserves_insertion_order`
- `test_overdue_uses_supplied_today`
- `test_all_view_includes_every_todo`
- `test_complete_todo_preserves_due_date`

Update existing exact model assertions and retain all existing service tests. Run `.venv/bin/python -m pytest tests/test_service.py`.

## 2. Expose date updates and overdue filtering through the API

**Files to change:** `src/app/routes.py`, `tests/test_routes.py`.

**Acceptance criteria**

- POST accepts optional due dates; all to-do responses include the nullable field.
- GET supports `overdue=true`; omitted or false filtering returns all items.
- PATCH `/api/todos/{id}/due-date` accepts a date or explicit null and returns the persisted item.
- Missing/invalid date fields produce 422 without mutations; unknown IDs with valid bodies produce 404.
- An overridable route-level clock supplies the server-local date once per overdue request to service. Routes never access storage.
- Health endpoint and its test remain unchanged; `main.py` stays wiring only.

**Pytest tests proving completion**

In `tests/test_routes.py`, add:

- `test_create_todo_without_due_date`
- `test_create_todo_with_due_date`
- `test_create_todo_rejects_invalid_due_date`
- `test_set_due_date`
- `test_change_due_date`
- `test_clear_due_date`
- `test_due_date_update_requires_field`
- `test_due_date_update_rejects_invalid_date`
- `test_due_date_update_unknown_todo`
- `test_due_date_update_preserves_other_fields`
- `test_overdue_uses_server_date_dependency`
- `test_overdue_includes_yesterday`
- `test_overdue_excludes_today`
- `test_overdue_excludes_future_dates`
- `test_overdue_excludes_completed_todos`
- `test_overdue_excludes_undated_todos`
- `test_unfiltered_list_includes_every_todo`
- `test_overdue_false_returns_all_todos`
- `test_due_date_update_changes_overdue_membership`
- `test_completing_todo_removes_it_from_overdue`
- `test_deleting_todo_removes_it_from_overdue`

Parameterize invalid input tests for impossible dates, timestamps, numeric epochs, and wrong types. Override the route date dependency with a fixed date and restore overrides after each test. Update existing exact response assertions.

Run `.venv/bin/python -m pytest tests/test_service.py tests/test_routes.py tests/test_health.py`, retaining the unchanged health test.

## 3. Add date controls and All/Overdue views; document and verify

**Files to change:** `src/ux/index.html`, `src/ux/app.js`, `tests/test_routes.py`, `README.md`.

**Acceptance criteria**

- Add optional creation date input, editable per-item dates, explicit Save actions, and All/Overdue controls.
- Default to All, preserve selected view after mutations, and use server-filtered results rather than browser date logic.
- Clearing sends null; date strings are not shifted through UTC conversion.
- Completed, deleted, cleared, or rescheduled items disappear from Overdue as appropriate.
- Show view-specific empty messages and visible errors; pending controls recover after failures.
- Retain the current theme, safe text rendering, and Complete/Delete behavior.
- Document date rules and API, keeping Setup/Run/Open/Test.
- All tests pass using the existing `.venv`; no server is started and no protected files or dependencies change.

**Pytest tests proving completion**

- Extend `tests/test_routes.py::test_static_ui` to assert the served page includes the creation date input and accessible All/Overdue controls.
- Retain `tests/test_routes.py::test_static_javascript` and extend it to confirm the served script is the updated asset.
- Re-run the API membership tests from task 2 to prove the server behavior supporting view changes.
- Run `.venv/bin/python -m pytest` for the full suite, including unchanged `tests/test_health.py::test_health`.

Static pytest assertions alone do not prove interactive browser behavior. Additionally exercise creation with/without dates, edit/clear, view switching, selected-view refresh, empty states, and request failures with existing browser tooling or a dependency-free JavaScript harness. Check JavaScript syntax with existing Node if available. Do not add a testing library or start a server.
