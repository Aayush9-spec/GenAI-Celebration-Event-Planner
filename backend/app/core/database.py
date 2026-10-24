from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


def _make_engine_url(url: str) -> str:
    """Normalise postgres:// → postgresql+psycopg2:// for SQLAlchemy."""
    url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://") and "+psycopg2" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


def get_engine():
    return create_engine(_make_engine_url(settings.DATABASE_URL))


# Lazy singletons — constructed on first use, not at import time
_engine = None
_SessionLocal = None

Base = declarative_base()


def get_db():
    global _engine, _SessionLocal
    if _engine is None:
        _engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Keep a module-level reference for Alembic env.py
def get_session_factory():
    global _engine, _SessionLocal
    if _engine is None:
        _engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _SessionLocal
