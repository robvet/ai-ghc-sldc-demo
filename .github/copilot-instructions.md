# To-Do Demo App: Copilot Instructions

## Overview
Minimal to-do app for demos. Single FastAPI process serves a JSON API and a static UI.
In-memory storage only. No database, no auth.

## Stack
- Python 3.11, FastAPI, Pydantic
- pytest + FastAPI TestClient (httpx)
- Vanilla HTML/JS UI, no frameworks
- Dependencies are limited to requirements.txt. Do not add libraries without asking.

## Structure
- src/app/main.py: wiring only. Include the router first, mount src/ux/ last. No endpoints here.
- src/app/routes.py: HTTP endpoints under /api. Call service only, never storage.
- src/app/service.py: business logic. No HTTP or FastAPI code.
- src/app/storage.py: in-memory data access only.
- src/app/models.py: Pydantic models shared across layers.
- src/ux/: index.html and app.js, served at /.
- tests/: pytest tests. conftest.py clears storage before each test.

## Conventions
- Keep functions small and readable; this code is shown live to an audience.
- Use type hints on all functions.
- Return 404 for unknown ids.
- One test per behavior; test names describe the behavior.

## Commands
- Activate: source .venv/bin/activate
- Run: python -m uvicorn app.main:app --app-dir src --host 127.0.0.1 --port 8010 --reload
- Test: pytest