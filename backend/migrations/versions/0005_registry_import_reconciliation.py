"""Add staged registry import, candidate review and audit history."""
from alembic import op
import sqlalchemy as sa

revision = "0005_registry_import_reconciliation"
down_revision = "0004_perpetual_contract_migrations"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "registry_import_batches",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("source", sa.String(100), nullable=False),
        sa.Column("source_version", sa.String(160), nullable=True),
        sa.Column("submitted_by", sa.String(160), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="staged"),
        sa.Column("total_records", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_registry_import_batches_source", "registry_import_batches", ["source"])
    op.create_index("ix_registry_import_batches_status", "registry_import_batches", ["status"])
    op.create_table(
        "registry_import_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("batch_id", sa.String(36), sa.ForeignKey("registry_import_batches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("row_number", sa.Integer(), nullable=False),
        sa.Column("entity_type", sa.String(40), nullable=False),
        sa.Column("source_namespace", sa.String(100), nullable=False),
        sa.Column("external_id", sa.String(220), nullable=False),
        sa.Column("raw_payload_json", sa.Text(), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="needs_review"),
        sa.Column("resolution_method", sa.String(80), nullable=True),
        sa.Column("resolved_entity_type", sa.String(40), nullable=True),
        sa.Column("resolved_entity_id", sa.String(36), nullable=True),
        sa.Column("evidence_ref", sa.String(500), nullable=True),
        sa.Column("decision_note", sa.String(1000), nullable=True),
        sa.Column("reviewed_by", sa.String(160), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("batch_id", "row_number", name="uq_import_record_batch_row"),
    )
    for col in ("batch_id", "entity_type", "status"):
        op.create_index(f"ix_registry_import_records_{col}", "registry_import_records", [col])
    op.create_table(
        "registry_import_candidates",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("import_record_id", sa.String(36), sa.ForeignKey("registry_import_records.id", ondelete="CASCADE"), nullable=False),
        sa.Column("candidate_entity_type", sa.String(40), nullable=False),
        sa.Column("candidate_entity_id", sa.String(36), nullable=False),
        sa.Column("match_basis", sa.String(80), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("evidence_ref", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("import_record_id", "candidate_entity_type", "candidate_entity_id", name="uq_import_candidate_entity"),
    )
    op.create_index("ix_registry_import_candidates_import_record_id", "registry_import_candidates", ["import_record_id"])
    op.create_table(
        "registry_import_audit_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("batch_id", sa.String(36), sa.ForeignKey("registry_import_batches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("import_record_id", sa.String(36), sa.ForeignKey("registry_import_records.id", ondelete="SET NULL"), nullable=True),
        sa.Column("actor", sa.String(160), nullable=False),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("details_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_registry_import_audit_events_batch_id", "registry_import_audit_events", ["batch_id"])
    op.create_index("ix_registry_import_audit_events_import_record_id", "registry_import_audit_events", ["import_record_id"])
    op.create_index("ix_registry_import_audit_events_action", "registry_import_audit_events", ["action"])


def downgrade():
    op.drop_index("ix_registry_import_audit_events_action", table_name="registry_import_audit_events")
    op.drop_index("ix_registry_import_audit_events_import_record_id", table_name="registry_import_audit_events")
    op.drop_index("ix_registry_import_audit_events_batch_id", table_name="registry_import_audit_events")
    op.drop_table("registry_import_audit_events")
    op.drop_index("ix_registry_import_candidates_import_record_id", table_name="registry_import_candidates")
    op.drop_table("registry_import_candidates")
    for col in ("status", "entity_type", "batch_id"):
        op.drop_index(f"ix_registry_import_records_{col}", table_name="registry_import_records")
    op.drop_table("registry_import_records")
    op.drop_index("ix_registry_import_batches_status", table_name="registry_import_batches")
    op.drop_index("ix_registry_import_batches_source", table_name="registry_import_batches")
    op.drop_table("registry_import_batches")
