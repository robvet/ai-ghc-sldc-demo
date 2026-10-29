# To-Do Demo App
To-Do Demo App: a simple FastAPI live demo with an in-memory to-do list and static UI.
Add, list, complete, and delete to-dos, with optional calendar due dates.
Data resets when the process restarts.
Not for: databases, auth, multiple services, or production.
Setup: python3.11 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
Run: python -m uvicorn app.main:app --app-dir src --host 127.0.0.1 --port 8010
Open: http://127.0.0.1:8010
Test: pytest

Dates use `YYYY-MM-DD`, not timestamps; undated items have `due_date: null`.
All is the default view and includes every item. Overdue includes only incomplete
items due strictly before the server-local date, excluding today, future dates,
completed items, and undated items. Both views preserve insertion order.
The browser keeps dates as calendar strings without UTC conversion.

Choose a date when adding a to-do, or edit an item's date and select Save.
Clear the date input and select Save to remove its due date. Completing an item
preserves its date. The selected view refreshes after each successful change;
items leave Overdue when completed, deleted, cleared, or rescheduled to today
or later. Select a view to refresh it; there is no automatic midnight refresh.

| API | Behavior |
| --- | --- |
| `GET /api/health` | Health check |
| `GET /api/todos` | All items; `?overdue=false` also returns all |
| `GET /api/todos?overdue=true` | Server-filtered overdue items |
| `POST /api/todos` | Create with `{"title":"Demo","due_date":"2026-10-27"}`; date may be omitted or null |
| `PATCH /api/todos/{id}/due-date` | Set/change with `{"due_date":"2026-10-29"}`, or clear with `{"due_date":null}` |
| `PATCH /api/todos/{id}/complete` | Complete an item |
| `DELETE /api/todos/{id}` | Delete an item |

All to-do responses include `due_date` as a date string or null. Creation returns
201, deletion returns 204, and unknown to-do IDs with valid requests return 404.
Date updates require the `due_date` field. Missing update dates, impossible dates,
timestamps, numeric epochs, and wrong types return 422 without changing data.

Routes call the service layer, which uses the in-memory repository.
`config/production/settings.json` contains placeholders only; the app does not read it.
