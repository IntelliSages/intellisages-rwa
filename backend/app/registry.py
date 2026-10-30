import re
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/v1/registry", tags=["identity registry"])

ENTITY_MODELS = {
    "underlying": models.UnderlyingAsset,
    "issuer": models.Issuer,
    "issuer_product": models.IssuerProduct,
    "deployment": models.Deployment,
    "venue": models.Venue,
    "perpetual_contract": models.PerpetualContract,
}

def _create(db: Session, model: type, payload: Any):
    record = model(**payload.model_dump())
    db.add(record)
    try:
        db.commit()
        db.refresh(record)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Identity conflicts with an existing registry record.") from exc
    return record

def _list(db: Session, model: type):
    return db.scalars(select(model).order_by(model.id)).all()

def _require(db: Session, model: type, entity_id: str, label: str):
    record = db.get(model, entity_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"{label} not found.")
    return record

def _normalize_identifier(family: str, value: str) -> str:
    if family == "evm":
        if not re.fullmatch(r"0x[a-fA-F0-9]{40}", value):
            raise HTTPException(status_code=422, detail="EVM deployments require a 20-byte hexadecimal address.")
        return value.lower()
    return value

@router.post("/underlyings", response_model=schemas.UnderlyingRead, status_code=201)
def create_underlying(payload: schemas.UnderlyingCreate, db: Session = Depends(get_db)):
    return _create(db, models.UnderlyingAsset, payload)
@router.get("/underlyings", response_model=list[schemas.UnderlyingRead])
def list_underlyings(db: Session = Depends(get_db)):
    return _list(db, models.UnderlyingAsset)

@router.post("/issuers", response_model=schemas.IssuerRead, status_code=201)
def create_issuer(payload: schemas.IssuerCreate, db: Session = Depends(get_db)):
    return _create(db, models.Issuer, payload)
@router.get("/issuers", response_model=list[schemas.IssuerRead])
def list_issuers(db: Session = Depends(get_db)):
    return _list(db, models.Issuer)

@router.post("/products", response_model=schemas.ProductRead, status_code=201)
def create_product(payload: schemas.ProductCreate, db: Session = Depends(get_db)):
    _require(db, models.Issuer, payload.issuer_id, "Issuer")
    _require(db, models.UnderlyingAsset, payload.underlying_id, "Underlying")
    return _create(db, models.IssuerProduct, payload)
@router.get("/products", response_model=list[schemas.ProductRead])
def list_products(db: Session = Depends(get_db)):
    return _list(db, models.IssuerProduct)

@router.post("/networks", response_model=schemas.NetworkRead, status_code=201)
def create_network(payload: schemas.NetworkCreate, db: Session = Depends(get_db)):
    return _create(db, models.Network, payload)
@router.get("/networks", response_model=list[schemas.NetworkRead])
def list_networks(db: Session = Depends(get_db)):
    return _list(db, models.Network)

@router.post("/deployments", response_model=schemas.DeploymentRead, status_code=201)
def create_deployment(payload: schemas.DeploymentCreate, db: Session = Depends(get_db)):
    _require(db, models.IssuerProduct, payload.issuer_product_id, "Issuer product")
    network = _require(db, models.Network, payload.network_id, "Network")
    normalized = _normalize_identifier(network.family, payload.native_identifier)
    record = models.Deployment(**payload.model_dump(), normalized_identifier=normalized)
    db.add(record)
    try:
        db.commit()
        db.refresh(record)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Deployment already exists for this network identifier.") from exc
    return record
@router.get("/deployments", response_model=list[schemas.DeploymentRead])
def list_deployments(db: Session = Depends(get_db)):
    return _list(db, models.Deployment)

@router.post("/venues", response_model=schemas.VenueRead, status_code=201)
def create_venue(payload: schemas.VenueCreate, db: Session = Depends(get_db)):
    return _create(db, models.Venue, payload)
@router.get("/venues", response_model=list[schemas.VenueRead])
def list_venues(db: Session = Depends(get_db)):
    return _list(db, models.Venue)

@router.post("/perpetual-contracts", response_model=schemas.PerpetualRead, status_code=201)
def create_perpetual(payload: schemas.PerpetualCreate, db: Session = Depends(get_db)):
    _require(db, models.Venue, payload.venue_id, "Venue")
    if payload.underlying_id:
        _require(db, models.UnderlyingAsset, payload.underlying_id, "Underlying")
    if payload.issuer_product_id:
        _require(db, models.IssuerProduct, payload.issuer_product_id, "Issuer product")
    return _create(db, models.PerpetualContract, payload)
@router.get("/perpetual-contracts", response_model=list[schemas.PerpetualRead])
def list_perpetuals(db: Session = Depends(get_db)):
    return _list(db, models.PerpetualContract)

@router.post("/aliases", response_model=schemas.AliasRead, status_code=201)
def create_alias(payload: schemas.AliasCreate, db: Session = Depends(get_db)):
    _require(db, ENTITY_MODELS[payload.entity_type], payload.entity_id, payload.entity_type)
    return _create(db, models.ProviderAlias, payload)
@router.get("/aliases", response_model=list[schemas.AliasRead])
def list_aliases(db: Session = Depends(get_db)):
    return _list(db, models.ProviderAlias)

@router.get("/aliases/resolve", response_model=schemas.AliasRead)
def resolve_alias(
    provider: str = Query(min_length=1),
    namespace: str = Query(min_length=1),
    external_id: str = Query(min_length=1),
    db: Session = Depends(get_db),
):
    alias = db.scalar(select(models.ProviderAlias).where(
        models.ProviderAlias.provider == provider,
        models.ProviderAlias.namespace == namespace,
        models.ProviderAlias.external_id == external_id,
    ))
    if alias is None:
        raise HTTPException(status_code=404, detail="Provider alias not found.")
    return alias

@router.get("/entities/{entity_type}/{entity_id}")
def get_entity(entity_type: str, entity_id: str, db: Session = Depends(get_db)):
    model = ENTITY_MODELS.get(entity_type)
    if model is None:
        raise HTTPException(status_code=404, detail="Entity type not found.")
    entity = _require(db, model, entity_id, entity_type)
    result = {"entity_type": entity_type, "id": entity.id}
    for field in ("canonical_key", "display_name", "legal_name", "native_product_id", "symbol", "namespace", "native_identifier", "native_market_id", "native_symbol", "domain", "builder_id"):
        if hasattr(entity, field):
            result[field] = getattr(entity, field)
    return result
