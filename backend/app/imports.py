import hmac
import json
import os
from datetime import date, datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import ValidationError
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import import_schemas, models, schemas
from app.database import get_db
from app.registry import _normalize_identifier

router = APIRouter(prefix="/api/v1/registry/imports", tags=["registry imports"])

ENTITY_MODELS = {"underlying": models.UnderlyingAsset, "issuer": models.Issuer,
                 "issuer_product": models.IssuerProduct, "deployment": models.Deployment}
CREATE_SCHEMAS = {"underlying": schemas.UnderlyingCreate, "issuer": schemas.IssuerCreate,
                  "issuer_product": schemas.ProductCreate, "deployment": schemas.DeploymentCreate}


def require_import_admin(x_registry_admin_token: str | None = Header(default=None)):
    expected = os.getenv("REGISTRY_ADMIN_TOKEN")
    if not expected:
        raise HTTPException(status_code=503, detail="Registry import administration is disabled: REGISTRY_ADMIN_TOKEN is not configured.")
    if x_registry_admin_token is None or not hmac.compare_digest(x_registry_admin_token, expected):
        raise HTTPException(status_code=401, detail="A valid registry administrator token is required.")


def _now():
    return datetime.now(timezone.utc)


def _audit(db: Session, batch_id: str, actor: str, action: str, details: dict[str, Any], record_id: str | None = None):
    db.add(models.RegistryImportAuditEvent(batch_id=batch_id, import_record_id=record_id, actor=actor,
        action=action, details_json=json.dumps(details, sort_keys=True, separators=(",", ":"))))


def _candidate(db: Session, record: models.RegistryImportRecord, entity_type: str, entity_id: str,
               basis: str, confidence: float, evidence_ref: str | None = None):
    exists = db.scalar(select(models.RegistryImportCandidate).where(
        models.RegistryImportCandidate.import_record_id == record.id,
        models.RegistryImportCandidate.candidate_entity_type == entity_type,
        models.RegistryImportCandidate.candidate_entity_id == entity_id))
    pending = any(
        isinstance(item, models.RegistryImportCandidate)
        and item.import_record_id == record.id
        and item.candidate_entity_type == entity_type
        and item.candidate_entity_id == entity_id
        for item in db.new
    )
    if exists is None and not pending:
        db.add(models.RegistryImportCandidate(import_record_id=record.id, candidate_entity_type=entity_type,
            candidate_entity_id=entity_id, match_basis=basis, confidence=confidence, evidence_ref=evidence_ref))


def _normalise_deployment_payload(db: Session, payload: dict[str, Any]) -> str:
    network = db.get(models.Network, payload.get("network_id"))
    if network is None:
        raise HTTPException(status_code=422, detail="Deployment import requires an existing canonical network_id.")
    return _normalize_identifier(network.family, payload.get("native_identifier", ""))


def _discover_candidates(db: Session, batch: models.RegistryImportBatch,
                         record: models.RegistryImportRecord, payload: dict[str, Any]):
    aliases = db.scalars(select(models.ProviderAlias).where(
        models.ProviderAlias.provider == batch.source,
        models.ProviderAlias.namespace == record.source_namespace,
        models.ProviderAlias.external_id == record.external_id,
        or_(models.ProviderAlias.effective_from.is_(None), models.ProviderAlias.effective_from <= date.today()),
        or_(models.ProviderAlias.effective_to.is_(None), models.ProviderAlias.effective_to > date.today()))).all()
    for alias in aliases:
        if alias.entity_type == record.entity_type:
            _candidate(db, record, alias.entity_type, alias.entity_id,
                "exact_provider_alias_verified" if alias.is_verified else "exact_provider_alias_unverified",
                1.0 if alias.is_verified else 0.95, alias.evidence_ref)

    model = ENTITY_MODELS[record.entity_type]
    if record.entity_type in {"underlying", "issuer"}:
        key = payload.get("canonical_key")
        if key:
            for item in db.scalars(select(model).where(model.canonical_key == key)).all():
                _candidate(db, record, record.entity_type, item.id, "exact_canonical_key", 1.0)
        field = "display_name" if record.entity_type == "underlying" else "legal_name"
        name = payload.get(field)
        if isinstance(name, str) and name:
            for item in db.scalars(select(model).where(func.lower(getattr(model, field)) == name.lower())).all():
                _candidate(db, record, record.entity_type, item.id, "exact_name_not_unique_identity", 0.55)
    elif record.entity_type == "issuer_product":
        key = payload.get("canonical_key")
        if key:
            for item in db.scalars(select(model).where(model.canonical_key == key)).all():
                _candidate(db, record, record.entity_type, item.id, "exact_canonical_key", 1.0)
        issuer_id, native_id = payload.get("issuer_id"), payload.get("native_product_id")
        if issuer_id and native_id:
            for item in db.scalars(select(model).where(model.issuer_id == issuer_id,
                    model.native_product_id == native_id)).all():
                _candidate(db, record, record.entity_type, item.id, "exact_issuer_native_product_id", 1.0)
        symbol = payload.get("symbol")
        if isinstance(symbol, str) and symbol:
            for item in db.scalars(select(model).where(model.symbol == symbol)).all():
                _candidate(db, record, record.entity_type, item.id, "symbol_only_do_not_auto_link", 0.1)
    elif record.entity_type == "deployment":
        if payload.get("network_id") and payload.get("native_identifier"):
            try:
                normalized = _normalise_deployment_payload(db, payload)
            except (HTTPException, TypeError):
                normalized = None
            if normalized:
                for item in db.scalars(select(model).where(model.network_id == payload["network_id"],
                        model.normalized_identifier == normalized)).all():
                    _candidate(db, record, record.entity_type, item.id, "exact_network_identifier", 1.0)


