"""Create canonical identity registry."""
from alembic import op
import sqlalchemy as sa
revision = "0001_identity_registry"
down_revision = None
branch_labels = None
depends_on = None

def _id():
    return sa.Column("id", sa.String(36), primary_key=True)

def upgrade():
    op.create_table("underlying_assets", _id(), sa.Column("canonical_key", sa.String(160), nullable=False, unique=True), sa.Column("display_name", sa.String(240), nullable=False), sa.Column("asset_type", sa.String(40), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("issuers", _id(), sa.Column("canonical_key", sa.String(160), nullable=False, unique=True), sa.Column("legal_name", sa.String(240), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("issuer_products", _id(), sa.Column("canonical_key", sa.String(160), nullable=False, unique=True), sa.Column("issuer_id", sa.String(36), sa.ForeignKey("issuers.id"), nullable=False), sa.Column("underlying_id", sa.String(36), sa.ForeignKey("underlying_assets.id"), nullable=False), sa.Column("native_product_id", sa.String(180), nullable=False), sa.Column("display_name", sa.String(240), nullable=False), sa.Column("symbol", sa.String(80)), sa.Column("instrument_form", sa.String(60), nullable=False), sa.Column("unit_description", sa.String(240), nullable=False), sa.Column("representation_type", sa.String(30), nullable=False), sa.UniqueConstraint("issuer_id", "native_product_id", name="uq_product_issuer_native_id"))
    op.create_index("ix_issuer_products_issuer_id", "issuer_products", ["issuer_id"])
    op.create_index("ix_issuer_products_underlying_id", "issuer_products", ["underlying_id"])
    op.create_table("networks", _id(), sa.Column("namespace", sa.String(120), nullable=False, unique=True), sa.Column("display_name", sa.String(120), nullable=False), sa.Column("family", sa.String(30), nullable=False))
    op.create_table("deployments", _id(), sa.Column("issuer_product_id", sa.String(36), sa.ForeignKey("issuer_products.id"), nullable=False), sa.Column("network_id", sa.String(36), sa.ForeignKey("networks.id"), nullable=False), sa.Column("native_identifier", sa.String(220), nullable=False), sa.Column("normalized_identifier", sa.String(220), nullable=False), sa.Column("representation_type", sa.String(30), nullable=False), sa.Column("is_verified", sa.Boolean(), nullable=False), sa.UniqueConstraint("network_id", "normalized_identifier", name="uq_deployment_network_identifier"))
    op.create_index("ix_deployments_issuer_product_id", "deployments", ["issuer_product_id"])
    op.create_index("ix_deployments_network_id", "deployments", ["network_id"])
    op.create_table("venues", _id(), sa.Column("canonical_key", sa.String(160), nullable=False, unique=True), sa.Column("display_name", sa.String(180), nullable=False), sa.Column("venue_type", sa.String(40), nullable=False))
    op.create_table("perpetual_contracts", _id(), sa.Column("canonical_key", sa.String(200), nullable=False, unique=True), sa.Column("venue_id", sa.String(36), sa.ForeignKey("venues.id"), nullable=False), sa.Column("native_market_id", sa.String(180), nullable=False), sa.Column("native_symbol", sa.String(100), nullable=False), sa.Column("domain", sa.String(120), nullable=False), sa.Column("builder_id", sa.String(120)), sa.Column("underlying_id", sa.String(36), sa.ForeignKey("underlying_assets.id")), sa.Column("issuer_product_id", sa.String(36), sa.ForeignKey("issuer_products.id")), sa.UniqueConstraint("venue_id", "domain", "native_market_id", name="uq_perp_venue_domain_market"))
    op.create_index("ix_perpetual_contracts_venue_id", "perpetual_contracts", ["venue_id"])
    op.create_table("provider_aliases", _id(), sa.Column("provider", sa.String(100), nullable=False), sa.Column("namespace", sa.String(100), nullable=False), sa.Column("external_id", sa.String(220), nullable=False), sa.Column("entity_type", sa.String(40), nullable=False), sa.Column("entity_id", sa.String(36), nullable=False), sa.Column("evidence_ref", sa.String(500)), sa.Column("is_verified", sa.Boolean(), nullable=False), sa.UniqueConstraint("provider", "namespace", "external_id", name="uq_provider_alias_external"))
    op.create_index("ix_provider_aliases_provider", "provider_aliases", ["provider"])
    op.create_index("ix_provider_aliases_entity_id", "provider_aliases", ["entity_id"])

def downgrade():
    for table in ["provider_aliases", "perpetual_contracts", "venues", "deployments", "networks", "issuer_products", "issuers", "underlying_assets"]:
        op.drop_table(table)
