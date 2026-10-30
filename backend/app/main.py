import logging

from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.registry import router as registry_router
from app.catalogue import router as catalogue_router
from app.imports import router as imports_router
from app.provider_runs import router as provider_runs_router
from app.coingecko_market_data_api import router as coingecko_market_data_router
from app.database import engine

logger = logging.getLogger(__name__)

app = FastAPI(
    title="RWAs Intelligence API",
    version="0.1.0",
    description="Canonical identity registry and read-only market intelligence services.",
)
app.include_router(registry_router)
app.include_router(catalogue_router)
app.include_router(imports_router)
app.include_router(provider_runs_router)
app.include_router(coingecko_market_data_router)


@app.on_event("startup")
def log_database_target():
    """Log the API process database target without exposing connection credentials."""
    if engine.dialect.name != "postgresql":
        logger.info("API database target: dialect=%s", engine.dialect.name)
        return

    try:
        with engine.connect() as connection:
            target = connection.execute(
                text(
                    """
                    SELECT
                        current_database() AS database_name,
                        current_user AS database_user,
                        current_schema() AS active_schema,
                        current_setting('search_path') AS search_path,
                        inet_server_addr()::text AS server_address,
                        inet_server_port() AS server_port,
                        pg_catalog.to_regclass('alembic_version')::text AS version_table,
                        pg_catalog.to_regclass('issuer_products')::text AS issuer_products
                    """
                )
            ).mappings().one()
            logger.info(
                "API PostgreSQL target: database=%s user=%s schema=%s "
                "search_path=%s server=%s port=%s alembic_version=%s "
                "issuer_products=%s",
                target["database_name"],
                target["database_user"],
                target["active_schema"],
                target["search_path"],
                target["server_address"],
                target["server_port"],
                target["version_table"],
                target["issuer_products"],
            )
    except SQLAlchemyError:
        logger.exception("Could not inspect the API PostgreSQL database target.")


@app.get("/healthz", tags=["operations"])
def healthcheck():
    """Readiness check: the API process and its persistent database must both respond."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database is unavailable.") from exc
    return {"status": "ok", "service": "rwa-intelligence-api", "database": "connected"}