def _record_read(db: Session, record: models.RegistryImportRecord):
    candidates = db.scalars(select(models.RegistryImportCandidate).where(
        models.RegistryImportCandidate.import_record_id == record.id).order_by(
        models.RegistryImportCandidate.confidence.desc(), models.RegistryImportCandidate.id)).all()
    return {"id": record.id, "batch_id": record.batch_id, "row_number": record.row_number,
        "entity_type": record.entity_type, "source_namespace": record.source_namespace,
        "external_id": record.external_id, "payload": json.loads(record.raw_payload_json),
        "status": record.status, "resolution_method": record.resolution_method,
        "resolved_entity_type": record.resolved_entity_type, "resolved_entity_id": record.resolved_entity_id,
        "evidence_ref": record.evidence_ref, "decision_note": record.decision_note,
        "reviewed_by": record.reviewed_by, "reviewed_at": record.reviewed_at.isoformat() if record.reviewed_at else None,
        "candidates": [{"id": c.id, "candidate_entity_type": c.candidate_entity_type,
            "candidate_entity_id": c.candidate_entity_id, "match_basis": c.match_basis,
            "confidence": c.confidence, "evidence_ref": c.evidence_ref} for c in candidates]}


def _batch_read(batch: models.RegistryImportBatch):
    return {"id": batch.id, "source": batch.source, "source_version": batch.source_version,
        "submitted_by": batch.submitted_by, "status": batch.status, "total_records": batch.total_records,
        "created_at": batch.created_at.isoformat(), "completed_at": batch.completed_at.isoformat() if batch.completed_at else None}


def _refresh_batch_status(db: Session, batch: models.RegistryImportBatch):
    db.flush()
    counts = dict(db.execute(select(models.RegistryImportRecord.status, func.count(models.RegistryImportRecord.id))
        .where(models.RegistryImportRecord.batch_id == batch.id).group_by(models.RegistryImportRecord.status)).all())
    if counts.get("needs_review", 0):
        batch.status, batch.completed_at = "reviewing", None
    elif counts.get("rejected", 0) or counts.get("duplicate", 0):
        batch.status, batch.completed_at = "completed_with_rejections", _now()
    else:
        batch.status, batch.completed_at = "completed", _now()


@router.post("", response_model=import_schemas.ImportBatchRead, status_code=201,
             dependencies=[Depends(require_import_admin)])
