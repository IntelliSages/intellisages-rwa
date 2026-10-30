from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.registry import router as registry_router
from app.catalogue import router as catalogue_router
from app.imports import router as imports_router
from app.provider_runs import router as provider_runs_router
from app.database import engine

app = FastAPI(
    title="RWAs Intelligence API",
    version="0.1.0",
    description="Canonical identity registry and read-only market intelligence services.",
)
app.include_router(registry_router)
app.include_router(catalogue_router)
app.include_router(imports_router)
app.include_router(provider_runs_router)


@app.get("/healthz", tags=["operations"])
def healthcheck():
    """Readiness check: the API process and its persistent database must both respond."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    return {"status": "ok", "service": "rwa-intelligence-api", "database": "connected"}
