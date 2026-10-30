from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/v1/catalogue", tags=["read-only catalogues"])


@router.get(
    "/tokenized-products",
    response_model=schemas.TokenizedProductCatalogueResponse,
)
def list_tokenized_products(
    q: str | None = Query(default=None, max_length=160),
    issuer_id: str | None = Query(default=None),
    network_id: str | None = Query(default=None),
    sort: str = Query(default="underlying", pattern="^(underlying|issuer|product)$"),
    direction: str = Query(default="asc", pattern="^(asc|desc)$"),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    as_of: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    effective_date = as_of or date.today()
    classification_join = (
        (models.ProductClassification.entity_type == "issuer_product")
        & (models.ProductClassification.entity_id == models.IssuerProduct.id)
        & (models.ProductClassification.classification == "rwa")
        & (models.ProductClassification.effective_from <= effective_date)
        & (
            models.ProductClassification.effective_to.is_(None)
            | (models.ProductClassification.effective_to > effective_date)
        )
    )
    base = (
        select(
            models.IssuerProduct,
            models.Issuer,
            models.UnderlyingAsset,
            models.ProductClassification,
        )
        .join(models.Issuer, models.Issuer.id == models.IssuerProduct.issuer_id)
        .join(
            models.UnderlyingAsset,
            models.UnderlyingAsset.id == models.IssuerProduct.underlying_id,
        )
        .join(models.ProductClassification, classification_join)
    )
    if q:
        pattern = f"%{q.strip()}%"
        base = base.where(
            or_(
                models.IssuerProduct.display_name.ilike(pattern),
                models.IssuerProduct.symbol.ilike(pattern),
                models.IssuerProduct.native_product_id.ilike(pattern),
                models.IssuerProduct.canonical_key.ilike(pattern),
                models.Issuer.legal_name.ilike(pattern),
                models.UnderlyingAsset.display_name.ilike(pattern),
                models.UnderlyingAsset.canonical_key.ilike(pattern),
            )
        )
    if issuer_id:
        base = base.where(models.IssuerProduct.issuer_id == issuer_id)
    if network_id:
        verified_on_network = select(models.Deployment.id).where(
            models.Deployment.issuer_product_id == models.IssuerProduct.id,
            models.Deployment.network_id == network_id,
            models.Deployment.is_verified.is_(True),
        ).exists()
        base = base.where(verified_on_network)

    sort_column = {
        "underlying": models.UnderlyingAsset.display_name,
        "issuer": models.Issuer.legal_name,
        "product": models.IssuerProduct.display_name,
    }[sort]
    sort_expression = sort_column.asc() if direction == "asc" else sort_column.desc()
    total = db.scalar(select(func.count()).select_from(base.order_by(None).subquery())) or 0
    rows = db.execute(
        base.order_by(sort_expression, models.IssuerProduct.id)
        .offset(offset)
        .limit(limit)
    ).all()
    product_ids = [row[0].id for row in rows]

    deployment_rows = []
    if product_ids:
        deployment_rows = db.execute(
            select(models.Deployment, models.Network)
            .join(models.Network, models.Network.id == models.Deployment.network_id)
            .where(models.Deployment.issuer_product_id.in_(product_ids))
            .order_by(models.Network.display_name, models.Deployment.id)
        ).all()
    deployments_by_product: dict[str, list] = {}
    for deployment, network in deployment_rows:
        deployments_by_product.setdefault(deployment.issuer_product_id, []).append(
            schemas.CatalogueDeploymentRead(
                id=deployment.id,
                network=schemas.CatalogueNetworkRead(
                    id=network.id,
                    namespace=network.namespace,
                    display_name=network.display_name,
                    family=network.family,
                ),
                native_identifier=deployment.native_identifier,
                representation_type=deployment.representation_type,
                is_verified=deployment.is_verified,
            )
        )

    items = []
    for product, issuer, underlying, classification in rows:
        product_deployments = deployments_by_product.get(product.id, [])
        items.append(
            schemas.TokenizedProductCatalogueItem(
                id=product.id,
                canonical_key=product.canonical_key,
                native_product_id=product.native_product_id,
                display_name=product.display_name,
                symbol=product.symbol,
                instrument_form=product.instrument_form,
                unit_description=product.unit_description,
                representation_type=product.representation_type,
                issuer=schemas.CatalogueIssuerRead(
                    id=issuer.id, legal_name=issuer.legal_name
                ),
                underlying=schemas.CatalogueUnderlyingRead(
                    id=underlying.id,
                    display_name=underlying.display_name,
                    asset_type=underlying.asset_type,
                ),
                classification=schemas.CatalogueClassificationRead(
                    classification="rwa",
                    effective_from=classification.effective_from,
                    effective_to=classification.effective_to,
                    source=classification.source,
                    evidence_ref=classification.evidence_ref,
                    provider_global_included=classification.provider_global_included,
                ),
                deployments=product_deployments,
                unverified_deployment_count=sum(
                    not deployment.is_verified for deployment in product_deployments
                ),
            )
        )

    eligible_products = (
        select(models.IssuerProduct.id)
        .join(models.ProductClassification, classification_join)
        .subquery()
    )
    issuer_facets = db.execute(
        select(models.Issuer.id, models.Issuer.legal_name)
        .join(models.IssuerProduct, models.IssuerProduct.issuer_id == models.Issuer.id)
        .join(eligible_products, eligible_products.c.id == models.IssuerProduct.id)
        .distinct()
        .order_by(models.Issuer.legal_name, models.Issuer.id)
    ).all()
    network_facets = db.execute(
        select(models.Network.id, models.Network.display_name)
        .join(models.Deployment, models.Deployment.network_id == models.Network.id)
        .join(models.IssuerProduct, models.IssuerProduct.id == models.Deployment.issuer_product_id)
        .join(eligible_products, eligible_products.c.id == models.IssuerProduct.id)
        .where(models.Deployment.is_verified.is_(True))
        .distinct()
        .order_by(models.Network.display_name, models.Network.id)
    ).all()

    return schemas.TokenizedProductCatalogueResponse(
        as_of=effective_date,
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        has_more=offset + len(items) < total,
        facets={
            "issuers": [
                schemas.CatalogueFacet(id=row[0], label=row[1]) for row in issuer_facets
            ],
            "networks": [
                schemas.CatalogueFacet(id=row[0], label=row[1]) for row in network_facets
            ],
        },
        coverage=schemas.CatalogueCoverage(
            status="unknown",
            scope="canonical identity registry",
            note=(
                "These are registered, currently RWA-classified issuer products only. "
                "The registry is not a provider-complete market universe; counts and "
                "facets must not be interpreted as global coverage."
            ),
        ),
    )



@router.get(
    "/tokenized-products/{product_id}",
    response_model=schemas.TokenizedProductCatalogueItem,
)
def get_tokenized_product(
    product_id: str,
    as_of: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Return one exact, currently RWA-classified issuer product.

    This is an identity detail endpoint, not a market-data endpoint. It never
    resolves by ticker, symbol, issuer marketing name or fuzzy matching.
    """
    effective_date = as_of or date.today()
    row = db.execute(
        select(
            models.IssuerProduct,
            models.Issuer,
            models.UnderlyingAsset,
            models.ProductClassification,
        )
        .join(models.Issuer, models.Issuer.id == models.IssuerProduct.issuer_id)
        .join(
            models.UnderlyingAsset,
            models.UnderlyingAsset.id == models.IssuerProduct.underlying_id,
        )
        .join(
            models.ProductClassification,
            (models.ProductClassification.entity_type == "issuer_product")
            & (models.ProductClassification.entity_id == models.IssuerProduct.id)
            & (models.ProductClassification.classification == "rwa")
            & (models.ProductClassification.effective_from <= effective_date)
            & (
                models.ProductClassification.effective_to.is_(None)
                | (models.ProductClassification.effective_to > effective_date)
            ),
        )
        .where(models.IssuerProduct.id == product_id)
    ).first()
    if row is None:
        raise HTTPException(
            status_code=404,
            detail="RWA-classified issuer product not found for the requested date.",
        )

    product, issuer, underlying, classification = row
    deployment_rows = db.execute(
        select(models.Deployment, models.Network)
        .join(models.Network, models.Network.id == models.Deployment.network_id)
        .where(models.Deployment.issuer_product_id == product.id)
        .order_by(models.Network.display_name, models.Deployment.id)
    ).all()
    deployments = [
        schemas.CatalogueDeploymentRead(
            id=deployment.id,
            network=schemas.CatalogueNetworkRead(
                id=network.id,
                namespace=network.namespace,
                display_name=network.display_name,
                family=network.family,
            ),
            native_identifier=deployment.native_identifier,
            representation_type=deployment.representation_type,
            is_verified=deployment.is_verified,
        )
        for deployment, network in deployment_rows
    ]
    return schemas.TokenizedProductCatalogueItem(
        id=product.id,
        canonical_key=product.canonical_key,
        native_product_id=product.native_product_id,
        display_name=product.display_name,
        symbol=product.symbol,
        instrument_form=product.instrument_form,
        unit_description=product.unit_description,
        representation_type=product.representation_type,
        issuer=schemas.CatalogueIssuerRead(id=issuer.id, legal_name=issuer.legal_name),
        underlying=schemas.CatalogueUnderlyingRead(
            id=underlying.id,
            display_name=underlying.display_name,
            asset_type=underlying.asset_type,
        ),
        classification=schemas.CatalogueClassificationRead(
            classification="rwa",
            effective_from=classification.effective_from,
            effective_to=classification.effective_to,
            source=classification.source,
            evidence_ref=classification.evidence_ref,
            provider_global_included=classification.provider_global_included,
        ),
        deployments=deployments,
        unverified_deployment_count=sum(not item.is_verified for item in deployments),
    )
