"""widen registry_import_candidates.match_basis"""
import sqlalchemy as sa
from alembic import op

revision = "0008_widen_match_basis"
down_revision = "0007_coingecko_rwa_market_data"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("registry_import_candidates") as batch:
        batch.alter_column(
            "match_basis",
            existing_type=sa.String(80),
            type_=sa.String(255),
            existing_nullable=False,
        )


def downgrade():
    with op.batch_alter_table("registry_import_candidates") as batch:
        batch.alter_column(
            "match_basis",
            existing_type=sa.String(255),
            type_=sa.String(80),
            existing_nullable=False,
        )
