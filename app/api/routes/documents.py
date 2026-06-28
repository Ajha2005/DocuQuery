import os
import shutil
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.exceptions import UnsupportedFileType, DocumentNotFound
from app.models.document import Document
from app.models.chunk import Chunk
from app.schemas.document import DocumentResponse, DocumentListResponse
from app.services.pdf_service import extract_text_by_page, get_page_count, PDFExtractionError
from app.services.chunking_service import chunk_text
from app.services.embedding_service import embed_texts

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = "uploaded_pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("", response_model=DocumentResponse)
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(".pdf"):
        raise UnsupportedFileType(file.filename)

    # Save the file to disk with a unique name to avoid collisions
    unique_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create the Document row immediately with status="processing"
    # so the user gets a response fast and we have an id to attach chunks to.
    document = Document(
        filename=file.filename,
        status="processing",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        page_count = get_page_count(file_path)
        pages = extract_text_by_page(file_path)
        raw_chunks = chunk_text(pages)

        if raw_chunks:
            texts = [c["content"] for c in raw_chunks]
            vectors = embed_texts(texts)

            chunk_rows = [
                Chunk(
                    document_id=document.id,
                    content=raw_chunk["content"],
                    page_number=raw_chunk["page_number"],
                    chunk_index=raw_chunk["chunk_index"],
                    token_count=len(raw_chunk["content"].split()),
                    embedding=vector,
                )
                for raw_chunk, vector in zip(raw_chunks, vectors)
            ]
            db.add_all(chunk_rows)

        document.page_count = page_count
        document.status = "ready"
        db.commit()
        db.refresh(document)

    except PDFExtractionError as e:
        document.status = "failed"
        db.commit()
        raise HTTPException(status_code=400, detail=str(e))

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
