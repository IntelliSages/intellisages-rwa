"""Add provider ingestion run and coverage records."""
from alembic import op
import sqlalchemy as sa

revision = "0006_provider_ingestion_runs"
down_revision = "0005_registry_import_reconciliation"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "provider_ingestion_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("provider", sa.String(100), nullable=False),
        sa.Column("dataset", sa.String(120), nullable=False),
        sa.Column("source_version", sa.String(160), nullable=False),
        sa.Column("started_by", sa.String(160), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="snapshot_ready"),
        sa.Column("manifest_sha256", sa.String(64), nullable=False),
        sa.Column("coverage_json", sa.Text(), nullable=False),
        sa.Column("staged_batch_ids_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("error_summary", sa.String(2000), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_provider_ingestion_runs_provider", "provider_ingestion_runs", ["provider"])
    op.create_index("ix_provider_ingestion_runs_status", "provider_ingestion_runs", ["status"])


def downgrade():
    op.drop_index("ix_provider_ingestion_runs_status", table_name="provider_ingestion_runs")
    op.drop_index("ix_provider_ingestion_runs_provider", table_name="provider_ingestion_runs")
    op.drop_table("provider_ingestion_runs")
