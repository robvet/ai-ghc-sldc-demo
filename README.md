# To-Do Demo App
To-Do Demo App: a simple FastAPI live demo with an in-memory to-do list and static UI.
Add, list, complete, and delete to-dos. Data resets when the process restarts.
Not for: databases, auth, multiple services, or production.
Setup: python3.11 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
Run: python -m uvicorn app.main:app --app-dir src --host 127.0.0.1 --port 8010
Open: http://127.0.0.1:8010
Test: pytest

API: `GET /api/health`, `GET /api/todos`, `POST /api/todos`,
`PATCH /api/todos/{id}/complete`, and `DELETE /api/todos/{id}`.
Creation returns 201, deletion returns 204, and unknown to-do IDs return 404.

Routes call the service layer, which uses the in-memory repository.
`config/production/settings.json` contains placeholders only; the app does not read it.
