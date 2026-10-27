# Python FastAPI – Minimal Starter
Use for: small demo or prototype apps, single process, in-memory data, simple static UI.
Not for: databases, auth, multiple services, or production.
Setup: python3.11 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
Run: python -m uvicorn app.main:app --app-dir src --host 127.0.0.1 --port 8010
Open: http://127.0.0.1:8010
Test: pytest
