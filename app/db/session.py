from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


def _normalize_db_url(url: str) -> str:
    """
    Some providers (e.g. Railway) hand out connection strings starting
    with 'postgres://', which SQLAlchemy 2.x no longer recognizes as
    a dialect. SQLAlchemy requires the explicit 'postgresql://' scheme.
    This normalizes either form to what SQLAlchemy expects.
    """
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


engine = create_engine(_normalize_db_url(settings.DATABASE_URL))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
