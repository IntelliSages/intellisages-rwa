from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

AssetType = Literal["equity", "commodity", "fund", "real_estate", "private_asset", "other"]
RepresentationType = Literal["independent_issuance", "bridge", "wrapper", "unknown"]
EntityType = Literal["underlying", "issuer", "network", "issuer_product", "deployment", "venue", "perpetual_contract"]

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

class UnderlyingCreate(StrictModel):
    canonical_key: str = Field(min_length=2, max_length=160, pattern=r"^[a-z0-9][a-z0-9._:-]*$")
    display_name: str = Field(min_length=1, max_length=240)
    asset_type: AssetType
class UnderlyingRead(UnderlyingCreate):
    id: str

class IssuerCreate(StrictModel):
    canonical_key: str = Field(min_length=2, max_length=160, pattern=r"^[a-z0-9][a-z0-9._:-]*$")
    legal_name: str = Field(min_length=1, max_length=240)
class IssuerRead(IssuerCreate):
    id: str

class ProductCreate(StrictModel):
    canonical_key: str = Field(min_length=2, max_length=160, pattern=r"^[a-z0-9][a-z0-9._:-]*$")
    issuer_id: str
    underlying_id: str
    native_product_id: str = Field(min_length=1, max_length=180)
    display_name: str = Field(min_length=1, max_length=240)
    symbol: str | None = Field(default=None, max_length=80)
    instrument_form: str = Field(min_length=1, max_length=60)
    unit_description: str = Field(min_length=1, max_length=240)
    representation_type: RepresentationType = "unknown"
class ProductRead(ProductCreate):
    id: str

class NetworkCreate(StrictModel):
    namespace: str = Field(min_length=3, max_length=120)
    display_name: str = Field(min_length=1, max_length=120)
    family: Literal["evm", "solana", "sui", "cosmos", "other"]
class NetworkRead(NetworkCreate):
    id: str

class DeploymentCreate(StrictModel):
    issuer_product_id: str
    network_id: str
    native_identifier: str = Field(min_length=1, max_length=220)
    representation_type: RepresentationType = "unknown"
    is_verified: bool = False
class DeploymentRead(DeploymentCreate):
    id: str
    normalized_identifier: str

class VenueCreate(StrictModel):
    canonical_key: str = Field(min_length=2, max_length=160, pattern=r"^[a-z0-9][a-z0-9._:-]*$")
    display_name: str = Field(min_length=1, max_length=180)
    venue_type: Literal["centralized_exchange", "dex", "perp_dex", "protocol", "other"]
class VenueRead(VenueCreate):
    id: str

class PerpetualCreate(StrictModel):
    canonical_key: str = Field(min_length=2, max_length=200, pattern=r"^[a-z0-9][a-z0-9._:-]*$")
    venue_id: str
    native_market_id: str = Field(min_length=1, max_length=180)
    native_symbol: str = Field(min_length=1, max_length=100)
    builder_id: str | None = Field(default=None, max_length=120)
    domain: str = Field(default="", max_length=120)
    underlying_id: str | None = None
    issuer_product_id: str | None = None

    @model_validator(mode="after")
    def builder_requires_domain(self):
        if self.builder_id and not self.domain:
            raise ValueError("Builder-scoped perpetuals require an exact domain.")
        return self
class PerpetualRead(PerpetualCreate):
    id: str

class PerpetualMigrationCreate(StrictModel):
    predecessor_contract_id: str
    successor_contract_id: str | None = None
    event_type: Literal[
        "symbol_changed", "market_id_changed", "venue_migrated",
        "replaced", "delisted", "expired"
    ]
    effective_at: date
    new_native_symbol: str | None = Field(default=None, min_length=1, max_length=100)
    source: str = Field(min_length=1, max_length=120)
    evidence_ref: str = Field(min_length=1, max_length=500)
    notes: str | None = Field(default=None, max_length=1000)
    is_verified: bool = False

    @model_validator(mode="after")
    def validate_successor(self):
        terminal_event = self.event_type in {"delisted", "expired"}
        if terminal_event and self.successor_contract_id is not None:
            raise ValueError("Delisting and expiry events cannot have a successor contract.")
        if self.event_type == "symbol_changed":
            if self.successor_contract_id is not None:
                raise ValueError("A symbol-only change is recorded against one contract without a successor.")
            if self.new_native_symbol is None:
                raise ValueError("A symbol change requires the new native symbol.")
        elif not terminal_event and self.successor_contract_id is None:
            raise ValueError("This migration event requires a successor contract.")
        if self.successor_contract_id == self.predecessor_contract_id:
            raise ValueError("A perpetual contract cannot migrate to itself.")
        return self


