"""CoinGecko RWA market snapshots with immutable raw evidence and coverage."""

from __future__ import annotations

import hashlib
import json
import math
import os
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models
from app.providers.coingecko_pilot import CoinGeckoClient

MARKETS_PATH = "rwas/markets"
LIST_PATH = "rwas/list"
PAGE_SIZE = 250


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _rows(payload: Any, endpoint: str) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        values = payload
    elif isinstance(payload, dict) and isinstance(payload.get("data"), list):
        values = payload["data"]
    else:
        raise RuntimeError(f"Unexpected CoinGecko response shape for {endpoint}.")
    return [row for row in values if isinstance(row, dict)]


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if not math.isfinite(float(value)):
        return None
    return float(value)


def _timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed


def normalize_market_row(row: dict[str, Any], retrieved_at: datetime) -> dict[str, Any]:
    market = row.get("tokenized_market_data")
    market = market if isinstance(market, dict) else {}
    return {
        "provider_rwa_id": str(row.get("id") or ""),
        "name": str(row.get("name") or "")[:240],
        "symbol": str(row.get("symbol") or "")[:80],
        "asset_type": str(row.get("asset_type") or "unknown")[:40],
        "current_price_usd": _number(market.get("current_price")),
        "market_cap_usd": _number(market.get("market_cap")),
        "total_volume_24h_usd": _number(market.get("total_volume")),
        "price_change_24h_pct": _number(
            market.get("price_change_percentage_24h_in_currency")
        ),
        "price_change_7d_pct": _number(
            market.get("price_change_percentage_7d_in_currency")
        ),
        "provider_updated_at": _timestamp(
            market.get("last_updated") or row.get("last_updated")
        ),
        "retrieved_at": retrieved_at,
    }


def refresh_coingecko_rwa_market_data(
    db: Session,
    client: CoinGeckoClient | None = None,
    page_size: int = PAGE_SIZE,
) -> dict[str, Any]:
    """Fetch all RWA market pages; persist every raw page and its normalized rows.

    A partial run is retained and explicitly marked partial. It never deletes the
    previous run, and the read API selects observations only from the latest
    non-failed run so old values cannot masquerade as fresh values.
    """
    if not 1 <= page_size <= PAGE_SIZE:
        raise ValueError(f"page_size must be between 1 and {PAGE_SIZE}.")
    api = client or CoinGeckoClient()
    started = _now()
    run = models.ProviderRefreshRun(
        provider="coingecko",
        dataset="rwa-markets",
        status="running",
        started_at=started,
        coverage_json="{}",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    expected_ids: set[str] = set()
    received_ids: set[str] = set()
    duplicate_ids: set[str] = set()
    pages = 0
    errors: list[str] = []
    try:
        list_retrieved = _now()
        list_payload = api.get_json(LIST_PATH)
        list_json = json.dumps(list_payload, sort_keys=True, separators=(",", ":"))
        db.add(models.ProviderRawResponse(
            run_id=run.id,
            provider="coingecko",
            endpoint=LIST_PATH,
            page=0,
            retrieved_at=list_retrieved,
            response_sha256=hashlib.sha256(list_json.encode("utf-8")).hexdigest(),
            response_json=list_json,
            record_count=len(list_payload) if isinstance(list_payload, list) else 0,
        ))
        db.commit()
        listed = _rows(list_payload, LIST_PATH)
        expected_ids = {
            str(item["id"]) for item in listed
            if isinstance(item.get("id"), str) and item["id"].strip()
        }
        if not expected_ids:
            raise RuntimeError("CoinGecko RWA list was empty; refusing zero-coverage refresh.")

        page_count = math.ceil(len(expected_ids) / page_size)
        for page in range(1, page_count + 1):
            endpoint = f"{MARKETS_PATH}?page={page}&per_page={page_size}"
            retrieved = _now()
            payload = api.get_json(
                MARKETS_PATH,
                {
                    "page": str(page),
                    "per_page": str(page_size),
                    "price_change_percentage": "24h,7d",
                },
            )
            rows = _rows(payload, MARKETS_PATH)
            raw_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
            digest = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()
            raw = models.ProviderRawResponse(
                run_id=run.id,
                provider="coingecko",
                endpoint=endpoint,
                page=page,
                retrieved_at=retrieved,
                response_sha256=digest,
                response_json=raw_json,
                record_count=len(rows),
            )
            db.add(raw)
            db.flush()
            pages += 1

            for row in rows:
                provider_id = row.get("id")
                if not isinstance(provider_id, str) or provider_id not in expected_ids:
                    continue
                if provider_id in received_ids:
                    duplicate_ids.add(provider_id)
                    continue
                received_ids.add(provider_id)
                normalized = normalize_market_row(row, retrieved)
                db.add(models.CoinGeckoRwaMarketObservation(
                    run_id=run.id,
                    raw_response_id=raw.id,
                    **normalized,
                ))
            db.commit()
            if len(rows) < page_size:
                break

        missing = sorted(expected_ids - received_ids)
        coverage = {
            "provider": "coingecko",
            "endpoint": MARKETS_PATH,
            "expected_rwa_count": len(expected_ids),
            "received_rwa_count": len(received_ids),
            "missing_rwa_count": len(missing),
            "missing_rwa_ids_sample": missing[:50],
            "duplicate_rwa_count": len(duplicate_ids),
            "pages_requested": pages,
            "scope": "CoinGecko-tracked RWA universe at retrieval time",
            "complete": not missing and not duplicate_ids and pages == page_count,
        }
        run.status = "complete" if coverage["complete"] else "partial"
        run.coverage_json = json.dumps(coverage, sort_keys=True)
    except Exception as exc:
        db.rollback()
        run = db.get(models.ProviderRefreshRun, run.id)
        errors.append(f"{type(exc).__name__}: {str(exc)[:400]}")
        run.status = "partial" if received_ids else "failed"
        run.coverage_json = json.dumps({
            "expected_rwa_count": len(expected_ids),
            "received_rwa_count": len(received_ids),
            "missing_rwa_count": max(0, len(expected_ids) - len(received_ids)),
            "pages_requested": pages,
            "complete": False,
        }, sort_keys=True)
        run.error_summary = "; ".join(errors)[:1000]

    run.completed_at = _now()
    db.commit()
    db.refresh(run)
    return {
        "id": run.id,
        "status": run.status,
        "started_at": run.started_at.isoformat(),
        "completed_at": run.completed_at.isoformat(),
        "coverage": json.loads(run.coverage_json),
        "error": run.error_summary,
    }


def latest_coingecko_run(db: Session) -> models.ProviderRefreshRun | None:
    return db.scalar(
        select(models.ProviderRefreshRun)
        .where(
            models.ProviderRefreshRun.provider == "coingecko",
            models.ProviderRefreshRun.dataset == "rwa-markets",
            models.ProviderRefreshRun.status.in_({"complete", "partial"}),
        )
        .order_by(models.ProviderRefreshRun.started_at.desc())
        .limit(1)
    )


def coingecko_refresh_enabled() -> bool:
    return bool(os.getenv("COINGECKO_API_KEY"))
