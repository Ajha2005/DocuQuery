from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str


class SourceCitation(BaseModel):
    chunk_id: int
    page_number: int | None
    content_snippet: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceCitation]
