from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="GenAI-powered Celebration & Event Planner API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS — reads from ALLOWED_ORIGINS env var (comma-separated or "*")
# ---------------------------------------------------------------------------
_raw_origins = settings.ALLOWED_ORIGINS
allowed_origins: list[str] = (
    ["*"] if _raw_origins.strip() == "*" else [o.strip() for o in _raw_origins.split(",")]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Router registration
# ---------------------------------------------------------------------------
from app.api.routes import auth    # noqa: E402
from app.api.routes import events  # noqa: E402
from app.api.routes import plans   # noqa: E402
from app.api.routes import chat    # noqa: E402
from app.api.routes import export  # noqa: E402

app.include_router(auth.router)
app.include_router(events.router)
app.include_router(plans.router)
app.include_router(chat.router)
app.include_router(export.router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "version": "1.0.0", "service": settings.PROJECT_NAME}


# ---------------------------------------------------------------------------
# Startup: create all tables via SQLAlchemy (works on any platform/host)
# ---------------------------------------------------------------------------
@app.on_event("startup")
def create_tables():
    """Create all DB tables on startup if they don't already exist."""
    try:
        from app.core.database import get_engine, Base
        import app.models  # noqa: F401 — registers all models on Base.metadata
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
        print("[INFO] Database tables created/verified OK.")
    except Exception as e:
        print(f"[ERROR] Could not create tables: {e}")
