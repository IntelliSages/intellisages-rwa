"""Resumable CoinGecko RWA discovery and staged registry import.

This module never writes canonical entities directly. It only stages source records
for the existing evidence-led human review workflow.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urljoin
from urllib.request import Request, urlopen

PROVIDER = "coingecko"
DATASET = "tokenized-rwa-catalogue"
RWA_LIST_PATH = "rwas/list"
ISSUER_LIST_PATH = "rwas/issuers/list"
RWA_DETAIL_PATH = "rwas/{rwa_id}"
MAX_BATCH_RECORDS = 400
UNIT_DESCRIPTION = (
    "Provider-reported token unit; legal/economic entitlement and conversion ratio "
    "have not been established by this import."
)

# Explicit chain identity mappings only. Unknown CoinGecko platform slugs are left
# unresolved and must be mapped by an operator; no chain IDs are inferred.
DEFAULT_NETWORK_MAP: dict[str, dict[str, str]] = {
    "ethereum": {"namespace": "eip155:1", "display_name": "Ethereum", "family": "evm"},
    "binance-smart-chain": {"namespace": "eip155:56", "display_name": "BNB Smart Chain", "family": "evm"},
    "polygon-pos": {"namespace": "eip155:137", "display_name": "Polygon PoS", "family": "evm"},
    "arbitrum-one": {"namespace": "eip155:42161", "display_name": "Arbitrum One", "family": "evm"},
    "base": {"namespace": "eip155:8453", "display_name": "Base", "family": "evm"},
    "optimistic-ethereum": {"namespace": "eip155:10", "display_name": "Optimism", "family": "evm"},
    "avalanche": {"namespace": "eip155:43114", "display_name": "Avalanche C-Chain", "family": "evm"},
    "solana": {
        "namespace": "solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp",
        "display_name": "Solana",
        "family": "solana",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def safe_slug(value: str, max_length: int = 110) -> str:
    slug = re.sub(r"[^a-z0-9._-]+", "-", value.strip().lower()).strip("-._")
    if not slug:
        slug = sha256_bytes(value.encode("utf-8"))[:16]
    if len(slug) > max_length:
        suffix = sha256_bytes(value.encode("utf-8"))[:12]
        slug = f"{slug[:max_length - 13]}-{suffix}"
    return slug


def source_key(kind: str, provider_id: str) -> str:
    slug = safe_slug(provider_id, 105)
    suffix = sha256_bytes(provider_id.encode("utf-8"))[:10]
    return f"coingecko:{kind}:{slug}-{suffix}"


def envelope(canonical_payload: dict[str, Any], source_payload: Any,
             source_metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "canonical_payload": canonical_payload,
        "source_payload": source_payload,
        "source_metadata": source_metadata,
    }


def _detail_file_name(rwa_id: str) -> str:
    return f"{safe_slug(rwa_id, 120)}-{sha256_bytes(rwa_id.encode('utf-8'))[:10]}.json"


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(canonical_json(value) + b"\n")
    temporary.replace(path)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


class CoinGeckoClient:
    def __init__(self, api_key: str | None = None, base_url: str | None = None,
                 min_interval: float = 2.1, timeout: float = 30.0, max_retries: int = 5):
        self.api_key = api_key or os.getenv("COINGECKO_API_KEY")
        if not self.api_key:
            raise RuntimeError("COINGECKO_API_KEY is required. Configure it locally; do not commit or paste it into source files.")
        self.base_url = (base_url or os.getenv(
            "COINGECKO_BASE_URL", "https://api.coingecko.com/api/v3"
        )).rstrip("/") + "/"
        self.min_interval = max(0.0, min_interval)
        self.timeout = timeout
        self.max_retries = max(0, max_retries)
        self._last_request = 0.0
        self.key_header = "x-cg-pro-api-key" if "pro-api.coingecko.com" in self.base_url else "x-cg-demo-api-key"

    def get_json(self, path: str, params: dict[str, str] | None = None) -> Any:
        url = urljoin(self.base_url, path.lstrip("/"))
        if params:
            url = f"{url}?{urlencode(params)}"
        headers = {"accept": "application/json", self.key_header: self.api_key or ""}
        for attempt in range(self.max_retries + 1):
            wait = self.min_interval - (time.monotonic() - self._last_request)
            if wait > 0:
                time.sleep(wait)
            request = Request(url, headers=headers, method="GET")
            self._last_request = time.monotonic()
            try:
                with urlopen(request, timeout=self.timeout) as response:
                    raw = response.read(5_000_001)
                if len(raw) > 5_000_000:
                    raise RuntimeError(f"CoinGecko response exceeded the 5 MB safety limit for {path}")
                return json.loads(raw.decode("utf-8"))
            except HTTPError as exc:
                if exc.code not in {429, 500, 502, 503, 504} or attempt >= self.max_retries:
                    # Never include request headers or the API key in raised errors.
                    raise RuntimeError(f"CoinGecko request failed: HTTP {exc.code} for {path}") from None
                retry_after = exc.headers.get("Retry-After")
                try:
                    delay = float(retry_after) if retry_after else min(60.0, 2.0 ** attempt)
                except ValueError:
                    delay = min(60.0, 2.0 ** attempt)
                time.sleep(max(0.5, delay))
            except (URLError, TimeoutError, json.JSONDecodeError) as exc:
                if attempt >= self.max_retries:
                    raise RuntimeError(f"CoinGecko request failed for {path}: {type(exc).__name__}") from None
                time.sleep(min(30.0, 2.0 ** attempt))
        raise RuntimeError(f"CoinGecko request exhausted retries for {path}")


def _list_payload(payload: Any, endpoint: str) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict) and isinstance(payload.get("data"), list):
        rows = payload["data"]
    else:
        raise RuntimeError(f"Unexpected response shape from CoinGecko {endpoint}; expected a list.")
    return [row for row in rows if isinstance(row, dict)]


def snapshot_digest(manifest: dict[str, Any]) -> str:
    stable = {
        "provider": manifest.get("provider"),
        "dataset": manifest.get("dataset"),
        "retrieved_at": manifest.get("retrieved_at"),
        "rwa_list_retrieved_at": manifest.get("rwa_list_retrieved_at"),
        "issuer_list_retrieved_at": manifest.get("issuer_list_retrieved_at"),
        "detail_retrieved_at": manifest.get("detail_retrieved_at", {}),
        "expected_rwa_count": manifest.get("expected_rwa_count"),
        "requested_rwa_count": manifest.get("requested_rwa_count"),
        "details_succeeded": manifest.get("details_succeeded"),
        "details_failed": manifest.get("details_failed"),
        "files": manifest.get("files", {}),
    }
    return sha256_bytes(canonical_json(stable))


def fetch_snapshot(output_dir: Path, client: CoinGeckoClient, limit: int | None = None,
                   refresh_details: bool = False) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    detail_dir = output_dir / "details"
    detail_dir.mkdir(parents=True, exist_ok=True)

    rwa_list = _list_payload(client.get_json(RWA_LIST_PATH), RWA_LIST_PATH)
    rwa_list_retrieved_at = utc_now()
    if not rwa_list:
        raise RuntimeError("CoinGecko returned an empty RWA list; refusing to create a zero-coverage snapshot.")
    if limit is not None and limit < 1:
        raise ValueError("--limit must be a positive integer.")
    _write_json(output_dir / "rwas-list.json", rwa_list)
    list_hash = sha256_bytes((output_dir / "rwas-list.json").read_bytes())

    issuer_rows: list[dict[str, Any]] = []
    issuer_list_path = output_dir / "issuers-list.json"
    if issuer_list_path.exists():
        issuer_list_path.unlink()
    issuer_list_error = None
    issuer_list_retrieved_at = None
    try:
        issuer_rows = _list_payload(client.get_json(ISSUER_LIST_PATH), ISSUER_LIST_PATH)
        issuer_list_retrieved_at = utc_now()
        _write_json(output_dir / "issuers-list.json", issuer_rows)
    except Exception as exc:  # optional corroborating endpoint; token issuer_details remains primary
        issuer_list_error = str(exc)[:500]

    selected = rwa_list[:limit] if limit else rwa_list
    prior_manifest_path = output_dir / "manifest.json"
    prior = _read_json(prior_manifest_path) if prior_manifest_path.exists() else {}
    can_resume = (
        prior.get("rwa_list_sha256") == list_hash
        and prior.get("requested_rwa_count") == len(selected)
        and not refresh_details
        and bool(prior.get("retrieved_at"))
    )
    if prior.get("staged_phases"):
        raise RuntimeError("A snapshot becomes immutable once an import phase is staged. Use a new output directory for a new source snapshot.")
    if not can_resume:
        for stale in detail_dir.glob("*.json"):
            stale.unlink()
    detail_errors: list[dict[str, str]] = []
    detail_retrieved_at: dict[str, str] = dict(prior.get("detail_retrieved_at", {})) if can_resume else {}
    details_succeeded = 0
    for index, item in enumerate(selected, start=1):
        rwa_id = item.get("id")
        if not isinstance(rwa_id, str) or not rwa_id.strip():
            detail_errors.append({"rwa_id": f"row-{index}", "error": "missing provider RWA id"})
            continue
        target = detail_dir / _detail_file_name(rwa_id)
        if can_resume and target.exists():
            detail_retrieved_at.setdefault(rwa_id, prior.get("retrieved_at") or rwa_list_retrieved_at)
            details_succeeded += 1
            continue
        try:
            detail = client.get_json(
                RWA_DETAIL_PATH.format(rwa_id=quote(rwa_id, safe="")),
                {"tokens": "true", "tokenized_market_data": "true"},
            )
            if not isinstance(detail, dict) or detail.get("id") != rwa_id:
                raise RuntimeError("detail response ID did not match requested RWA ID")
            if not isinstance(detail.get("tokens"), list):
                raise RuntimeError("detail response omitted the requested tokens array")
            _write_json(target, detail)
            detail_retrieved_at[rwa_id] = utc_now()
            details_succeeded += 1
        except Exception as exc:
            detail_errors.append({"rwa_id": rwa_id, "error": str(exc)[:500]})
        # A compact checkpoint is written after every record so long snapshots resume safely.
        _write_json(output_dir / "snapshot-progress.json", {
            "rwa_list_sha256": list_hash, "processed": index,
            "details_succeeded": details_succeeded, "details_failed": len(detail_errors),
            "updated_at": utc_now(),
        })

    files: dict[str, str] = {}
    for path in [output_dir / "rwas-list.json", output_dir / "issuers-list.json", *sorted(detail_dir.glob("*.json"))]:
        if path.exists():
            files[str(path.relative_to(output_dir))] = sha256_bytes(path.read_bytes())
    retrieved_at = prior.get("retrieved_at") if can_resume else utc_now()
    manifest = {
        "provider": PROVIDER,
        "dataset": DATASET,
        "retrieved_at": retrieved_at,
        "rwa_list_retrieved_at": rwa_list_retrieved_at,
        "issuer_list_retrieved_at": issuer_list_retrieved_at,
        "detail_retrieved_at": detail_retrieved_at,
        "source_base_url": client.base_url,
        "rwa_list_sha256": list_hash,
        "expected_rwa_count": len(rwa_list),
        "requested_rwa_count": len(selected),
        "is_full_provider_list": len(selected) == len(rwa_list),
        "details_succeeded": details_succeeded,
        "details_failed": len(detail_errors),
        "detail_errors": detail_errors,
        "issuer_list_count": len(issuer_rows),
        "issuer_list_available": issuer_list_error is None,
        "issuer_list_error": issuer_list_error,
        "files": files,
        "provider_universe_scope": "CoinGecko-tracked RWA list at retrieval time; not the complete global tokenized-asset universe.",
        "run_id": prior.get("run_id"),
        "staged_phases": prior.get("staged_phases", {}),
        "staged_batch_ids": prior.get("staged_batch_ids", []),
    }
    manifest["manifest_sha256"] = snapshot_digest(manifest)
    _write_json(output_dir / "manifest.json", manifest)
    _write_json(output_dir / "coverage.json", build_coverage(output_dir, manifest))
    return manifest


def load_snapshot(output_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, dict[str, Any]]]:
    manifest = _read_json(output_dir / "manifest.json")
    rwa_list = _read_json(output_dir / "rwas-list.json")
    details: dict[str, dict[str, Any]] = {}
    for item in rwa_list[:manifest.get("requested_rwa_count", len(rwa_list))]:
        rwa_id = item.get("id")
        if not isinstance(rwa_id, str):
            continue
        path = output_dir / "details" / _detail_file_name(rwa_id)
        if path.exists():
            details[rwa_id] = _read_json(path)
    return manifest, rwa_list, details


def extract_tokens(details: dict[str, dict[str, Any]]) -> list[tuple[str, dict[str, Any], dict[str, Any]]]:
    output = []
    for rwa_id, detail in details.items():
        tokens = detail.get("tokens")
        if not isinstance(tokens, list):
            continue
        for token in tokens:
            if isinstance(token, dict):
                output.append((rwa_id, detail, token))
    return output


def _asset_type(value: Any) -> str:
    return {"stock": "equity", "commodity": "commodity", "etf": "fund"}.get(
        str(value).lower(), "other"
    )


def _instrument_form(value: Any) -> str:
    return {"stock": "tokenized_stock", "commodity": "tokenized_commodity", "etf": "tokenized_etf"}.get(
        str(value).lower(), "tokenized_rwa"
    )


def _active_alias_map(aliases: list[dict[str, Any]], namespace: str,
                      entity_type: str) -> dict[str, str]:
    today = date.today()
    grouped: dict[str, list[dict[str, Any]]] = {}
    for alias in aliases:
        if alias.get("provider") != PROVIDER or alias.get("namespace") != namespace:
            continue
        if alias.get("entity_type") != entity_type or alias.get("is_verified") is not True:
            continue
        start = alias.get("effective_from")
        end = alias.get("effective_to")
        if start and date.fromisoformat(start) > today:
            continue
        if end and date.fromisoformat(end) <= today:
            continue
        grouped.setdefault(alias.get("external_id", ""), []).append(alias)
    result = {}
    for external_id, rows in grouped.items():
        entity_ids = {row.get("entity_id") for row in rows}
        if len(entity_ids) == 1 and None not in entity_ids:
            result[external_id] = next(iter(entity_ids))
    return result


def _metadata(endpoint: str, retrieved_at: str, source_id: str,
              source_hash: str, **extra: Any) -> dict[str, Any]:
    return {
        "provider": PROVIDER, "endpoint": endpoint, "source_record_id": source_id,
        "retrieved_at": retrieved_at, "source_sha256": source_hash, **extra,
    }


def build_foundation_rows(output_dir: Path, manifest: dict[str, Any],
                          rwa_list: list[dict[str, Any]],
                          details: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    rows: list[dict[str, Any]] = []
    issuer_sources: dict[str, tuple[str, dict[str, Any], str | None]] = {}
    counters = {"underlyings": 0, "issuers": 0, "missing_underlying_name": 0,
                "tokens_without_issuer": 0, "underlying_id_out_of_range": 0,
                "issuer_id_out_of_range": 0, "issuer_without_name": 0}
    retrieved_at = manifest["retrieved_at"]
    for item in rwa_list[:manifest.get("requested_rwa_count", len(rwa_list))]:
        rwa_id = item.get("id")
        if not isinstance(rwa_id, str) or not rwa_id or len(rwa_id) > 220:
            counters["underlying_id_out_of_range"] += 1
            continue
        detail = details.get(rwa_id)
        if not detail:
            continue
        name = detail.get("name") or item.get("name")
        if not isinstance(name, str) or not name.strip():
            counters["missing_underlying_name"] += 1
            continue
        source_path = output_dir / "details" / _detail_file_name(rwa_id)
        raw_hash = sha256_bytes(source_path.read_bytes())
        canonical = {
            "canonical_key": source_key("rwa", rwa_id),
            "display_name": name.strip()[:240],
            "asset_type": _asset_type(detail.get("asset_type") or item.get("asset_type")),
        }
        rows.append({
            "entity_type": "underlying", "source_namespace": "rwa_id", "external_id": rwa_id,
            "payload": envelope(canonical, item, _metadata(
                f"/rwas/{quote(rwa_id, safe='')}?tokens=true&tokenized_market_data=true",
                manifest.get("detail_retrieved_at", {}).get(rwa_id, retrieved_at), rwa_id, raw_hash,
                discovery_endpoint="/rwas/list",
                discovery_retrieved_at=manifest.get("rwa_list_retrieved_at"),
            )),
        })
        counters["underlyings"] += 1
        for token in detail.get("tokens", []) if isinstance(detail.get("tokens"), list) else []:
            issuer = token.get("issuer_details") if isinstance(token, dict) else None
            if not isinstance(issuer, dict) or not isinstance(issuer.get("id"), str) or not issuer.get("id") or not isinstance(issuer.get("name"), str) or not issuer.get("name").strip():
                counters["tokens_without_issuer"] += 1
                continue
            issuer_id = issuer["id"]
            if len(issuer_id) > 220:
                counters["issuer_id_out_of_range"] += 1
                continue
            issuer_sources.setdefault(issuer_id, (issuer["name"].strip()[:240], issuer, rwa_id))
    issuer_list_path = output_dir / "issuers-list.json"
    issuer_list_rows = _read_json(issuer_list_path) if issuer_list_path.exists() else []
    for issuer_row in issuer_list_rows if isinstance(issuer_list_rows, list) else []:
        if not isinstance(issuer_row, dict) or not isinstance(issuer_row.get("id"), str) or not issuer_row.get("id") or not isinstance(issuer_row.get("name"), str) or not issuer_row.get("name").strip():
            counters["issuer_without_name"] += 1
            continue
        issuer_id = issuer_row["id"]
        if len(issuer_id) > 220:
            counters["issuer_id_out_of_range"] += 1
        else:
            issuer_sources.setdefault(issuer_id, (issuer_row["name"].strip()[:240], issuer_row, None))
    for issuer_id, (issuer_name, raw_issuer, source_rwa_id) in sorted(issuer_sources.items()):
        canonical = {
            "canonical_key": source_key("issuer", issuer_id),
            # This is a provider-reported issuer label, not proof of the legal entity's registered name.
            "legal_name": issuer_name.strip()[:240],
        }
        rows.append({
            "entity_type": "issuer", "source_namespace": "issuer_id", "external_id": issuer_id,
            "payload": envelope(canonical, raw_issuer, _metadata(
                "/rwas/issuers/list" if source_rwa_id is None else f"/rwas/{quote(source_rwa_id, safe='')}?tokens=true&tokenized_market_data=true",
                manifest.get("issuer_list_retrieved_at") if source_rwa_id is None else
                manifest.get("detail_retrieved_at", {}).get(source_rwa_id, retrieved_at), issuer_id,
                sha256_bytes(canonical_json(raw_issuer)) if source_rwa_id is None else
                sha256_bytes((output_dir / "details" / _detail_file_name(source_rwa_id)).read_bytes()),
                name_semantics="CoinGecko-reported issuer label; legal identity requires independent review.",
                observed_underlying_rwa_id=source_rwa_id,
            )),
        })
        counters["issuers"] += 1
    return rows, counters


def build_network_rows(output_dir: Path, manifest: dict[str, Any],
                       details: dict[str, dict[str, Any]],
                       network_map: dict[str, dict[str, str]] | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    mapping = dict(DEFAULT_NETWORK_MAP)
    if network_map:
        mapping.update(network_map)
    slugs: set[str] = set()
    tokens_without_platforms = 0
    for detail in details.values():
        for token in detail.get("tokens", []) if isinstance(detail.get("tokens"), list) else []:
            platforms = token.get("platforms") if isinstance(token, dict) else None
            if isinstance(platforms, dict) and platforms:
                slugs.update(str(k) for k, v in platforms.items() if isinstance(v, str) and v.strip())
            else:
                tokens_without_platforms += 1
    rows = []
    unknown = []
    platform_evidence: dict[str, list[dict[str, Any]]] = {slug: [] for slug in slugs}
    for rwa_id, detail in details.items():
        for token in detail.get("tokens", []) if isinstance(detail.get("tokens"), list) else []:
            platforms = token.get("platforms") if isinstance(token, dict) else None
            if not isinstance(platforms, dict):
                continue
            for slug, address in platforms.items():
                if isinstance(address, str) and address.strip():
                    platform_evidence.setdefault(slug, []).append({
                        "rwa_id": rwa_id, "token_id": token.get("id"), "address": address,
                    })
    for slug in sorted(slugs):
        config = mapping.get(slug)
        if not config:
            unknown.append(slug)
            continue
        canonical = {
            "namespace": config["namespace"], "display_name": config["display_name"],
            "family": config["family"],
        }
        rows.append({
            "entity_type": "network", "source_namespace": "platform_slug", "external_id": slug,
            "payload": envelope(canonical, {"platform_slug": slug, **config}, _metadata(
                "/rwas/{id}?tokens=true&tokenized_market_data=true&tokenized_market_data=true", manifest["retrieved_at"], slug,
                sha256_bytes(canonical_json(platform_evidence.get(slug, []))),
                mapping_basis="explicit CoinGecko platform-to-CAIP-2 mapping",
                source_rwa_ids=sorted({item["rwa_id"] for item in platform_evidence.get(slug, [])}),
                source_retrieved_at_by_rwa={
                    rwa_id: manifest.get("detail_retrieved_at", {}).get(rwa_id, manifest["retrieved_at"])
                    for rwa_id in sorted({item["rwa_id"] for item in platform_evidence.get(slug, [])})
                },
            )),
        })
    return rows, {"platform_slugs_discovered": len(slugs), "supported_platform_slugs": len(rows),
                  "unsupported_platform_slugs": unknown, "tokens_without_platforms": tokens_without_platforms}


def build_product_rows(manifest: dict[str, Any], details: dict[str, dict[str, Any]],
                       aliases: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    underlying_map = _active_alias_map(aliases, "rwa_id", "underlying")
    issuer_map = _active_alias_map(aliases, "issuer_id", "issuer")
    rows = []
    token_id_counts: dict[str, int] = {}
    for _, _, token in extract_tokens(details):
        if isinstance(token.get("id"), str):
            token_id_counts[token["id"]] = token_id_counts.get(token["id"], 0) + 1
    duplicate_token_ids = {key for key, count in token_id_counts.items() if count > 1}
    counters = {"tokens_discovered": 0, "products_stageable": 0,
                "duplicate_token_ids": len(duplicate_token_ids),
                "unresolved_underlying_alias": 0, "unresolved_issuer_alias": 0,
                "tokens_without_provider_id": 0, "tokens_without_issuer": 0}
    for rwa_id, detail, token in extract_tokens(details):
        counters["tokens_discovered"] += 1
        token_id = token.get("id")
        issuer = token.get("issuer_details") if isinstance(token.get("issuer_details"), dict) else {}
        issuer_id = issuer.get("id")
        if not isinstance(token_id, str) or not token_id or len(token_id) > 180:
            counters["tokens_without_provider_id"] += 1
            continue
        if token_id in duplicate_token_ids:
            continue
        if not isinstance(issuer_id, str) or not issuer_id:
            counters["tokens_without_issuer"] += 1
            continue
        underlying_id = underlying_map.get(rwa_id)
        issuer_canonical_id = issuer_map.get(issuer_id)
        if not underlying_id:
            counters["unresolved_underlying_alias"] += 1
        if not issuer_canonical_id:
            counters["unresolved_issuer_alias"] += 1
        if not underlying_id or not issuer_canonical_id:
            continue
        source_hash = sha256_bytes(canonical_json(token))
        canonical = {
            "canonical_key": source_key("token", token_id),
            "issuer_id": issuer_canonical_id,
            "underlying_id": underlying_id,
            "native_product_id": token_id,
            "display_name": str(token.get("name") or token_id)[:240],
            "symbol": str(token["symbol"])[:80] if token.get("symbol") is not None else None,
            "instrument_form": _instrument_form(detail.get("asset_type")),
            "unit_description": UNIT_DESCRIPTION,
            "representation_type": "unknown",
        }
        rows.append({
            "entity_type": "issuer_product", "source_namespace": "rwa_token_id",
            "external_id": token_id,
            "payload": envelope(canonical, token, _metadata(
                f"/rwas/{quote(rwa_id, safe='')}?tokens=true&tokenized_market_data=true", manifest["retrieved_at"],
                token_id, source_hash, underlying_rwa_id=rwa_id,
                source_retrieved_at=manifest.get("detail_retrieved_at", {}).get(rwa_id, manifest["retrieved_at"]),
                issuer_id=issuer_id, issuer_name=issuer.get("name"),
                native_product_id_semantics="CoinGecko RWA token ID used as a provisional provider-native identifier; not asserted to be the issuer's internal product ID.",
            )),
        })
        counters["products_stageable"] += 1
    return rows, counters


def build_deployment_rows(manifest: dict[str, Any], details: dict[str, dict[str, Any]],
                          aliases: list[dict[str, Any]],
                          network_map: dict[str, dict[str, str]] | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    mapping = dict(DEFAULT_NETWORK_MAP)
    if network_map:
        mapping.update(network_map)
    product_map = _active_alias_map(aliases, "rwa_token_id", "issuer_product")
    network_alias_map = _active_alias_map(aliases, "platform_slug", "network")
    rows = []
    token_id_counts: dict[str, int] = {}
    for _, _, token in extract_tokens(details):
        if isinstance(token.get("id"), str):
            token_id_counts[token["id"]] = token_id_counts.get(token["id"], 0) + 1
    duplicate_token_ids = {key for key, count in token_id_counts.items() if count > 1}
    counters = {"platform_entries": 0, "deployments_stageable": 0,
                "duplicate_token_ids": len(duplicate_token_ids), "tokens_without_platforms": 0,
                "unresolved_product_alias": 0, "unresolved_network_alias": 0,
                "unsupported_platform_slugs": set(), "invalid_platform_addresses": 0}
    for rwa_id, detail, token in extract_tokens(details):
        token_id = token.get("id")
        if not isinstance(token_id, str) or not token_id or token_id in duplicate_token_ids:
            continue
        product_id = product_map.get(token_id)
        platforms = token.get("platforms") if isinstance(token.get("platforms"), dict) else {}
        if not platforms:
            counters["tokens_without_platforms"] += 1
        for slug, address in platforms.items():
            if not isinstance(address, str) or not address.strip() or len(address) > 220:
                counters["invalid_platform_addresses"] += 1
                continue
            if mapping.get(slug, {}).get("family") == "evm" and not re.fullmatch(r"0x[a-fA-F0-9]{40}", address):
                counters["invalid_platform_addresses"] += 1
                continue
            counters["platform_entries"] += 1
            if slug not in mapping:
                counters["unsupported_platform_slugs"].add(slug)
                continue
            network_id = network_alias_map.get(slug)
            if not network_id:
                counters["unresolved_network_alias"] += 1
                continue
            if not product_id:
                counters["unresolved_product_alias"] += 1
                continue
            external_id = f"{token_id}:{slug}:{address}"
            if len(external_id) > 220:
                external_id = f"{token_id[:80]}:{slug[:40]}:{sha256_bytes(external_id.encode())[:32]}"
            canonical = {
                "issuer_product_id": product_id, "network_id": network_id,
                "native_identifier": address, "representation_type": "unknown",
                "is_verified": False,
            }
            rows.append({
                "entity_type": "deployment", "source_namespace": "rwa_token_platform",
                "external_id": external_id,
                "payload": envelope(canonical, {"token_id": token_id, "platform_slug": slug,
                    "native_identifier": address}, _metadata(
                    f"/rwas/{quote(rwa_id, safe='')}?tokens=true&tokenized_market_data=true", manifest["retrieved_at"],
                    external_id, sha256_bytes(canonical_json({"token_id": token_id, "platform": slug, "address": address})),
                    underlying_rwa_id=rwa_id,
                    source_retrieved_at=manifest.get("detail_retrieved_at", {}).get(rwa_id, manifest["retrieved_at"]),
                )),
            })
            counters["deployments_stageable"] += 1
    counters["unsupported_platform_slugs"] = sorted(counters["unsupported_platform_slugs"])
    return rows, counters


def build_coverage(output_dir: Path, manifest: dict[str, Any],
                   extra: dict[str, Any] | None = None) -> dict[str, Any]:
    _, rwa_list, details = load_snapshot(output_dir) if (output_dir / "manifest.json").exists() else (manifest, [], {})
    token_rows = extract_tokens(details)
    issuer_list_path = output_dir / "issuers-list.json"
    issuer_list = _read_json(issuer_list_path) if issuer_list_path.exists() else []
    issuer_list_ids = {item.get("id") for item in issuer_list if isinstance(item, dict) and item.get("id")}
    issuer_ids = set()
    platform_pairs = set()
    tokens_missing_issuer = 0
    for _, _, token in token_rows:
        issuer = token.get("issuer_details")
        if isinstance(issuer, dict) and issuer.get("id"):
            issuer_ids.add(issuer["id"])
        else:
            tokens_missing_issuer += 1
        platforms = token.get("platforms")
        if isinstance(platforms, dict):
            for slug, address in platforms.items():
                if isinstance(address, str) and address.strip():
                    platform_pairs.add((token.get("id"), slug, address))
    coverage = {
        "provider": PROVIDER,
        "dataset": DATASET,
        "scope": manifest.get("provider_universe_scope"),
        "snapshot_retrieved_at": manifest.get("retrieved_at"),
        "rwa_list_retrieved_at": manifest.get("rwa_list_retrieved_at"),
        "issuer_list_retrieved_at": manifest.get("issuer_list_retrieved_at"),
        "detail_retrieved_at_count": len(manifest.get("detail_retrieved_at", {})),
        "provider_rwa_list_count": manifest.get("expected_rwa_count", 0),
        "requested_rwa_count": manifest.get("requested_rwa_count", 0),
        "full_provider_list_requested": manifest.get("is_full_provider_list", False),
        "detail_success_count": len(details),
        "detail_failure_count": manifest.get("details_failed", 0),
        "detail_error_ids": [item.get("rwa_id") for item in manifest.get("detail_errors", [])],
        "detail_coverage_ratio": round(len(details) / max(1, manifest.get("requested_rwa_count", 0)), 4),
        "tokens_discovered": len(token_rows),
        "distinct_issuer_ids_in_token_details": len(issuer_ids),
        "distinct_issuer_ids_in_issuer_list": len(issuer_list_ids),
        "issuer_list_available": issuer_list_path.exists(),
        "issuer_list_error": manifest.get("issuer_list_error"),
        "issuer_ids_only_in_issuer_list": len(issuer_list_ids - issuer_ids),
        "issuer_ids_only_in_token_details": len(issuer_ids - issuer_list_ids),
        "tokens_without_issuer_id": tokens_missing_issuer,
        "tokens_without_platforms": sum(
            1 for _, _, token in token_rows
            if not isinstance(token.get("platforms"), dict) or not token.get("platforms")
        ),
        "provider_platform_contract_entries": len(platform_pairs),
        "unsupported_platform_slugs": [],
        "staged_phases": sorted(manifest.get("staged_phases", {}).keys()),
        "staged_batch_count": len(manifest.get("staged_batch_ids", [])),
        "coverage_warning": (
            "This measures CoinGecko's tracked RWA catalogue only. It is not proof of complete market coverage, "
            "legal issuer identity, underlying ownership, token backing, or verified deployment status."
        ),
    }
    if extra:
        coverage.update(extra)
    return coverage


def chunk_import_rows(rows: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    """Chunk import rows under both the API row-count and serialized-payload limits."""
    chunks: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    current_bytes = 2
    for row in rows:
        row_bytes = len(canonical_json(row)) + 1
        if row_bytes > 50_000:
            identity = f"{row.get('entity_type')}:{row.get('source_namespace')}:{row.get('external_id')}"
            raise RuntimeError(f"Import row exceeds the 50 KB payload limit: {identity}")
        if current and (len(current) >= MAX_BATCH_RECORDS or current_bytes + row_bytes > 4_500_000):
            chunks.append(current)
            current = []
            current_bytes = 2
        current.append(row)
        current_bytes += row_bytes
    if current:
        chunks.append(current)
    return chunks


class RegistryClient:
    def __init__(self, base_url: str | None = None, admin_token: str | None = None,
                 timeout: float = 30.0):
        self.base_url = (base_url or os.getenv("RWA_API_BASE_URL", "http://127.0.0.1:8000")).rstrip("/") + "/"
        self.admin_token = admin_token or os.getenv("REGISTRY_ADMIN_TOKEN")
        if not self.admin_token:
            raise RuntimeError("REGISTRY_ADMIN_TOKEN is required to stage imports.")
        self.timeout = timeout

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        body = canonical_json(payload) if payload is not None else None
        headers = {"accept": "application/json", "X-Registry-Admin-Token": self.admin_token}
        if body is not None:
            headers["content-type"] = "application/json"
        request = Request(urljoin(self.base_url, path.lstrip("/")), data=body, headers=headers, method=method)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                raw = response.read()
            return json.loads(raw.decode("utf-8")) if raw else None
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:1000]
            if self.admin_token:
                detail = detail.replace(self.admin_token, "[REDACTED]")
            raise RuntimeError(f"Registry API {method} {path} failed: HTTP {exc.code}: {detail}") from None
        except (URLError, TimeoutError) as exc:
            raise RuntimeError(f"Registry API {method} {path} failed: {type(exc).__name__}") from None

    def get_aliases(self) -> list[dict[str, Any]]:
        return self.request("GET", "/api/v1/registry/aliases")

    def get_batch(self, batch_id: str) -> dict[str, Any]:
        return self.request("GET", f"/api/v1/registry/imports/{quote(batch_id, safe='')}")

    def stage_rows(self, rows: list[dict[str, Any]], submitted_by: str,
                   source_version: str,
                   on_batch: Callable[[dict[str, Any], list[dict[str, Any]]], None] | None = None
                   ) -> list[dict[str, Any]]:
        staged = []
        for chunk in chunk_import_rows(rows):
            result = self.request("POST", "/api/v1/registry/imports", {
                "source": PROVIDER, "source_version": source_version,
                "submitted_by": submitted_by, "records": chunk,
            })
            staged.append(result)
            if on_batch is not None:
                on_batch(result, chunk)
        return staged


def _load_network_map(path: Path | None) -> dict[str, dict[str, str]]:
    if path is None:
        return {}
    data = _read_json(path)
    if not isinstance(data, dict):
        raise RuntimeError("Network map must be a JSON object keyed by CoinGecko platform slug.")
    cleaned = {}
    for slug, item in data.items():
        if not isinstance(item, dict) or item.get("family") not in {"evm", "solana", "sui", "cosmos", "other"}:
            raise RuntimeError(f"Invalid network mapping for {slug}: expected namespace, display_name and valid family.")
        if not isinstance(slug, str) or not slug or len(slug) > 220:
            raise RuntimeError(f"Invalid network mapping key: {slug!r}")
        if not all(isinstance(item.get(k), str) and item[k].strip() for k in ("namespace", "display_name", "family")):
            raise RuntimeError(f"Invalid network mapping for {slug}: namespace, display_name and family are required.")
        if len(item["namespace"]) > 120 or len(item["display_name"]) > 120:
            raise RuntimeError(f"Network mapping for {slug} exceeds the registry field length limits.")
        cleaned[slug] = item
    return cleaned


def _ensure_run(output_dir: Path, manifest: dict[str, Any], api: RegistryClient,
                submitted_by: str) -> dict[str, Any]:
    if manifest.get("run_id"):
        return api.request("GET", f"/api/v1/registry/provider-runs/{quote(manifest['run_id'], safe='')}")
    coverage = build_coverage(output_dir, manifest)
    run = api.request("POST", "/api/v1/registry/provider-runs", {
        "provider": PROVIDER, "dataset": DATASET, "source_version": manifest["retrieved_at"],
        "started_by": submitted_by, "manifest_sha256": manifest["manifest_sha256"],
        "coverage": coverage,
    })
    manifest["run_id"] = run["id"]
    _write_json(output_dir / "manifest.json", manifest)
    return run


def stage_phase(output_dir: Path, phase: str, submitted_by: str,
                api: RegistryClient, network_map: dict[str, dict[str, str]] | None = None) -> dict[str, Any]:
    manifest, rwa_list, details = load_snapshot(output_dir)
    if phase not in {"foundations", "networks", "products", "deployments"}:
        raise RuntimeError(f"Unsupported import phase: {phase}")
    existing_phase = manifest.get("staged_phases", {}).get(phase, {})
    if existing_phase.get("status") == "complete":
        raise RuntimeError(f"Phase {phase} is already complete for this snapshot.")
    run = _ensure_run(output_dir, manifest, api, submitted_by)
    effective_network_map = dict(manifest.get("network_map", {}))
    if network_map:
        effective_network_map.update(network_map)
        manifest["network_map"] = effective_network_map
    aliases = api.get_aliases()
    counters: dict[str, Any] = {}
    if phase == "foundations":
        rows, counters = build_foundation_rows(output_dir, manifest, rwa_list, details)
        # Do not create duplicate review work for source IDs already approved to one canonical entity.
        rwa_aliases = _active_alias_map(aliases, "rwa_id", "underlying")
        issuer_aliases = _active_alias_map(aliases, "issuer_id", "issuer")
        filtered = []
        already = {"underlyings": 0, "issuers": 0}
        for row in rows:
            ns, external_id = row["source_namespace"], row["external_id"]
            mapped = rwa_aliases.get(external_id) if ns == "rwa_id" else issuer_aliases.get(external_id)
            if mapped:
                already["underlyings" if ns == "rwa_id" else "issuers"] += 1
            else:
                filtered.append(row)
        rows = filtered
        counters["already_mapped"] = already
    elif phase == "networks":
        rows, counters = build_network_rows(output_dir, manifest, details, effective_network_map)
        network_aliases = _active_alias_map(aliases, "platform_slug", "network")
        filtered = [row for row in rows if row["external_id"] not in network_aliases]
        counters["already_mapped"] = len(rows) - len(filtered)
        rows = filtered
    elif phase == "products":
        rows, counters = build_product_rows(manifest, details, aliases)
    else:
        rows, counters = build_deployment_rows(manifest, details, aliases, effective_network_map)

    phase_state = manifest.setdefault("staged_phases", {}).setdefault(phase, {
        "attempts": 0, "staged_external_ids": [], "batch_ids": [],
    })
    staged_identities = set(phase_state["staged_external_ids"])
    rows = [row for row in rows if f"{row['entity_type']}|{row['source_namespace']}|{row['external_id']}" not in staged_identities]
    phase_state["attempts"] += 1
    phase_state["staged_at"] = utc_now()
    phase_state["last_eligible_rows"] = len(rows)
    phase_state["last_counters"] = counters

    def persist_successful_batch(result: dict[str, Any], chunk: list[dict[str, Any]]) -> None:
        batch_id = result["id"]
        phase_state["batch_ids"] = list(dict.fromkeys(phase_state["batch_ids"] + [batch_id]))
        phase_state["staged_external_ids"] = list(dict.fromkeys(
            phase_state["staged_external_ids"] + [
                f"{row['entity_type']}|{row['source_namespace']}|{row['external_id']}" for row in chunk
            ]
        ))
        manifest.setdefault("staged_batch_ids", []).append(batch_id)
        manifest["staged_batch_ids"] = list(dict.fromkeys(manifest["staged_batch_ids"]))
        # Persist each successful batch immediately. If a later chunk fails, a retry
        # will not duplicate the already-created batch or lose its reconciliation ID.
        _write_json(output_dir / "manifest.json", manifest)

    try:
        batches = api.stage_rows(rows, submitted_by, manifest["retrieved_at"],
                                 on_batch=persist_successful_batch) if rows else []
    except Exception:
        phase_state["status"] = "in_progress"
        _write_json(output_dir / "manifest.json", manifest)
        try:
            api.request("PATCH", f"/api/v1/registry/provider-runs/{run['id']}", {
                "status": "awaiting_review",
                "coverage": build_coverage(output_dir, manifest, {"last_staged_phase": phase}),
                "staged_batch_ids": manifest.get("staged_batch_ids", []),
            })
        except Exception:
            pass
        raise
    batch_ids = [item["id"] for item in batches]
    if phase == "networks":
        phase_complete = not counters.get("unsupported_platform_slugs") and counters.get("tokens_without_platforms", 0) == 0
    elif phase == "products":
        phase_complete = not any(counters.get(k, 0) for k in (
            "unresolved_underlying_alias", "unresolved_issuer_alias",
            "tokens_without_provider_id", "tokens_without_issuer", "duplicate_token_ids",
            "issuer_id_out_of_range"
        )) and counters.get("tokens_discovered", 0) > 0
    elif phase == "deployments":
        phase_complete = not any(counters.get(k, 0) for k in (
            "unresolved_product_alias", "unresolved_network_alias",
            "invalid_platform_addresses", "unsupported_platform_slugs", "duplicate_token_ids",
            "tokens_without_platforms"
        )) and counters.get("platform_entries", 0) > 0
    else:
        phase_complete = not any(counters.get(k, 0) for k in (
            "missing_underlying_name", "underlying_id_out_of_range",
            "issuer_id_out_of_range", "issuer_without_name"
        ))
    phase_state["status"] = "complete" if phase_complete else "in_progress"
    phase_state["eligible_rows_total"] = len(phase_state["staged_external_ids"])
    manifest.setdefault("staged_batch_ids", []).extend(batch_ids)
    manifest["staged_batch_ids"] = list(dict.fromkeys(manifest["staged_batch_ids"]))
    coverage = build_coverage(output_dir, manifest, {
        "last_staged_phase": phase, "last_phase_eligible_rows": len(rows),
        "phase_counters": counters, "staged_batch_ids": manifest["staged_batch_ids"],
    })
    _write_json(output_dir / "manifest.json", manifest)
    _write_json(output_dir / "coverage.json", coverage)
    api.request("PATCH", f"/api/v1/registry/provider-runs/{run['id']}", {
        "status": "awaiting_review", "coverage": coverage,
        "staged_batch_ids": manifest["staged_batch_ids"],
    })
    return {"run_id": run["id"], "phase": phase, "eligible_rows": len(rows),
            "batches": batches, "counters": counters, "coverage": coverage}


def reconcile_run(output_dir: Path, api: RegistryClient) -> dict[str, Any]:
    manifest, _, _ = load_snapshot(output_dir)
    run_id = manifest.get("run_id")
    if not run_id:
        raise RuntimeError("No provider ingestion run exists. Stage the foundations phase first.")
    batch_status: dict[str, int] = {}
    record_status: dict[str, int] = {}
    records_by_type: dict[str, dict[str, int]] = {}
    for batch_id in manifest.get("staged_batch_ids", []):
        result = api.get_batch(batch_id)
        batch = result["batch"]
        batch_status[batch["status"]] = batch_status.get(batch["status"], 0) + 1
        for record in result.get("records", []):
            status = record["status"]
            entity_type = record["entity_type"]
            record_status[status] = record_status.get(status, 0) + 1
            typed = records_by_type.setdefault(entity_type, {})
            typed[status] = typed.get(status, 0) + 1
    phase_states = manifest.get("staged_phases", {})
    phases = set(phase_states)
    all_phases_staged = phases == {"foundations", "networks", "products", "deployments"} and all(
        phase_states.get(name, {}).get("status") == "complete"
        for name in ("foundations", "networks", "products", "deployments")
    )
    phase_counters = {name: state.get("last_counters", {}) for name, state in phase_states.items()}
    unsupported = sorted(set(
        slug for counters in phase_counters.values()
        for slug in counters.get("unsupported_platform_slugs", [])
    ))
    unresolved_dependencies = sum(
        counters.get(key, 0)
        for counters in phase_counters.values()
        for key in ("unresolved_underlying_alias", "unresolved_issuer_alias",
                    "unresolved_product_alias", "unresolved_network_alias")
    )
    needs_review = record_status.get("needs_review", 0)
    base_coverage = build_coverage(output_dir, manifest)
    coverage = {
        **base_coverage,
        "staged_phases": sorted(phases),
        "phase_status": {name: state.get("status", "in_progress") for name, state in phase_states.items()},
        "phase_counters": phase_counters,
        "unsupported_platform_slugs": unsupported,
        "unresolved_parent_mappings": unresolved_dependencies,
        "all_pipeline_phases_staged": all_phases_staged,
        "batch_status_counts": batch_status,
        "record_status_counts": record_status,
        "record_status_by_entity_type": records_by_type,
        "review_queue_remaining": needs_review,
        "approved_record_count": record_status.get("approved", 0),
        "rejected_record_count": record_status.get("rejected", 0),
        "duplicate_record_count": record_status.get("duplicate", 0),
    }
    if needs_review:
        status = "awaiting_review"
    elif (
        all_phases_staged
        and manifest.get("is_full_provider_list")
        and manifest.get("details_failed", 0) == 0
        and not unsupported
        and unresolved_dependencies == 0
    ):
        status = "completed"
    else:
        status = "partial"
    _write_json(output_dir / "coverage.json", coverage)
    api.request("PATCH", f"/api/v1/registry/provider-runs/{run_id}", {
        "status": status, "coverage": coverage,
        "staged_batch_ids": manifest.get("staged_batch_ids", []),
    })
    return coverage


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CoinGecko RWA snapshot and evidence-led registry staging.")
    commands = parser.add_subparsers(dest="command", required=True)
    snapshot_parser = commands.add_parser("snapshot", help="Fetch a resumable raw CoinGecko RWA snapshot.")
    snapshot_parser.add_argument("--output-dir", required=True, type=Path)
    snapshot_parser.add_argument("--limit", type=int)
    snapshot_parser.add_argument("--min-interval", type=float, default=2.1)
    snapshot_parser.add_argument("--max-retries", type=int, default=5)
    snapshot_parser.add_argument("--refresh-details", action="store_true")

    stage_parser = commands.add_parser("stage", help="Stage one phase for human review.")
    stage_parser.add_argument("--snapshot-dir", required=True, type=Path)
    stage_parser.add_argument("--phase", required=True, choices=["foundations", "networks", "products", "deployments"])
    stage_parser.add_argument("--submitted-by", required=True)
    stage_parser.add_argument("--network-map", type=Path)

    reconcile_parser = commands.add_parser("reconcile", help="Reconcile staged batches and refresh coverage.")
    reconcile_parser.add_argument("--snapshot-dir", required=True, type=Path)

    args = parser.parse_args(argv)
    try:
        if args.command == "snapshot":
            client = CoinGeckoClient(min_interval=args.min_interval, max_retries=args.max_retries)
            manifest = fetch_snapshot(args.output_dir, client, args.limit, args.refresh_details)
            print(json.dumps(build_coverage(args.output_dir, manifest), indent=2))
        elif args.command == "stage":
            api = RegistryClient()
            result = stage_phase(args.snapshot_dir, args.phase, args.submitted_by, api,
                                 _load_network_map(args.network_map))
            print(json.dumps(result, indent=2))
        else:
            coverage = reconcile_run(args.snapshot_dir, RegistryClient())
            print(json.dumps(coverage, indent=2))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
