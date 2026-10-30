from pathlib import Path

from app.providers.coingecko_pilot import (
    DEFAULT_NETWORK_MAP,
    build_deployment_rows,
    build_foundation_rows,
    build_network_rows,
    build_product_rows,
    build_coverage,
    fetch_snapshot,
)


class FakeCoinGecko:
    base_url = "https://api.coingecko.com/api/v3/"

    def __init__(self):
        self.calls = []

    def get_json(self, path, params=None):
        self.calls.append((path, params))
        if path == "rwas/list":
            return [{"id": "nvidia", "symbol": "nvda", "name": "NVIDIA", "asset_type": "stock"}]
        if path == "rwas/issuers/list":
            return [{"id": "xstocks", "name": "xStocks"}, {"id": "ondo", "name": "Ondo Finance"}]
        if path == "rwas/nvidia":
            return {
                "id": "nvidia", "symbol": "nvda", "name": "NVIDIA", "asset_type": "stock",
                "tokens": [
                    {"id": "nvidia-xstock", "symbol": "nvdax", "name": "NVIDIA xStock",
                     "issuer_details": {"id": "xstocks", "name": "xStocks"},
                     "platforms": {"ethereum": "0x" + "a" * 40, "solana": "Mint111", "unknown-chain": "addr-1"}},
                    {"id": "nvidia-ondo", "symbol": "nvdaon", "name": "NVIDIA Ondo",
                     "issuer_details": {"id": "ondo", "name": "Ondo Finance"},
                     "platforms": {"ethereum": "0x" + "b" * 40}},
                ],
            }
        raise AssertionError(f"Unexpected path {path}")


def aliases_for_parents():
    return [
        {"provider": "coingecko", "namespace": "rwa_id", "external_id": "nvidia",
         "entity_type": "underlying", "entity_id": "underlying-1", "is_verified": True,
         "effective_from": "2026-01-01", "effective_to": None},
        {"provider": "coingecko", "namespace": "issuer_id", "external_id": "xstocks",
         "entity_type": "issuer", "entity_id": "issuer-1", "is_verified": True,
         "effective_from": "2026-01-01", "effective_to": None},
        {"provider": "coingecko", "namespace": "issuer_id", "external_id": "ondo",
         "entity_type": "issuer", "entity_id": "issuer-2", "is_verified": True,
         "effective_from": "2026-01-01", "effective_to": None},
    ]


def test_snapshot_fetches_real_endpoint_shapes_and_writes_resumable_raw_files(tmp_path):
    client = FakeCoinGecko()
    manifest = fetch_snapshot(tmp_path, client)
    assert manifest["expected_rwa_count"] == 1
    assert manifest["details_succeeded"] == 1
    assert manifest["details_failed"] == 0
    assert (tmp_path / "rwas-list.json").exists()
    assert (tmp_path / "details" / "nvidia.json").exists()
    assert manifest["manifest_sha256"] and len(manifest["manifest_sha256"]) == 64
    # A second run with the same RWA list reuses the saved detail, rather than refetching it.
    second = fetch_snapshot(tmp_path, client)
    assert second["details_succeeded"] == 1
    assert [call[0] for call in client.calls].count("rwas/nvidia") == 1


def test_foundations_create_underlyings_and_deduplicated_issuers_with_provenance(tmp_path):
    client = FakeCoinGecko()
    manifest = fetch_snapshot(tmp_path, client)
    rwa_list = __import__("json").loads((tmp_path / "rwas-list.json").read_text())
    details = {"nvidia": __import__("json").loads((tmp_path / "details" / "nvidia.json").read_text())}
    rows, counters = build_foundation_rows(tmp_path, manifest, rwa_list, details)
    assert counters["underlyings"] == 1
    assert counters["issuers"] == 2
    assert {r["entity_type"] for r in rows} == {"underlying", "issuer"}
    underlying = next(r for r in rows if r["entity_type"] == "underlying")
    assert underlying["payload"]["canonical_payload"]["asset_type"] == "equity"
    assert underlying["payload"]["source_payload"]["id"] == "nvidia"
    issuer = next(r for r in rows if r["entity_type"] == "issuer")
    assert "legal identity requires independent review" in issuer["payload"]["source_metadata"]["name_semantics"]


