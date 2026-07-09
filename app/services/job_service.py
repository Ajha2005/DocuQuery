"""
The actual PDF processing pipeline, extracted so it can run
inside an RQ worker process (which has no access to FastAPI's
request-scoped get_db() dependency) as well as anywhere else
that needs it.

The route no longer does this work inline — it just enqueues
a call to process_document(document_id, file_path) and returns
immediately with status="pending".
"""

from app.db.session import SessionLocal
from app.models.document import Document
from app.models.chunk import Chunk
from app.services.pdf_service import extract_text_by_page, get_page_count, PDFExtractionError
from app.services.chunking_service import chunk_text
from app.services.embedding_service import embed_texts


def process_document(document_id: int, file_path: str) -> None:
    """
    Runs inside the RQ worker process. Opens its own DB session
    (SessionLocal directly, not Depends(get_db) — that dependency
    only exists within a FastAPI request lifecycle, which this isn't).
    """
    db = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return  # job orphaned, nothing to update

        document.status = "processing"
        db.commit()

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

    except PDFExtractionError as e:
        document.status = "failed"
        db.commit()
        raise  # let RQ record the job as failed, with the traceback in its log

    finally:
        db.close()

