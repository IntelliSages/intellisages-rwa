from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

AssetType = Literal["equity", "commodity", "fund", "real_estate", "private_asset", "other"]
RepresentationType = Literal["independent_issuance", "bridge", "wrapper", "unknown"]
EntityType = Literal["underlying", "issuer", "issuer_product", "deployment", "venue", "perpetual_contract"]

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

class AliasCreate(StrictModel):
    provider: str = Field(min_length=1, max_length=100)
    namespace: str = Field(min_length=1, max_length=100)
    external_id: str = Field(min_length=1, max_length=220)
    entity_type: EntityType
    entity_id: str
    evidence_ref: str | None = Field(default=None, max_length=500)
    is_verified: bool = False
class AliasRead(AliasCreate):
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
