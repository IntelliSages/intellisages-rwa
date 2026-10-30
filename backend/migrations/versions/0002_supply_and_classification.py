"""Add economic supply groups and effective-dated classifications."""
from alembic import op
import sqlalchemy as sa

revision = "0002_supply_classification"
down_revision = "0001_identity_registry"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "economic_supply_groups",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("canonical_key", sa.String(160), nullable=False, unique=True),
        sa.Column("display_name", sa.String(240), nullable=False),
        sa.Column("methodology_notes", sa.String(1000), nullable=False),
    )
    op.create_table(
        "economic_supply_memberships",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("group_id", sa.String(36), sa.ForeignKey("economic_supply_groups.id"), nullable=False),
        sa.Column("issuer_product_id", sa.String(36), sa.ForeignKey("issuer_products.id"), nullable=False),
        sa.Column("membership_type", sa.String(20), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("evidence_ref", sa.String(500), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.UniqueConstraint("issuer_product_id", "effective_from", name="uq_supply_member_product_start"),
    )
    op.create_index("ix_economic_supply_memberships_group_id", "economic_supply_memberships", ["group_id"])
    op.create_index("ix_economic_supply_memberships_issuer_product_id", "economic_supply_memberships", ["issuer_product_id"])
    op.create_table(
        "product_classifications",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("entity_type", sa.String(30), nullable=False),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column("classification", sa.String(20), nullable=False),
        sa.Column("effective_from", sa.Date(), nullable=False),
        sa.Column("effective_to", sa.Date(), nullable=True),
        sa.Column("source", sa.String(120), nullable=False),
        sa.Column("evidence_ref", sa.String(500), nullable=False),
        sa.Column("provider_global_included", sa.Boolean(), nullable=True),
    )
    op.create_index("ix_product_classifications_entity_type", "product_classifications", ["entity_type"])
    op.create_index("ix_product_classifications_entity_id", "product_classifications", ["entity_id"])

def downgrade():
    op.drop_table("product_classifications")
    op.drop_table("economic_supply_memberships")
    op.drop_table("economic_supply_groups")
