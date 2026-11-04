"""One-shot Phase 2 orchestration for CoinGecko RWA registry population.

Completes the automatable portion of Phase 2 against a running registry API:

- approves staged provider-reported underlyings (create_new with source evidence),
- stages and approves canonical networks (create_new with mapping evidence),
- attempts products (reports the issuer-alias blocker),
- exports the remaining issuers for manual legal-name review, and
- reconciles coverage.

Issuers are deliberately not auto-approved: a CoinGecko label is not an
independently evidenced legal name, so products and deployments stay blocked until
those 33 records are reviewed by a human.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .coingecko_pilot import RegistryClient, load_snapshot, reconcile_run, stage_phase
from .coingecko_review import (
    apply_decisions,
    build_network_bootstrap_decisions,
    build_underlying_bootstrap_decisions,
)

DEFAULT_SNAPSHOT = Path("data/provider_snapshots/coingecko/full-2026-10-30")


def _issuer_summary(record: dict[str, Any]) -> dict[str, Any]:
    payload = record.get("payload") or {}
    source = payload.get("source_payload") if isinstance(payload, dict) else {}
    source = source if isinstance(source, dict) else {}
    return {
        "record_id": record.get("id"),
        "external_id": record.get("external_id"),
        "provider_name": source.get("name") or record.get("external_id"),
        "required_decision": "link_existing (with evidence + target) OR create_new "
                             "(with canonical_payload_override.legal_name + evidence)",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Complete the automatable portion of Phase 2 registry population.",
    )
    parser.add_argument("--snapshot-dir", type=Path, default=DEFAULT_SNAPSHOT)
    parser.add_argument("--base-url", default=None, help="Registry API base URL (default RWA_API_BASE_URL).")
    parser.add_argument("--admin-token", default=None, help="Registry admin token (default REGISTRY_ADMIN_TOKEN).")
    parser.add_argument("--submitted-by", required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--issuer-export", type=Path, default=Path("issuer-review.json"))
    args = parser.parse_args(argv)

    api = RegistryClient(base_url=args.base_url, admin_token=args.admin_token)
    manifest, _, _ = load_snapshot(args.snapshot_dir)
    report: dict[str, Any] = {"underlyings_approved": 0, "networks_approved": 0, "issuers_deferred": 0}

    # 1. Approve every staged foundation underlying with its captured source evidence.
    for batch_id in manifest.get("staged_batch_ids", []):
        records = api.review_queue(batch_id=batch_id, limit=500)
        decisions, deferred = build_underlying_bootstrap_decisions(records, args.reviewer)
        report["issuers_deferred"] += deferred
        if decisions:
            apply_decisions(api, decisions)
            report["underlyings_approved"] += len(decisions)

    # 2. Stage + approve the canonical network identities.
    network_result = stage_phase(args.snapshot_dir, "networks", args.submitted_by, api)
    for batch in network_result["batches"]:
        records = api.review_queue(batch_id=batch["id"], limit=500)
        decisions = build_network_bootstrap_decisions(records, args.reviewer)
        if decisions:
            apply_decisions(api, decisions)
            report["networks_approved"] += len(decisions)
    report["networks_counters"] = network_result["counters"]

    # 3. Attempt products; they remain unresolved until issuer aliases are approved.
    try:
        product_result = stage_phase(args.snapshot_dir, "products", args.submitted_by, api)
        report["products"] = product_result["counters"]
    except Exception as exc:  # noqa: BLE001 - reported, not fatal.
        report["products_error"] = str(exc)

    # 4. Export the remaining issuers for manual legal-name review.
    issuers: list[dict[str, Any]] = []
    for batch_id in manifest.get("staged_batch_ids", []):
        issuers.extend(
            record for record in api.review_queue(batch_id=batch_id, limit=500)
            if record.get("entity_type") == "issuer"
        )
    args.issuer_export.write_text(
        json.dumps([_issuer_summary(item) for item in issuers], indent=2), encoding="utf-8",
    )
    report["issuer_review_file"] = str(args.issuer_export)
    report["issuers_awaiting_legal_name"] = len(issuers)

    # 5. Reconcile and record coverage.
    coverage = reconcile_run(args.snapshot_dir, api)
    report["review_queue_remaining"] = coverage.get("review_queue_remaining", 0)
    report["approved_record_count"] = coverage.get("approved_record_count", 0)
    report["unsupported_platform_slugs"] = coverage.get("unsupported_platform_slugs", [])
    report["phase_status"] = coverage.get("phase_status", {})

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
