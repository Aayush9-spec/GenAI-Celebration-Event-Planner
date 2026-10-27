from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


def _make_engine_url(url: str) -> str:
    """Normalise postgres:// → postgresql+psycopg2:// for SQLAlchemy."""
    url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://") and "+psycopg2" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


def get_engine():
    url = _make_engine_url(settings.DATABASE_URL)
    connect_args = {}
    # Supabase port 6543 = pgbouncer pooler — requires SSL + no prepared statements
    if "supabase.co" in url or "supabase.com" in url:
        connect_args = {
            "sslmode": "require",
            "options": "-c statement_timeout=30000",
        }
    return create_engine(
        url,
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_recycle=300,
        # Required for pgbouncer (port 6543) — disables prepared statements
        execution_options={"no_parameters": False},
    )


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


# Keep a module-level reference for Alembic env.py and startup
def get_session_factory():
    global _engine, _SessionLocal
    if _engine is None:
        _engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    return _SessionLocal
