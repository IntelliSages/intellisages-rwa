"""Add evidence-bearing perpetual contract migration history."""
from alembic import op
import sqlalchemy as sa

revision = "0004_perpetual_contract_migrations"
down_revision = "0003_effective_provider_aliases"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "perpetual_contract_migrations",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("predecessor_contract_id", sa.String(length=36), nullable=False),
        sa.Column("successor_contract_id", sa.String(length=36), nullable=True),
        sa.Column("event_type", sa.String(length=30), nullable=False),
        sa.Column("effective_at", sa.Date(), nullable=False),
        sa.Column("previous_native_market_id", sa.String(length=180), nullable=False),
        sa.Column("new_native_market_id", sa.String(length=180), nullable=True),
        sa.Column("previous_native_symbol", sa.String(length=100), nullable=False),
        sa.Column("new_native_symbol", sa.String(length=100), nullable=True),
        sa.Column("source", sa.String(length=120), nullable=False),
        sa.Column("evidence_ref", sa.String(length=500), nullable=False),
        sa.Column("notes", sa.String(length=1000), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(
            ["predecessor_contract_id"], ["perpetual_contracts.id"],
            name="fk_perp_migration_predecessor",
        ),
        sa.ForeignKeyConstraint(
            ["successor_contract_id"], ["perpetual_contracts.id"],
            name="fk_perp_migration_successor",
        ),
        sa.CheckConstraint(
            "successor_contract_id IS NULL OR predecessor_contract_id <> successor_contract_id",
            name="ck_perp_migration_not_self",
        ),
        sa.UniqueConstraint(
            "predecessor_contract_id", "successor_contract_id", "event_type", "effective_at",
            name="uq_perp_migration_edge_event_date",
        ),
    )
    op.create_index(
        "ix_perpetual_contract_migrations_predecessor_contract_id",
        "perpetual_contract_migrations", ["predecessor_contract_id"],
    )
    op.create_index(
        "ix_perpetual_contract_migrations_successor_contract_id",
        "perpetual_contract_migrations", ["successor_contract_id"],
    )


def downgrade():
    op.drop_index(
        "ix_perpetual_contract_migrations_successor_contract_id",
        table_name="perpetual_contract_migrations",
    )
    op.drop_index(
        "ix_perpetual_contract_migrations_predecessor_contract_id",
        table_name="perpetual_contract_migrations",
    )
    op.drop_table("perpetual_contract_migrations")
