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
    assert (tmp_path / "details" / next((p.name for p in (tmp_path / "details").glob("*.json")))).exists()
    assert manifest["manifest_sha256"] and len(manifest["manifest_sha256"]) == 64
    # A second run with the same RWA list reuses the saved detail, rather than refetching it.
    second = fetch_snapshot(tmp_path, client)
    assert second["details_succeeded"] == 1
    assert [call[0] for call in client.calls].count("rwas/nvidia") == 1


def test_foundations_create_underlyings_and_deduplicated_issuers_with_provenance(tmp_path):
    client = FakeCoinGecko()
    manifest = fetch_snapshot(tmp_path, client)
    rwa_list = __import__("json").loads((tmp_path / "rwas-list.json").read_text())
    details = {"nvidia": __import__("json").loads(next((tmp_path / "details").glob("*.json")).read_text())}
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
    details = {"nvidia": __import__("json").loads(next((tmp_path / "details").glob("*.json")).read_text())}
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



class FakeRegistry:
    def __init__(self):
        self.aliases = []
        self.batches = {}
        self.run = None
        self.next_batch = 1

    def get_aliases(self):
        return list(self.aliases)

    def stage_rows(self, rows, submitted_by, source_version):
        batch_id = f"batch-{self.next_batch}"
        self.next_batch += 1
        self.batches[batch_id] = {
            "batch": {"id": batch_id, "status": "reviewing"},
            "records": [{"entity_type": row["entity_type"], "status": "needs_review",
                         "source_namespace": row["source_namespace"], "external_id": row["external_id"]}
                        for row in rows],
        }
        return [{"id": batch_id, "total_records": len(rows)}]

    def get_batch(self, batch_id):
        return self.batches[batch_id]

    def request(self, method, path, payload=None):
        if method == "POST" and path == "/api/v1/registry/provider-runs":
            self.run = {"id": "provider-run-1", **payload, "staged_batch_ids": []}
            return self.run
        if method == "GET" and path == "/api/v1/registry/provider-runs/provider-run-1":
            return self.run
        if method == "PATCH" and path.endswith("/provider-run-1"):
            self.run.update(payload)
            self.run["staged_batch_ids"] = list(dict.fromkeys(
                self.run.get("staged_batch_ids", []) + payload.get("staged_batch_ids", [])
            ))
            return self.run
        raise AssertionError((method, path, payload))


def _approved_alias(namespace, external_id, entity_type, entity_id):
    from datetime import date
    return {"provider": "coingecko", "namespace": namespace, "external_id": external_id,
            "entity_type": entity_type, "entity_id": entity_id, "is_verified": True,
            "effective_from": date.today().isoformat(), "effective_to": None}


def test_phased_pipeline_waits_for_approved_parents_and_can_resume_partial_phases(tmp_path):
    from app.providers.coingecko_pilot import stage_phase

    manifest = fetch_snapshot(tmp_path, FakeCoinGecko())
    assert manifest["details_succeeded"] == 1
    api = FakeRegistry()

    foundations = stage_phase(tmp_path, "foundations", "operator", api)
    assert foundations["eligible_rows"] == 3
    assert foundations["run_id"] == "provider-run-1"

    # Products cannot be staged until both underlying and issuer aliases have been human-approved.
    blocked_products = stage_phase(tmp_path, "products", "operator", api)
    assert blocked_products["eligible_rows"] == 0
    assert blocked_products["counters"]["unresolved_underlying_alias"] == 2
    assert blocked_products["counters"]["unresolved_issuer_alias"] == 2

    api.aliases.extend([
        _approved_alias("rwa_id", "nvidia", "underlying", "underlying-1"),
        _approved_alias("issuer_id", "xstocks", "issuer", "issuer-1"),
        _approved_alias("issuer_id", "ondo", "issuer", "issuer-2"),
    ])
    products = stage_phase(tmp_path, "products", "operator", api)
    assert products["eligible_rows"] == 2
    assert products["counters"]["unresolved_underlying_alias"] == 0
    assert products["counters"]["unresolved_issuer_alias"] == 0

    # The default map intentionally leaves unknown-chain unresolved; an explicit operator map can complete it.
    networks = stage_phase(tmp_path, "networks", "operator", api)
    assert networks["eligible_rows"] == 2
    assert networks["counters"]["unsupported_platform_slugs"] == ["unknown-chain"]
    custom_map = {"unknown-chain": {"namespace": "custom:unknown-chain",
                                    "display_name": "Unknown Chain", "family": "other"}}
    networks_retry = stage_phase(tmp_path, "networks", "operator", api, custom_map)
    assert networks_retry["eligible_rows"] == 1
    assert networks_retry["counters"]["unsupported_platform_slugs"] == []

    api.aliases.extend([
        _approved_alias("rwa_token_id", "nvidia-xstock", "issuer_product", "product-1"),
        _approved_alias("rwa_token_id", "nvidia-ondo", "issuer_product", "product-2"),
        _approved_alias("platform_slug", "ethereum", "network", "network-eth"),
        _approved_alias("platform_slug", "solana", "network", "network-sol"),
        _approved_alias("platform_slug", "unknown-chain", "network", "network-unknown"),
    ])
    deployments = stage_phase(tmp_path, "deployments", "operator", api, custom_map)
    assert deployments["eligible_rows"] == 4
    assert deployments["counters"]["unresolved_product_alias"] == 0
    assert deployments["counters"]["unresolved_network_alias"] == 0

    saved = __import__("json").loads((tmp_path / "manifest.json").read_text())
    assert saved["staged_phases"]["foundations"]["status"] == "complete"
    assert saved["staged_phases"]["products"]["status"] == "complete"
    assert saved["staged_phases"]["networks"]["status"] == "complete"
    assert saved["staged_phases"]["deployments"]["status"] == "complete"
    assert len(saved["staged_batch_ids"]) == 5
