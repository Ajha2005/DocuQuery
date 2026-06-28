from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    upload_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    page_count = Column(Integer, nullable=True)
    status = Column(String, default="processing", nullable=False)

    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")
