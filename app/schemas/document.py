from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    """What we send back to the client after upload or when listing documents."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    upload_time: datetime
    page_count: int | None
    status: str


class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
