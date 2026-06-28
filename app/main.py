from fastapi import FastAPI

from app.db.init_db import init_db
from app.models import Document, Chunk  # noqa: F401  (ensures models are registered with Base)

app = FastAPI(title="DocuQuery", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health_check():
    return {"status": "ok"}