def stage_import(payload: import_schemas.ImportBatchCreate, db: Session = Depends(get_db)):
    batch = models.RegistryImportBatch(source=payload.source, source_version=payload.source_version,
        submitted_by=payload.submitted_by, status="staged", total_records=len(payload.records))
    db.add(batch)
    db.flush()
    seen: set[tuple[str, str, str]] = set()
    total_payload_bytes = 0
    for index, item in enumerate(payload.records, start=1):
        identity = (item.entity_type, item.source_namespace, item.external_id)
        try:
            raw_payload = json.dumps(item.payload, sort_keys=True, separators=(",", ":"))
        except (TypeError, ValueError) as exc:
            db.rollback()
            raise HTTPException(status_code=422, detail=f"Import row {index} payload must be JSON serializable.") from exc
        payload_size = len(raw_payload.encode("utf-8"))
        total_payload_bytes += payload_size
        if payload_size > 50_000 or total_payload_bytes > 5_000_000:
            db.rollback()
            raise HTTPException(status_code=413, detail="Import payload exceeds the 50 KB per-row or 5 MB per-batch safety limit.")
        record = models.RegistryImportRecord(batch_id=batch.id, row_number=index, entity_type=item.entity_type,
            source_namespace=item.source_namespace, external_id=item.external_id, raw_payload_json=raw_payload)
        db.add(record)
        db.flush()
        if identity in seen:
            record.status, record.resolution_method = "duplicate", "duplicate_in_batch"
            _audit(db, batch.id, payload.submitted_by, "duplicate_detected", {
                "entity_type": item.entity_type, "source_namespace": item.source_namespace,
                "external_id": item.external_id, "row_number": index}, record.id)
        else:
            seen.add(identity)
            _discover_candidates(db, batch, record, item.payload)
            db.flush()
            count = db.scalar(select(func.count(models.RegistryImportCandidate.id)).where(
                models.RegistryImportCandidate.import_record_id == record.id))
            _audit(db, batch.id, payload.submitted_by, "record_staged", {
                "entity_type": item.entity_type, "source_namespace": item.source_namespace,
                "external_id": item.external_id, "candidate_count": count}, record.id)
    _refresh_batch_status(db, batch)
    db.commit()
    db.refresh(batch)
    return _batch_read(batch)


@router.get("", response_model=list[import_schemas.ImportBatchRead], dependencies=[Depends(require_import_admin)])
def list_imports(db: Session = Depends(get_db), limit: int = Query(default=50, ge=1, le=200)):
    rows = db.scalars(select(models.RegistryImportBatch).order_by(
        models.RegistryImportBatch.created_at.desc(), models.RegistryImportBatch.id).limit(limit)).all()
    return [_batch_read(row) for row in rows]


@router.get("/queue", response_model=list[import_schemas.ImportRecordRead], dependencies=[Depends(require_import_admin)])
def review_queue(db: Session = Depends(get_db), batch_id: str | None = None,
                 limit: int = Query(default=100, ge=1, le=500)):
    query = select(models.RegistryImportRecord).where(models.RegistryImportRecord.status == "needs_review")
    if batch_id:
        query = query.where(models.RegistryImportRecord.batch_id == batch_id)
    rows = db.scalars(query.order_by(models.RegistryImportRecord.created_at,
        models.RegistryImportRecord.row_number).limit(limit)).all()
    return [_record_read(db, row) for row in rows]


