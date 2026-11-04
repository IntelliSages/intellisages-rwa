from fastapi import APIRouter, Depends
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.imports import require_import_admin

router = APIRouter(
    prefix="/api/v1/registry/diagnostics",
    tags=["operations"],
    dependencies=[Depends(require_import_admin)],
)


@router.get("/database")
def database_diagnostic(db: Session = Depends(get_db)):
    """Read-only DB identity and persistence diagnostic (registry-admin protected)."""
    connection = db.connection()
    dialect = connection.dialect.name

    if dialect == "postgresql":
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
                    (SELECT version_num FROM alembic_version LIMIT 1) AS alembic_revision
                """
            )
        ).mappings().one()
        identity = dict(target)
    else:
        identity = {
            "database_name": "sqlite",
            "database_user": None,
            "active_schema": None,
            "search_path": None,
            "server_address": None,
            "server_port": None,
            "alembic_revision": None,
        }

    counts = {
        "registry_import_batches": db.scalar(
            select(func.count()).select_from(models.RegistryImportBatch)
        ),
        "registry_import_records": db.scalar(
            select(func.count()).select_from(models.RegistryImportRecord)
        ),
        "registry_import_candidates": db.scalar(
            select(func.count()).select_from(models.RegistryImportCandidate)
        ),
        "registry_import_audit_events": db.scalar(
            select(func.count()).select_from(models.RegistryImportAuditEvent)
        ),
        "provider_ingestion_runs": db.scalar(
            select(func.count()).select_from(models.ProviderIngestionRun)
        ),
        "provider_refresh_runs": db.scalar(
            select(func.count()).select_from(models.ProviderRefreshRun)
        ),
        "provider_raw_responses": db.scalar(
            select(func.count()).select_from(models.ProviderRawResponse)
        ),
        "coingecko_rwa_market_observations": db.scalar(
            select(func.count()).select_from(models.CoinGeckoRwaMarketObservation)
        ),
    }

    return {
        "status": "ok",
        "database": identity,
        "table_counts": counts,
        "interpretation": (
            "All counts are read-only and reflect this API process's configured database. "
            "A zero registry count alongside nonzero market observations means registry "
            "batches are not present in this database."
        ),
    }