class PerpetualMigrationRead(PerpetualMigrationCreate):
    id: str
    previous_native_market_id: str
    new_native_market_id: str | None
    previous_native_symbol: str


class AliasCreate(StrictModel):
    provider: str = Field(min_length=1, max_length=100)
    namespace: str = Field(min_length=1, max_length=100)
    external_id: str = Field(min_length=1, max_length=220)
    effective_from: date
    effective_to: date | None = None
    entity_type: EntityType
    entity_id: str
    evidence_ref: str | None = Field(default=None, max_length=500)
    is_verified: bool = False

    @model_validator(mode="after")
    def valid_period(self):
        if self.effective_to is not None and self.effective_to <= self.effective_from:
            raise ValueError("effective_to must be later than effective_from")
        return self

class AliasClose(StrictModel):
    effective_to: date

class AliasRead(StrictModel):
    provider: str
    namespace: str
    external_id: str
    effective_from: date | None
    effective_to: date | None
    entity_type: EntityType
    entity_id: str
    evidence_ref: str | None
    is_verified: bool
    id: str

class SupplyGroupCreate(StrictModel):
    canonical_key: str = Field(min_length=2, max_length=160, pattern=r"^[a-z0-9][a-z0-9._:-]*$")
    display_name: str = Field(min_length=1, max_length=240)
    methodology_notes: str = Field(min_length=1, max_length=1000)
class SupplyGroupRead(SupplyGroupCreate):
    id: str

class SupplyMembershipCreate(StrictModel):
    group_id: str
    issuer_product_id: str
    membership_type: Literal["native", "bridge", "wrapper"]
    effective_from: date
    effective_to: date | None = None
    evidence_ref: str = Field(min_length=1, max_length=500)
    is_verified: bool = False

    @model_validator(mode="after")
    def valid_period(self):
        if self.effective_to is not None and self.effective_to <= self.effective_from:
            raise ValueError("effective_to must be later than effective_from")
        return self
class SupplyMembershipRead(SupplyMembershipCreate):
    id: str

class ClassificationCreate(StrictModel):
    entity_type: Literal["underlying", "issuer_product"]
    entity_id: str
    classification: Literal["crypto", "rwa", "other", "unknown"]
    effective_from: date
    effective_to: date | None = None
    source: str = Field(min_length=1, max_length=120)
    evidence_ref: str = Field(min_length=1, max_length=500)
    provider_global_included: bool | None = None

    @model_validator(mode="after")
    def valid_period(self):
        if self.effective_to is not None and self.effective_to <= self.effective_from:
            raise ValueError("effective_to must be later than effective_from")
        return self
class ClassificationRead(ClassificationCreate):
    id: str


class CatalogueIssuerRead(BaseModel):
    id: str
    legal_name: str

class CatalogueUnderlyingRead(BaseModel):
    id: str
    display_name: str
    asset_type: str

class CatalogueNetworkRead(BaseModel):
    id: str
    namespace: str
    display_name: str
    family: str

class CatalogueDeploymentRead(BaseModel):
    id: str
    network: CatalogueNetworkRead
    native_identifier: str
    representation_type: RepresentationType
    is_verified: bool

class CatalogueClassificationRead(BaseModel):
    classification: Literal["rwa"]
    effective_from: date
    effective_to: date | None
    source: str
    evidence_ref: str
    provider_global_included: bool | None

class TokenizedProductCatalogueItem(BaseModel):
    id: str
    canonical_key: str
    native_product_id: str
    display_name: str
    symbol: str | None
    instrument_form: str
    unit_description: str
    representation_type: RepresentationType
    issuer: CatalogueIssuerRead
    underlying: CatalogueUnderlyingRead
    classification: CatalogueClassificationRead
    deployments: list[CatalogueDeploymentRead]
    unverified_deployment_count: int

class CatalogueFacet(BaseModel):
    id: str
    label: str

class CatalogueCoverage(BaseModel):
    status: Literal["unknown"]
    scope: str
    note: str

class TokenizedProductCatalogueResponse(BaseModel):
    as_of: date
    items: list[TokenizedProductCatalogueItem]
    total: int
    limit: int
    offset: int
    has_more: bool
    facets: dict[str, list[CatalogueFacet]]
    coverage: CatalogueCoverage
