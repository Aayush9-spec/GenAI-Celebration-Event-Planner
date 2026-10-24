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
# Startup: run Alembic migrations automatically
# ---------------------------------------------------------------------------
@app.on_event("startup")
def run_migrations():
    """Run alembic upgrade head on startup so Supabase schema is always current."""
    import subprocess, sys, os
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"[WARN] Alembic migration warning: {result.stderr[:500]}")
        else:
            print("[INFO] Alembic migrations applied.")
    except Exception as e:
        print(f"[WARN] Could not run migrations: {e}")
