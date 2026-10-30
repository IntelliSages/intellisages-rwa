from datetime import date, datetime, timezone
from uuid import uuid4
from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

def new_id() -> str:
    return str(uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Base(DeclarativeBase):
    pass

class UnderlyingAsset(Base):
    __tablename__ = "underlying_assets"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    canonical_key: Mapped[str] = mapped_column(String(160), unique=True)
    display_name: Mapped[str] = mapped_column(String(240))
    asset_type: Mapped[str] = mapped_column(String(40))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

class Issuer(Base):
    __tablename__ = "issuers"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    canonical_key: Mapped[str] = mapped_column(String(160), unique=True)
    legal_name: Mapped[str] = mapped_column(String(240))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

class IssuerProduct(Base):
    __tablename__ = "issuer_products"
    __table_args__ = (UniqueConstraint("issuer_id", "native_product_id", name="uq_product_issuer_native_id"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    canonical_key: Mapped[str] = mapped_column(String(160), unique=True)
    issuer_id: Mapped[str] = mapped_column(ForeignKey("issuers.id"), index=True)
    underlying_id: Mapped[str] = mapped_column(ForeignKey("underlying_assets.id"), index=True)
    native_product_id: Mapped[str] = mapped_column(String(180))
    display_name: Mapped[str] = mapped_column(String(240))
    symbol: Mapped[str | None] = mapped_column(String(80), nullable=True)
    instrument_form: Mapped[str] = mapped_column(String(60))
    unit_description: Mapped[str] = mapped_column(String(240))
    representation_type: Mapped[str] = mapped_column(String(30), default="unknown")
    issuer: Mapped[Issuer] = relationship()
    underlying: Mapped[UnderlyingAsset] = relationship()

class Network(Base):
    __tablename__ = "networks"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    namespace: Mapped[str] = mapped_column(String(120), unique=True)
    display_name: Mapped[str] = mapped_column(String(120))
    family: Mapped[str] = mapped_column(String(30))

class Deployment(Base):
    __tablename__ = "deployments"
    __table_args__ = (UniqueConstraint("network_id", "normalized_identifier", name="uq_deployment_network_identifier"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    issuer_product_id: Mapped[str] = mapped_column(ForeignKey("issuer_products.id"), index=True)
    network_id: Mapped[str] = mapped_column(ForeignKey("networks.id"), index=True)
    native_identifier: Mapped[str] = mapped_column(String(220))
    normalized_identifier: Mapped[str] = mapped_column(String(220))
    representation_type: Mapped[str] = mapped_column(String(30), default="unknown")
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    issuer_product: Mapped[IssuerProduct] = relationship()
    network: Mapped[Network] = relationship()

class Venue(Base):
    __tablename__ = "venues"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    canonical_key: Mapped[str] = mapped_column(String(160), unique=True)
    display_name: Mapped[str] = mapped_column(String(180))
    venue_type: Mapped[str] = mapped_column(String(40))

class PerpetualContract(Base):
    __tablename__ = "perpetual_contracts"
    __table_args__ = (UniqueConstraint("venue_id", "domain", "native_market_id", name="uq_perp_venue_domain_market"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    canonical_key: Mapped[str] = mapped_column(String(200), unique=True)
    venue_id: Mapped[str] = mapped_column(ForeignKey("venues.id"), index=True)
    native_market_id: Mapped[str] = mapped_column(String(180))
    native_symbol: Mapped[str] = mapped_column(String(100))
    domain: Mapped[str] = mapped_column(String(120), default="")
    builder_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    underlying_id: Mapped[str | None] = mapped_column(ForeignKey("underlying_assets.id"), nullable=True)
    issuer_product_id: Mapped[str | None] = mapped_column(ForeignKey("issuer_products.id"), nullable=True)
    venue: Mapped[Venue] = relationship()

class PerpetualContractMigration(Base):
    __tablename__ = "perpetual_contract_migrations"
    __table_args__ = (
        UniqueConstraint(
            "predecessor_contract_id", "successor_contract_id", "event_type", "effective_at",
            name="uq_perp_migration_edge_event_date",
        ),
        CheckConstraint(
            "successor_contract_id IS NULL OR predecessor_contract_id <> successor_contract_id",
            name="ck_perp_migration_not_self",
        ),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    predecessor_contract_id: Mapped[str] = mapped_column(
        ForeignKey("perpetual_contracts.id"), index=True
    )
    successor_contract_id: Mapped[str | None] = mapped_column(
        ForeignKey("perpetual_contracts.id"), nullable=True, index=True
    )
    event_type: Mapped[str] = mapped_column(String(30))
    effective_at: Mapped[date] = mapped_column(Date)
    previous_native_market_id: Mapped[str] = mapped_column(String(180))
    new_native_market_id: Mapped[str | None] = mapped_column(String(180), nullable=True)
    previous_native_symbol: Mapped[str] = mapped_column(String(100))
    new_native_symbol: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source: Mapped[str] = mapped_column(String(120))
    evidence_ref: Mapped[str] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    predecessor: Mapped[PerpetualContract] = relationship(
        foreign_keys=[predecessor_contract_id]
    )
    successor: Mapped[PerpetualContract | None] = relationship(
        foreign_keys=[successor_contract_id]
    )


class ProviderAlias(Base):
    __tablename__ = "provider_aliases"
    __table_args__ = (UniqueConstraint("provider", "namespace", "external_id", "effective_from", name="uq_provider_alias_external_start"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    provider: Mapped[str] = mapped_column(String(100), index=True)
    namespace: Mapped[str] = mapped_column(String(100))
    external_id: Mapped[str] = mapped_column(String(220))
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    entity_type: Mapped[str] = mapped_column(String(40))
    entity_id: Mapped[str] = mapped_column(String(36), index=True)
    evidence_ref: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

class EconomicSupplyGroup(Base):
    __tablename__ = "economic_supply_groups"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    canonical_key: Mapped[str] = mapped_column(String(160), unique=True)
    display_name: Mapped[str] = mapped_column(String(240))
    methodology_notes: Mapped[str] = mapped_column(String(1000))

class EconomicSupplyMembership(Base):
    __tablename__ = "economic_supply_memberships"
    __table_args__ = (UniqueConstraint("issuer_product_id", "effective_from", name="uq_supply_member_product_start"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    group_id: Mapped[str] = mapped_column(ForeignKey("economic_supply_groups.id"), index=True)
    issuer_product_id: Mapped[str] = mapped_column(ForeignKey("issuer_products.id"), index=True)
    membership_type: Mapped[str] = mapped_column(String(20))
    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    evidence_ref: Mapped[str] = mapped_column(String(500))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

class ProductClassification(Base):
    __tablename__ = "product_classifications"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    entity_type: Mapped[str] = mapped_column(String(30), index=True)
    entity_id: Mapped[str] = mapped_column(String(36), index=True)
    classification: Mapped[str] = mapped_column(String(20))
    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    source: Mapped[str] = mapped_column(String(120))
    evidence_ref: Mapped[str] = mapped_column(String(500))
    provider_global_included: Mapped[bool | None] = mapped_column(Boolean, nullable=True)


class RegistryImportBatch(Base):
    __tablename__ = "registry_import_batches"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    source: Mapped[str] = mapped_column(String(100), index=True)
    source_version: Mapped[str | None] = mapped_column(String(160), nullable=True)
    submitted_by: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(30), default="staged", index=True)
    total_records: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class RegistryImportRecord(Base):
    __tablename__ = "registry_import_records"
    __table_args__ = (UniqueConstraint("batch_id", "row_number", name="uq_import_record_batch_row"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    batch_id: Mapped[str] = mapped_column(ForeignKey("registry_import_batches.id", ondelete="CASCADE"), index=True)
    row_number: Mapped[int] = mapped_column(Integer)
    entity_type: Mapped[str] = mapped_column(String(40), index=True)
    source_namespace: Mapped[str] = mapped_column(String(100))
    external_id: Mapped[str] = mapped_column(String(220))
    raw_payload_json: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="needs_review", index=True)
    resolution_method: Mapped[str | None] = mapped_column(String(80), nullable=True)
    resolved_entity_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    resolved_entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    evidence_ref: Mapped[str | None] = mapped_column(String(500), nullable=True)
    decision_note: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(160), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class RegistryImportCandidate(Base):
    __tablename__ = "registry_import_candidates"
    __table_args__ = (UniqueConstraint("import_record_id", "candidate_entity_type", "candidate_entity_id", name="uq_import_candidate_entity"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    import_record_id: Mapped[str] = mapped_column(ForeignKey("registry_import_records.id", ondelete="CASCADE"), index=True)
    candidate_entity_type: Mapped[str] = mapped_column(String(40))
    candidate_entity_id: Mapped[str] = mapped_column(String(36))
    match_basis: Mapped[str] = mapped_column(String(80))
    confidence: Mapped[float] = mapped_column(Float)
    evidence_ref: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class RegistryImportAuditEvent(Base):
    __tablename__ = "registry_import_audit_events"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    batch_id: Mapped[str] = mapped_column(ForeignKey("registry_import_batches.id", ondelete="CASCADE"), index=True)
    import_record_id: Mapped[str | None] = mapped_column(ForeignKey("registry_import_records.id", ondelete="SET NULL"), nullable=True, index=True)
    actor: Mapped[str] = mapped_column(String(160))
    action: Mapped[str] = mapped_column(String(80), index=True)
    details_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
