from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base

EMBEDDING_DIMENSIONS = 384  # all-MiniLM-L6-v2 output size


class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    chunk_index = Column(Integer, nullable=False)
    token_count = Column(Integer, nullable=True)
    embedding = Column(Vector(EMBEDDING_DIMENSIONS), nullable=True)

    document = relationship("Document", back_populates="chunks")
