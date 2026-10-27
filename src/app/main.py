from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import router

app = FastAPI()
app.include_router(router)
app.mount("/", StaticFiles(directory=Path(__file__).resolve().parent.parent / "ux", html=True))