@router.get("/{batch_id}", dependencies=[Depends(require_import_admin)])
def get_import(batch_id: str, db: Session = Depends(get_db)):
    batch = db.get(models.RegistryImportBatch, batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Import batch not found.")
    rows = db.scalars(select(models.RegistryImportRecord).where(
        models.RegistryImportRecord.batch_id == batch.id).order_by(models.RegistryImportRecord.row_number)).all()
    return {"batch": _batch_read(batch), "records": [_record_read(db, row) for row in rows]}


@router.get("/{batch_id}/audit", response_model=list[import_schemas.ImportAuditRead],
            dependencies=[Depends(require_import_admin)])
def get_import_audit(batch_id: str, db: Session = Depends(get_db)):
    if db.get(models.RegistryImportBatch, batch_id) is None:
        raise HTTPException(status_code=404, detail="Import batch not found.")
    events = db.scalars(select(models.RegistryImportAuditEvent).where(
        models.RegistryImportAuditEvent.batch_id == batch_id).order_by(
        models.RegistryImportAuditEvent.created_at, models.RegistryImportAuditEvent.id)).all()
    return [{"id": e.id, "batch_id": e.batch_id, "import_record_id": e.import_record_id,
        "actor": e.actor, "action": e.action, "details": json.loads(e.details_json),
        "created_at": e.created_at.isoformat()} for e in events]


@router.post("/records/{record_id}/decision", response_model=import_schemas.ImportRecordRead,
             dependencies=[Depends(require_import_admin)])
def decide_import_record(record_id: str, decision: import_schemas.ImportDecision,
                         db: Session = Depends(get_db)):
    record = db.scalar(select(models.RegistryImportRecord).where(
        models.RegistryImportRecord.id == record_id
    ).with_for_update())
    if record is None:
        raise HTTPException(status_code=404, detail="Import record not found.")
    if record.status != "needs_review":
        raise HTTPException(status_code=409, detail=f"Import record is already {record.status}.")
    batch = db.get(models.RegistryImportBatch, record.batch_id)
    payload = json.loads(record.raw_payload_json)

    if decision.action == "reject":
        if not decision.note:
            raise HTTPException(status_code=422, detail="A rejection note is required.")
        record.status, record.decision_note = "rejected", decision.note
        record.reviewed_by, record.reviewed_at = decision.reviewer, _now()
        _audit(db, batch.id, decision.reviewer, "record_rejected", {"reason": decision.note}, record.id)
    else:
        if not decision.evidence_ref:
            raise HTTPException(status_code=422, detail="Evidence reference is required before approving a mapping.")
        if decision.action == "link_existing":
            if not decision.target_entity_id:
                raise HTTPException(status_code=422, detail="target_entity_id is required to link an existing entity.")
            target = db.get(ENTITY_MODELS[record.entity_type], decision.target_entity_id)
            if target is None:
                raise HTTPException(status_code=404, detail="Target canonical entity not found.")
            target_id, method = target.id, "human_approved_existing_link"
        else:
            try:
                clean = CREATE_SCHEMAS[record.entity_type].model_validate(payload)
            except ValidationError as exc:
                raise HTTPException(status_code=422, detail={
                    "message": "Imported payload does not satisfy canonical entity requirements.",
                    "errors": exc.errors()}) from exc
            data = clean.model_dump()
            if record.entity_type == "issuer_product":
                if db.get(models.Issuer, data["issuer_id"]) is None:
                    raise HTTPException(status_code=404, detail="Imported issuer product references an unknown canonical issuer.")
                if db.get(models.UnderlyingAsset, data["underlying_id"]) is None:
                    raise HTTPException(status_code=404, detail="Imported issuer product references an unknown canonical underlying.")
            if record.entity_type == "deployment":
                if db.get(models.IssuerProduct, data["issuer_product_id"]) is None:
                    raise HTTPException(status_code=404, detail="Imported deployment references an unknown canonical issuer product.")
                data["normalized_identifier"] = _normalise_deployment_payload(db, data)
            target = ENTITY_MODELS[record.entity_type](**data)
            db.add(target)
            try:
                db.flush()
            except IntegrityError as exc:
                db.rollback()
                raise HTTPException(status_code=409, detail="Canonical identity already exists; refresh candidates and link the existing entity instead.") from exc
            target_id, method = target.id, "human_approved_new_entity"

        aliases = db.scalars(select(models.ProviderAlias).where(
            models.ProviderAlias.provider == batch.source,
            models.ProviderAlias.namespace == record.source_namespace,
            models.ProviderAlias.external_id == record.external_id,
            or_(models.ProviderAlias.effective_to.is_(None), models.ProviderAlias.effective_to > date.today()))).all()
        for alias in aliases:
            if alias.entity_type != record.entity_type or alias.entity_id != target_id:
                raise HTTPException(status_code=409, detail="Source identifier is already mapped to a different canonical entity; resolve the conflict explicitly.")
            alias.is_verified = True
            alias.evidence_ref = decision.evidence_ref
        if not aliases:
            db.add(models.ProviderAlias(provider=batch.source, namespace=record.source_namespace,
                external_id=record.external_id, effective_from=date.today(), entity_type=record.entity_type,
                entity_id=target_id, evidence_ref=decision.evidence_ref, is_verified=True))
        record.status, record.resolution_method = "approved", method
        record.resolved_entity_type, record.resolved_entity_id = record.entity_type, target_id
        record.evidence_ref, record.decision_note = decision.evidence_ref, decision.note
        record.reviewed_by, record.reviewed_at = decision.reviewer, _now()
        _audit(db, batch.id, decision.reviewer, "record_approved", {
            "action": decision.action, "entity_type": record.entity_type, "entity_id": target_id,
            "resolution_method": method, "evidence_ref": decision.evidence_ref}, record.id)

    _refresh_batch_status(db, batch)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Import decision conflicts with an existing source alias or canonical identity.") from exc
    db.refresh(record)
    return _record_read(db, record)
