from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.exceptions import DocumentNotFound
from app.models.document import Document
from app.schemas.query import QueryRequest, QueryResponse
from app.services.rag_service import answer_question

router = APIRouter(prefix="/documents", tags=["query"])


@router.post("/{document_id}/query", response_model=QueryResponse)
def query_document(document_id: int, request: QueryRequest, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise DocumentNotFound(document_id)

    result = answer_question(db, document_id=document_id, question=request.question)
    return QueryResponse(**result)
