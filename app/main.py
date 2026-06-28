from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.init_db import init_db
from app.models import Document, Chunk  # noqa: F401
from app.api.routes import documents, query
from app.api.error_handlers import register_error_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="DocuQuery", version="0.1.0", lifespan=lifespan)

app.include_router(documents.router)
app.include_router(query.router)
register_error_handlers(app)


@app.get("/health")
def health_check():
    return {"status": "ok"}
