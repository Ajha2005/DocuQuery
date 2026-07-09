import os
import shutil
import uuid

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from redis import Redis
from rq import Queue

from app.api.deps import get_db
from app.core.config import settings
from app.core.exceptions import UnsupportedFileType, DocumentNotFound
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentListResponse
from app.services.job_service import process_document

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

redis_conn = Redis.from_url(settings.REDIS_URL)
job_queue = Queue("default", connection=redis_conn)


@router.post("", response_model=DocumentResponse)
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".pdf"):
        raise UnsupportedFileType(file.filename)

    unique_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create the Document row immediately with status="pending".
    # Actual processing happens asynchronously in the worker process —
    # this endpoint returns instantly regardless of file size.
    document = Document(
        filename=file.filename,
        status="pending",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    job_queue.enqueue(process_document, document.id, file_path)

    return document


@router.get("", response_model=DocumentListResponse)
def list_documents(db: Session = Depends(get_db)):
    documents = db.query(Document).order_by(Document.upload_time.desc()).all()
    return DocumentListResponse(documents=documents)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise DocumentNotFound(document_id)
    return document
