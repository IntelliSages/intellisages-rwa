import re
from datetime import date
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
    "network": models.Network,
    "network": models.Network,
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


@router.post("/perpetual-contract-migrations", response_model=schemas.PerpetualMigrationRead, status_code=201)
def create_perpetual_migration(
    payload: schemas.PerpetualMigrationCreate, db: Session = Depends(get_db)
):
    predecessor = _require(
        db, models.PerpetualContract, payload.predecessor_contract_id, "Predecessor perpetual contract"
    )
    successor = None
    if payload.successor_contract_id is not None:
        successor = _require(
            db, models.PerpetualContract, payload.successor_contract_id, "Successor perpetual contract"
        )

        # Migration edges are directed. Reject a new edge if the successor already
        # reaches the predecessor; otherwise historical lineage would become cyclic.
        edges = db.execute(
            select(
                models.PerpetualContractMigration.predecessor_contract_id,
                models.PerpetualContractMigration.successor_contract_id,
            ).where(models.PerpetualContractMigration.successor_contract_id.is_not(None))
        ).all()
        adjacency: dict[str, set[str]] = {}
        for predecessor_id, successor_id in edges:
            adjacency.setdefault(predecessor_id, set()).add(successor_id)

        pending = [payload.successor_contract_id]
        visited: set[str] = set()
        while pending:
            current = pending.pop()
            if current == payload.predecessor_contract_id:
                raise HTTPException(status_code=409, detail="Perpetual contract migration would create a lineage cycle.")
            if current in visited:
                continue
            visited.add(current)
            pending.extend(adjacency.get(current, ()))

    duplicate = db.scalar(
        select(models.PerpetualContractMigration).where(
            models.PerpetualContractMigration.predecessor_contract_id == payload.predecessor_contract_id,
            models.PerpetualContractMigration.successor_contract_id == payload.successor_contract_id,
            models.PerpetualContractMigration.event_type == payload.event_type,
            models.PerpetualContractMigration.effective_at == payload.effective_at,
        )
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="This perpetual contract migration event is already registered.")
    event_data = payload.model_dump()
    event_data["previous_native_market_id"] = predecessor.native_market_id
    event_data["previous_native_symbol"] = predecessor.native_symbol
    if payload.event_type == "symbol_changed":
        event_data["new_native_market_id"] = predecessor.native_market_id
        event_data["new_native_symbol"] = payload.new_native_symbol
    elif successor is not None:
        event_data["new_native_market_id"] = successor.native_market_id
        event_data["new_native_symbol"] = successor.native_symbol
    else:
        event_data["new_native_market_id"] = None
        event_data["new_native_symbol"] = None

    record = models.PerpetualContractMigration(**event_data)
    db.add(record)
    try:
        db.commit()
        db.refresh(record)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Perpetual contract migration conflicts with an existing event.") from exc
    return record


@router.get("/perpetual-contract-migrations", response_model=list[schemas.PerpetualMigrationRead])
def list_perpetual_migrations(db: Session = Depends(get_db)):
    return db.scalars(
        select(models.PerpetualContractMigration).order_by(
            models.PerpetualContractMigration.effective_at,
            models.PerpetualContractMigration.id,
        )
    ).all()


@router.post("/aliases", response_model=schemas.AliasRead, status_code=201)
def create_alias(payload: schemas.AliasCreate, db: Session = Depends(get_db)):
    _require(db, ENTITY_MODELS[payload.entity_type], payload.entity_id, payload.entity_type)
    conditions = [
        models.ProviderAlias.provider == payload.provider,
        models.ProviderAlias.namespace == payload.namespace,
        models.ProviderAlias.external_id == payload.external_id,
        or_(
            models.ProviderAlias.effective_to.is_(None),
            models.ProviderAlias.effective_to > payload.effective_from,
        ),
    ]
    if payload.effective_to is not None:
        conditions.append(
            or_(
                models.ProviderAlias.effective_from.is_(None),
                models.ProviderAlias.effective_from < payload.effective_to,
            )
        )
    overlap = db.scalar(select(models.ProviderAlias).where(*conditions))
    if overlap:
        raise HTTPException(status_code=409, detail="Provider alias has an overlapping effective period.")
    return _create(db, models.ProviderAlias, payload)
@router.get("/aliases", response_model=list[schemas.AliasRead])
def list_aliases(db: Session = Depends(get_db)):
    return _list(db, models.ProviderAlias)

