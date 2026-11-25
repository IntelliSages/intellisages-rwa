"""Add append-only deployment verification events."""

from alembic import op
import sqlalchemy as sa

revision = "0009_deployment_verification"
down_revision = "0008_widen_match_basis"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "deployment_verification_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("deployment_id", sa.String(36), sa.ForeignKey("deployments.id"), nullable=False),
        sa.Column("verified", sa.Boolean(), nullable=False),
        sa.Column("evidence_ref", sa.String(500), nullable=False),
        sa.Column("verified_by", sa.String(160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_deployment_verification_events_deployment_id",
        "deployment_verification_events", ["deployment_id"])


def downgrade():
    op.drop_index(
        "ix_deployment_verification_events_deployment_id",
        table_name="deployment_verification_events")
    op.drop_table("deployment_verification_events")
