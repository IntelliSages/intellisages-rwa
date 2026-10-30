"""Add effective-dated provider alias history."""
from alembic import op
import sqlalchemy as sa

revision = "0003_effective_provider_aliases"
down_revision = "0002_supply_classification"
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table("provider_aliases", recreate="always") as batch_op:
        batch_op.add_column(sa.Column("effective_from", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("effective_to", sa.Date(), nullable=True))
        batch_op.drop_constraint("uq_provider_alias_external", type_="unique")
        batch_op.create_unique_constraint(
            "uq_provider_alias_external_start",
            ["provider", "namespace", "external_id", "effective_from"],
        )

def downgrade():
    with op.batch_alter_table("provider_aliases", recreate="always") as batch_op:
        batch_op.drop_constraint("uq_provider_alias_external_start", type_="unique")
        batch_op.drop_column("effective_to")
        batch_op.drop_column("effective_from")
        batch_op.create_unique_constraint(
            "uq_provider_alias_external",
            ["provider", "namespace", "external_id"],
        )