@router.patch("/aliases/{alias_id}/close", response_model=schemas.AliasRead)
def close_alias(alias_id: str, payload: schemas.AliasClose, db: Session = Depends(get_db)):
    alias = _require(db, models.ProviderAlias, alias_id, "Provider alias")
    if alias.effective_to is not None:
        raise HTTPException(status_code=409, detail="Provider alias is already closed.")
    if alias.effective_from is not None and payload.effective_to <= alias.effective_from:
        raise HTTPException(status_code=422, detail="effective_to must be later than effective_from.")

    conditions = [
        models.ProviderAlias.id != alias.id,
        models.ProviderAlias.provider == alias.provider,
        models.ProviderAlias.namespace == alias.namespace,
        models.ProviderAlias.external_id == alias.external_id,
        or_(
            models.ProviderAlias.effective_from.is_(None),
            models.ProviderAlias.effective_from < payload.effective_to,
        ),
    ]
    if alias.effective_from is not None:
        conditions.append(
            or_(
                models.ProviderAlias.effective_to.is_(None),
                models.ProviderAlias.effective_to > alias.effective_from,
            )
        )
    conflict = db.scalar(select(models.ProviderAlias).where(*conditions))
    if conflict:
        raise HTTPException(status_code=409, detail="Closing this alias would overlap another effective alias period.")

    alias.effective_to = payload.effective_to
    try:
        db.commit()
        db.refresh(alias)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Provider alias history conflicts with an existing record.") from exc
    return alias


@router.get("/aliases/resolve", response_model=schemas.AliasRead)
def resolve_alias(
    provider: str = Query(min_length=1),
    namespace: str = Query(min_length=1),
    external_id: str = Query(min_length=1),
    as_of: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    effective_date = as_of or date.today()
    alias = db.scalar(select(models.ProviderAlias).where(
        models.ProviderAlias.provider == provider,
        models.ProviderAlias.namespace == namespace,
        models.ProviderAlias.external_id == external_id,
        or_(
            models.ProviderAlias.effective_from.is_(None),
            models.ProviderAlias.effective_from <= effective_date,
        ),
        or_(
            models.ProviderAlias.effective_to.is_(None),
            models.ProviderAlias.effective_to > effective_date,
        ),
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
    for field in ("canonical_key", "display_name", "legal_name", "native_product_id", "symbol", "namespace", "display_name", "family", "native_identifier", "native_market_id", "native_symbol", "domain", "builder_id"):
        if hasattr(entity, field):
            result[field] = getattr(entity, field)
    return result

@router.post("/supply-groups", response_model=schemas.SupplyGroupRead, status_code=201)
def create_supply_group(payload: schemas.SupplyGroupCreate, db: Session = Depends(get_db)):
    return _create(db, models.EconomicSupplyGroup, payload)

@router.get("/supply-groups", response_model=list[schemas.SupplyGroupRead])
def list_supply_groups(db: Session = Depends(get_db)):
    return _list(db, models.EconomicSupplyGroup)

@router.post("/supply-memberships", response_model=schemas.SupplyMembershipRead, status_code=201)
def create_supply_membership(payload: schemas.SupplyMembershipCreate, db: Session = Depends(get_db)):
    _require(db, models.EconomicSupplyGroup, payload.group_id, "Economic supply group")
    _require(db, models.IssuerProduct, payload.issuer_product_id, "Issuer product")
    conditions = [
        models.EconomicSupplyMembership.issuer_product_id == payload.issuer_product_id,
        or_(
            models.EconomicSupplyMembership.effective_to.is_(None),
            models.EconomicSupplyMembership.effective_to > payload.effective_from,
        ),
    ]
    if payload.effective_to is not None:
        conditions.append(models.EconomicSupplyMembership.effective_from < payload.effective_to)
    overlap = db.scalar(select(models.EconomicSupplyMembership).where(*conditions))
    if overlap:
        raise HTTPException(status_code=409, detail="Product already has an overlapping economic-supply membership.")
    return _create(db, models.EconomicSupplyMembership, payload)

@router.get("/supply-memberships", response_model=list[schemas.SupplyMembershipRead])
def list_supply_memberships(db: Session = Depends(get_db)):
    return _list(db, models.EconomicSupplyMembership)

@router.post("/classifications", response_model=schemas.ClassificationRead, status_code=201)
def create_classification(payload: schemas.ClassificationCreate, db: Session = Depends(get_db)):
    target_model = {"underlying": models.UnderlyingAsset, "issuer_product": models.IssuerProduct}[payload.entity_type]
    _require(db, target_model, payload.entity_id, payload.entity_type)
    conditions = [
        models.ProductClassification.entity_type == payload.entity_type,
        models.ProductClassification.entity_id == payload.entity_id,
        or_(
            models.ProductClassification.effective_to.is_(None),
            models.ProductClassification.effective_to > payload.effective_from,
        ),
    ]
    if payload.effective_to is not None:
        conditions.append(models.ProductClassification.effective_from < payload.effective_to)
    overlap = db.scalar(select(models.ProductClassification).where(*conditions))
    if overlap:
        raise HTTPException(status_code=409, detail="Classification periods for an entity cannot overlap.")
    return _create(db, models.ProductClassification, payload)

@router.get("/classifications", response_model=list[schemas.ClassificationRead])
def list_classifications(entity_type: str | None = Query(default=None), entity_id: str | None = Query(default=None), db: Session = Depends(get_db)):
    query = select(models.ProductClassification)
    if entity_type:
        query = query.where(models.ProductClassification.entity_type == entity_type)
    if entity_id:
        query = query.where(models.ProductClassification.entity_id == entity_id)
    return db.scalars(query.order_by(models.ProductClassification.effective_from)).all()
