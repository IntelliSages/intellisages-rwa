"""CoinGecko RWA market-data read and controlled refresh endpoints."""

import hmac
import json
import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.providers.coingecko_market_data import (
    latest_coingecko_run,
    refresh_coingecko_rwa_market_data,
)

router = APIRouter(prefix="/api/v1/market-data/coingecko", tags=["provider market data"])


def _freshness(observed_at: datetime | None, retrieved_at: datetime) -> str:
    now = datetime.now(timezone.utc)
    stamp = observed_at or retrieved_at
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    return "stale" if now - stamp > timedelta(minutes=15) else "available"


def _read_observation(row: models.CoinGeckoRwaMarketObservation) -> dict:
    return {
        "provider_rwa_id": row.provider_rwa_id,
        "name": row.name,
        "symbol": row.symbol,
        "asset_type": row.asset_type,
        "current_price_usd": row.current_price_usd,
        "market_cap_usd": row.market_cap_usd,
        "total_volume_24h_usd": row.total_volume_24h_usd,
        "price_change_24h_pct": row.price_change_24h_pct,
        "price_change_7d_pct": row.price_change_7d_pct,
        "provider_updated_at": row.provider_updated_at.isoformat() if row.provider_updated_at else None,
        "retrieved_at": row.retrieved_at.isoformat(),
        "freshness": _freshness(row.provider_updated_at, row.retrieved_at),
        "source": "CoinGecko RWA Markets API",
        "scope": "aggregated tokenized underlying market; not issuer-product or underlying spot-market data",
    }


@router.get("/rwa/latest")
def get_latest_rwa_market_data(db: Session = Depends(get_db)):
    run = latest_coingecko_run(db)
    if run is None:
        return {
            "provider": "coingecko",
            "status": "unavailable",
            "reason": "no_successful_refresh",
            "run": None,
            "coverage": {"status": "unknown", "complete": False},
            "items": [],
        }
    rows = db.scalars(
        select(models.CoinGeckoRwaMarketObservation)
        .where(models.CoinGeckoRwaMarketObservation.run_id == run.id)
        .order_by(models.CoinGeckoRwaMarketObservation.name)
    ).all()
    return {
        "provider": "coingecko",
        "status": run.status,
        "run": {
            "id": run.id,
            "started_at": run.started_at.isoformat(),
            "completed_at": run.completed_at.isoformat() if run.completed_at else None,
        },
        "coverage": json.loads(run.coverage_json),
        "items": [_read_observation(row) for row in rows],
    }


@router.get("/rwa/verified-underlyings")
def get_verified_underlying_market_data(db: Session = Depends(get_db)):
    """Return aggregate RWA metrics only for independently verified provider aliases."""
    run = latest_coingecko_run(db)
    if run is None:
        return {"status": "unavailable", "reason": "no_successful_refresh", "items": []}
    rows = db.execute(
        select(models.ProviderAlias, models.CoinGeckoRwaMarketObservation)
        .join(
            models.CoinGeckoRwaMarketObservation,
            models.CoinGeckoRwaMarketObservation.provider_rwa_id
            == models.ProviderAlias.external_id,
        )
        .where(
            models.ProviderAlias.provider == "coingecko",
            models.ProviderAlias.namespace == "rwa_id",
            models.ProviderAlias.entity_type == "underlying",
            models.ProviderAlias.is_verified.is_(True),
            models.CoinGeckoRwaMarketObservation.run_id == run.id,
        )
    ).all()
    return {
        "status": run.status,
        "run_id": run.id,
        "coverage": json.loads(run.coverage_json),
        "items": [
            {"underlying_id": alias.entity_id, **_read_observation(observation)}
            for alias, observation in rows
            if db.get(models.UnderlyingAsset, alias.entity_id) is not None
        ],
    }


@router.post("/rwa/refresh", status_code=202)
def refresh_rwa_market_data(
    x_coingecko_refresh_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    expected = os.getenv("COINGECKO_REFRESH_ADMIN_TOKEN")
    if not expected:
        raise HTTPException(status_code=503, detail="Controlled provider refresh is not configured.")
    if x_coingecko_refresh_token is None or not hmac.compare_digest(
        x_coingecko_refresh_token, expected
    ):
        raise HTTPException(status_code=401, detail="A valid provider refresh token is required.")
    if not os.getenv("COINGECKO_API_KEY"):
        raise HTTPException(status_code=503, detail="CoinGecko API credentials are not configured.")
    result = refresh_coingecko_rwa_market_data(db)
    return result
