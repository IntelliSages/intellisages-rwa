"""Persist CoinGecko RWA market refreshes, raw pages and normalized observations."""

from alembic import op
import sqlalchemy as sa

revision = "0007_coingecko_rwa_market_data"
down_revision = "0006_provider_ingestion_runs"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "provider_refresh_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("provider", sa.String(100), nullable=False),
        sa.Column("dataset", sa.String(120), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("coverage_json", sa.Text(), nullable=False),
        sa.Column("error_summary", sa.String(1000), nullable=True),
    )
    op.create_index("ix_provider_refresh_runs_provider", "provider_refresh_runs", ["provider"])
    op.create_index("ix_provider_refresh_runs_status", "provider_refresh_runs", ["status"])

    op.create_table(
        "provider_raw_responses",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("provider_refresh_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(100), nullable=False),
        sa.Column("endpoint", sa.String(300), nullable=False),
        sa.Column("page", sa.Integer(), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("response_sha256", sa.String(64), nullable=False),
        sa.Column("response_json", sa.Text(), nullable=False),
        sa.Column("record_count", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_provider_raw_responses_run_id", "provider_raw_responses", ["run_id"])
    op.create_index("ix_provider_raw_responses_provider", "provider_raw_responses", ["provider"])

    op.create_table(
        "coingecko_rwa_market_observations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("run_id", sa.String(36), sa.ForeignKey("provider_refresh_runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("raw_response_id", sa.String(36), sa.ForeignKey("provider_raw_responses.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("provider_rwa_id", sa.String(220), nullable=False),
        sa.Column("name", sa.String(240), nullable=False),
        sa.Column("symbol", sa.String(80), nullable=False),
        sa.Column("asset_type", sa.String(40), nullable=False),
        sa.Column("current_price_usd", sa.Float(), nullable=True),
        sa.Column("market_cap_usd", sa.Float(), nullable=True),
        sa.Column("total_volume_24h_usd", sa.Float(), nullable=True),
        sa.Column("price_change_24h_pct", sa.Float(), nullable=True),
        sa.Column("price_change_7d_pct", sa.Float(), nullable=True),
        sa.Column("provider_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("run_id", "provider_rwa_id", name="uq_cg_rwa_observation_run_id"),
    )
    op.create_index("ix_coingecko_rwa_market_observations_run_id", "coingecko_rwa_market_observations", ["run_id"])
    op.create_index("ix_coingecko_rwa_market_observations_provider_rwa_id", "coingecko_rwa_market_observations", ["provider_rwa_id"])
    op.create_index("ix_coingecko_rwa_market_observations_retrieved_at", "coingecko_rwa_market_observations", ["retrieved_at"])


def downgrade():
    op.drop_index("ix_coingecko_rwa_market_observations_retrieved_at", table_name="coingecko_rwa_market_observations")
    op.drop_index("ix_coingecko_rwa_market_observations_provider_rwa_id", table_name="coingecko_rwa_market_observations")
    op.drop_index("ix_coingecko_rwa_market_observations_run_id", table_name="coingecko_rwa_market_observations")
    op.drop_table("coingecko_rwa_market_observations")
    op.drop_index("ix_provider_raw_responses_provider", table_name="provider_raw_responses")
    op.drop_index("ix_provider_raw_responses_run_id", table_name="provider_raw_responses")
    op.drop_table("provider_raw_responses")
    op.drop_index("ix_provider_refresh_runs_status", table_name="provider_refresh_runs")
    op.drop_index("ix_provider_refresh_runs_provider", table_name="provider_refresh_runs")
    op.drop_table("provider_refresh_runs")
