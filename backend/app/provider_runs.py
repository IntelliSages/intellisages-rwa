import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import import_schemas, models
from app.database import get_db
from app.imports import require_import_admin

router = APIRouter(prefix="/api/v1/registry/provider-runs", tags=["provider ingestion runs"])


def _read(run: models.ProviderIngestionRun):
    return {
        "id": run.id, "provider": run.provider, "dataset": run.dataset,
        "source_version": run.source_version, "started_by": run.started_by,
        "status": run.status, "manifest_sha256": run.manifest_sha256,
        "coverage": json.loads(run.coverage_json),
        "staged_batch_ids": json.loads(run.staged_batch_ids_json),
        "error_summary": run.error_summary,
        "created_at": run.created_at.isoformat(), "updated_at": run.updated_at.isoformat(),
        "completed_at": run.completed_at.isoformat() if run.completed_at else None,
    }


@router.post("", response_model=import_schemas.ProviderRunRead, status_code=201,
             dependencies=[Depends(require_import_admin)])
def create_provider_run(payload: import_schemas.ProviderRunCreate, db: Session = Depends(get_db)):
    run = models.ProviderIngestionRun(
        provider=payload.provider, dataset=payload.dataset, source_version=payload.source_version,
        started_by=payload.started_by, status="snapshot_ready", manifest_sha256=payload.manifest_sha256,
        coverage_json=json.dumps(payload.coverage, sort_keys=True, separators=(",", ":")),
        staged_batch_ids_json="[]",
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return _read(run)


@router.patch("/{run_id}", response_model=import_schemas.ProviderRunRead,
              dependencies=[Depends(require_import_admin)])
def update_provider_run(run_id: str, payload: import_schemas.ProviderRunUpdate,
                        db: Session = Depends(get_db)):
    run = db.scalar(select(models.ProviderIngestionRun).where(
        models.ProviderIngestionRun.id == run_id
    ).with_for_update())
    if run is None:
        raise HTTPException(status_code=404, detail="Provider ingestion run not found.")
    if run.status == "completed":
        raise HTTPException(status_code=409, detail="Completed provider ingestion runs are immutable.")
    data = payload.model_dump(exclude_unset=True)
    if "coverage" in data and data["coverage"] is not None:
        run.coverage_json = json.dumps(data.pop("coverage"), sort_keys=True, separators=(",", ":"))
    if "staged_batch_ids" in data and data["staged_batch_ids"] is not None:
        existing = json.loads(run.staged_batch_ids_json)
        run.staged_batch_ids_json = json.dumps(list(dict.fromkeys(existing + data.pop("staged_batch_ids"))))
    for field, value in data.items():
        setattr(run, field, value)
    run.updated_at = datetime.now(timezone.utc)
    if run.status == "completed":
        run.completed_at = run.updated_at
    db.commit()
    db.refresh(run)
    return _read(run)


@router.get("", response_model=list[import_schemas.ProviderRunRead],
            dependencies=[Depends(require_import_admin)])
def list_provider_runs(db: Session = Depends(get_db)):
    runs = db.scalars(select(models.ProviderIngestionRun).order_by(
        models.ProviderIngestionRun.created_at.desc()).limit(100)).all()
    return [_read(run) for run in runs]


@router.get("/{run_id}", response_model=import_schemas.ProviderRunRead,
            dependencies=[Depends(require_import_admin)])
def get_provider_run(run_id: str, db: Session = Depends(get_db)):
    run = db.get(models.ProviderIngestionRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Provider ingestion run not found.")
    return _read(run)
