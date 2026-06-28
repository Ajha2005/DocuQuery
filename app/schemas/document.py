from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    """What we send back to the client after upload or when listing documents."""
    id: int
    filename: str
    upload_time: datetime
    page_count: int | None
    status: str

    class Config:
        from_attributes = True  # allows creating this from a SQLAlchemy model directly


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
