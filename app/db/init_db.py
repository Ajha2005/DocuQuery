from sqlalchemy import text

from app.db.base import Base
from app.db.session import engine


def init_db() -> None:
    # Enable pgvector extension (must exist before creating vector columns)
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    # Create all tables defined in models
    Base.metadata.create_all(bind=engine)