def test_network_mapping_is_explicit_and_unknown_slugs_remain_unresolved(tmp_path):
    client = FakeCoinGecko()
    manifest = fetch_snapshot(tmp_path, client)
    details = {"nvidia": __import__("json").loads((tmp_path / "details" / "nvidia.json").read_text())}
    rows, coverage = build_network_rows(tmp_path, manifest, details)
    assert {row["external_id"] for row in rows} == {"ethereum", "solana"}
    assert coverage["unsupported_platform_slugs"] == ["unknown-chain"]
    assert next(row for row in rows if row["external_id"] == "ethereum")["payload"]["canonical_payload"]["namespace"] == "eip155:1"
    assert "unknown-chain" not in DEFAULT_NETWORK_MAP


def test_products_require_verified_underlying_and_issuer_aliases():
    detail = {"nvidia": {
        "id": "nvidia", "asset_type": "stock",
        "tokens": [{"id": "nvidia-xstock", "symbol": "nvdax", "name": "NVIDIA xStock",
                    "issuer_details": {"id": "xstocks", "name": "xStocks"},
                    "platforms": {"ethereum": "0x" + "a" * 40}}]}}
    rows, counters = build_product_rows({"retrieved_at": "2026-10-30T00:00:00Z"}, detail, [])
    assert rows == []
    assert counters["unresolved_underlying_alias"] == 1
    rows, counters = build_product_rows({"retrieved_at": "2026-10-30T00:00:00Z"}, detail, aliases_for_parents())
    assert len(rows) == 1
    payload = rows[0]["payload"]["canonical_payload"]
    assert payload["issuer_id"] == "issuer-1"
    assert payload["underlying_id"] == "underlying-1"
    assert payload["representation_type"] == "unknown"
    assert "entitlement" in payload["unit_description"]


def test_deployments_require_approved_product_and_network_aliases():
    detail = {"nvidia": {
        "id": "nvidia", "asset_type": "stock",
        "tokens": [{"id": "nvidia-xstock", "symbol": "nvdax",
                    "issuer_details": {"id": "xstocks", "name": "xStocks"},
                    "platforms": {"ethereum": "0x" + "a" * 40, "unknown-chain": "addr-1"}}]}}
    aliases = aliases_for_parents() + [
        {"provider": "coingecko", "namespace": "rwa_token_id", "external_id": "nvidia-xstock",
         "entity_type": "issuer_product", "entity_id": "product-1", "is_verified": True,
         "effective_from": "2026-01-01", "effective_to": None},
        {"provider": "coingecko", "namespace": "platform_slug", "external_id": "ethereum",
         "entity_type": "network", "entity_id": "network-1", "is_verified": True,
         "effective_from": "2026-01-01", "effective_to": None},
    ]
    rows, counters = build_deployment_rows({"retrieved_at": "2026-10-30T00:00:00Z"}, detail, aliases)
    assert len(rows) == 1
    assert rows[0]["payload"]["canonical_payload"]["issuer_product_id"] == "product-1"
    assert rows[0]["payload"]["canonical_payload"]["network_id"] == "network-1"
    assert rows[0]["payload"]["canonical_payload"]["is_verified"] is False
    assert counters["unsupported_platform_slugs"] == ["unknown-chain"]


def test_coverage_labels_provider_scope_not_global_market_completeness(tmp_path):
    client = FakeCoinGecko()
    manifest = fetch_snapshot(tmp_path, client, limit=1)
    coverage = build_coverage(tmp_path, manifest)
    assert coverage["provider_rwa_list_count"] == 1
    assert coverage["full_provider_list_requested"] is True
    assert "not proof of complete market coverage" in coverage["coverage_warning"]
