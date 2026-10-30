from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models import Base, CoinGeckoRwaMarketObservation, ProviderRawResponse, ProviderRefreshRun
from app.providers.coingecko_market_data import normalize_market_row, refresh_coingecko_rwa_market_data


class FakeCoinGeckoClient:
    def get_json(self, path, params=None):
        if path == "rwas/list":
            return [{"id": "gold"}, {"id": "silver"}, {"id": "amazon"}]
        page = int(params["page"])
        rows = [
            {"id": "gold", "name": "Gold", "symbol": "gold", "asset_type": "commodity",
             "tokenized_market_data": {"current_price": 2300, "market_cap": 1000000,
             "total_volume": 50000, "price_change_percentage_24h_in_currency": 1.2,
             "price_change_percentage_7d_in_currency": 2.4}},
            {"id": "silver", "name": "Silver", "symbol": "xag", "asset_type": "commodity",
             "tokenized_market_data": {"current_price": 30, "market_cap": 200000,
             "total_volume": 10000}},
            {"id": "amazon", "name": "Amazon", "symbol": "amzn", "asset_type": "stock",
             "tokenized_market_data": {"current_price": 190, "market_cap": 3000000,
             "total_volume": 70000}},
        ]
        return rows[:2] if page == 1 else rows[2:]


def test_normalize_market_row_preserves_nulls_and_timestamp():
    retrieved = datetime(2026, 10, 30, tzinfo=timezone.utc)
    row = normalize_market_row({
        "id": "gold",
        "name": "Gold",
        "symbol": "xau",
        "asset_type": "commodity",
        "tokenized_market_data": {
            "current_price": 2300,
            "market_cap": None,
            "total_volume": 0,
            "price_change_percentage_24h_in_currency": 1.5,
            "last_updated": "2026-10-30T10:00:00Z",
        },
    }, retrieved)
    assert row["current_price_usd"] == 2300.0
    assert row["market_cap_usd"] is None
    assert row["total_volume_24h_usd"] == 0.0
    assert row["price_change_24h_pct"] == 1.5
    assert row["provider_updated_at"] == datetime(2026, 10, 30, 10, tzinfo=timezone.utc)


def test_refresh_persists_raw_pages_and_normalized_observations():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        result = refresh_coingecko_rwa_market_data(
            db, client=FakeCoinGeckoClient(), page_size=2
        )
        assert result["status"] == "complete"
        assert result["coverage"]["expected_rwa_count"] == 3
        assert result["coverage"]["received_rwa_count"] == 3
        assert result["coverage"]["complete"] is True
        assert len(db.scalars(select(ProviderRawResponse)).all()) == 2
        observations = db.scalars(select(CoinGeckoRwaMarketObservation)).all()
        assert {row.provider_rwa_id for row in observations} == {"gold", "silver", "amazon"}
        assert len(db.scalars(select(ProviderRefreshRun)).all()) == 1
    Base.metadata.drop_all(engine)


def test_refresh_marks_missing_market_rows_as_partial():
    class PartialClient(FakeCoinGeckoClient):
        def get_json(self, path, params=None):
            if path == "rwas/list":
                return [{"id": "gold"}, {"id": "not-returned"}]
            return [{
                "id": "gold", "name": "Gold", "symbol": "xau",
                "tokenized_market_data": {"current_price": 2300},
            }]

    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        result = refresh_coingecko_rwa_market_data(
            db, client=PartialClient(), page_size=2
        )
        assert result["status"] == "partial"
        assert result["coverage"]["missing_rwa_count"] == 1
        assert result["coverage"]["complete"] is False
    Base.metadata.drop_all(engine)
