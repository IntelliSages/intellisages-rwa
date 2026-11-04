"""Operator review CLI for staged CoinGecko RWA discovery records.

Drives the existing evidence-gated import review API (``GET /imports/queue`` and
``POST /imports/records/{id}/decision``) so a human reviewer can approve or reject
staged discovery records without hand-writing HTTP requests.

This module never fabricates source evidence and never bypasses the server-side
review rules. Approving a mapping (``link_existing`` or ``create_new``) requires an
``evidence_ref``; creating a new issuer requires a ``canonical_payload_override``
supplying the independently evidenced ``legal_name`` (the provider label is never
used as a canonical legal name).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .coingecko_pilot import RegistryClient

ACTIONS = ("link_existing", "create_new", "reject")
ENTITIES = ("underlying", "issuer", "network", "issuer_product", "deployment")


def _load_json_file(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError(f"Could not read JSON from {path}: {exc}") from exc


def build_decision_payload(decision: dict[str, Any]) -> dict[str, Any]:
    """Validate one decision entry and return the full API request body.

    The server schema requires every field to be present (null is allowed), so the
    returned body always contains all six keys.
    """
    action = decision.get("action")
    if action not in ACTIONS:
        raise ValueError(f"Invalid action {action!r}; expected one of {ACTIONS}.")
    reviewer = decision.get("reviewer")
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise ValueError("Each decision requires a non-empty 'reviewer'.")

    evidence = decision.get("evidence_ref")
    note = decision.get("note")
    target = decision.get("target_entity_id")
    override = decision.get("canonical_payload_override")

    body: dict[str, Any] = {
        "action": action,
        "reviewer": reviewer.strip(),
        "evidence_ref": None,
        "target_entity_id": None,
        "note": None,
        "canonical_payload_override": None,
    }

    if action == "reject":
        if override is not None:
            raise ValueError("canonical_payload_override is only valid for create_new decisions.")
        if not isinstance(note, str) or not note.strip():
            raise ValueError("A rejection requires a non-empty 'note'.")
        body["note"] = note.strip()
        return body

    # Both approval actions require source evidence.
    if not isinstance(evidence, str) or not evidence.strip():
        raise ValueError(f"{action} requires a non-empty 'evidence_ref'.")
    body["evidence_ref"] = evidence.strip()
    if isinstance(note, str) and note.strip():
        body["note"] = note.strip()

    if action == "link_existing":
        if override is not None:
            raise ValueError("canonical_payload_override cannot be used when linking an existing entity.")
        if not isinstance(target, str) or not target.strip():
            raise ValueError("link_existing requires 'target_entity_id'.")
        body["target_entity_id"] = target.strip()
        return body

    # create_new
    if isinstance(target, str) and target.strip():
        raise ValueError("target_entity_id cannot be used with create_new; omit it.")
    body["canonical_payload_override"] = override if isinstance(override, dict) else None
    return body


def apply_decisions(api: RegistryClient | None, decisions: list[dict[str, Any]],
                    *, dry_run: bool = False) -> list[dict[str, Any]]:
    """Post a list of decisions, validating each before it reaches the server.

    ``api`` is only used when ``dry_run`` is false.
    """
    results: list[dict[str, Any]] = []
    for index, decision in enumerate(decisions, start=1):
        record_id = decision.get("record_id")
        if not isinstance(record_id, str) or not record_id.strip():
            raise ValueError(f"Decision #{index} is missing a non-empty 'record_id'.")
        payload = build_decision_payload(decision)
        if dry_run:
            results.append({"record_id": record_id, "dry_run": True, "payload": payload})
            continue
        results.append(api.decide_record(record_id.strip(), payload))
    return results


def build_underlying_bootstrap_decisions(records: list[dict[str, Any]],
                                         reviewer: str) -> tuple[list[dict[str, Any]], int]:
    """Generate evidence-backed create_new decisions for provider-reported underlyings.

    Returns ``(decisions, deferred_issuer_count)``. Issuers are never auto-approved:
    their CoinGecko label is not an independently evidenced legal name, so they are
    counted as deferred and left for manual review.
    """
    decisions: list[dict[str, Any]] = []
    deferred = 0
    for record in records:
        entity_type = record.get("entity_type")
        if entity_type == "issuer":
            deferred += 1
            continue
        if entity_type != "underlying":
            continue
        payload = record.get("payload") or {}
        metadata = payload.get("source_metadata") if isinstance(payload, dict) else {}
        metadata = metadata if isinstance(metadata, dict) else {}
        endpoint = metadata.get("endpoint") or metadata.get("discovery_endpoint") or "CoinGecko RWA discovery"
        evidence = f"CoinGecko {endpoint}"
        sha = metadata.get("source_sha256")
        retrieved = metadata.get("retrieved_at")
        if sha:
            evidence += f" (source_sha256:{sha})"
        if retrieved:
            evidence += f" retrieved {retrieved}"
        decisions.append({
            "record_id": record.get("id"),
            "action": "create_new",
            "reviewer": reviewer,
            "evidence_ref": evidence,
        })
    return decisions, deferred


def _canonical_display_name(record: dict[str, Any]) -> str:
    payload = record.get("payload") or {}
    canonical = payload.get("canonical_payload") if isinstance(payload, dict) else {}
    if isinstance(canonical, dict):
        for key in ("display_name", "legal_name", "provider_name"):
            value = canonical.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return record.get("external_id", "?")


def _canonical_asset_type(record: dict[str, Any]) -> str:
    payload = record.get("payload") or {}
    canonical = payload.get("canonical_payload") if isinstance(payload, dict) else {}
    value = canonical.get("asset_type") if isinstance(canonical, dict) else None
    return value if isinstance(value, str) else ""


def format_record_summary(record: dict[str, Any]) -> str:
    entity = record.get("entity_type", "?")
    display = _canonical_display_name(record)
    asset = _canonical_asset_type(record)
    asset_suffix = f" · {asset}" if asset else ""
    candidates = record.get("candidates") or []
    return (f"{record.get('id', '?')}  {entity:<14} {display}{asset_suffix}  "
            f"ext_id={record.get('external_id', '?')}  candidates={len(candidates)}")


def fetch_queue(api: RegistryClient, batch_id: str | None, entity_type: str | None,
                limit: int) -> list[dict[str, Any]]:
    records = api.review_queue(batch_id=batch_id, limit=limit)
    if entity_type:
        records = [r for r in records if r.get("entity_type") == entity_type]
    return records


def build_client(args: argparse.Namespace) -> RegistryClient:
    return RegistryClient(base_url=args.base_url, admin_token=args.admin_token)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Review staged CoinGecko RWA discovery records via the import review API.",
    )
    parser.add_argument("--base-url", default=None,
                        help="Registry API base URL (defaults to RWA_API_BASE_URL).")
    parser.add_argument("--admin-token", default=None,
                        help="Registry admin token (defaults to REGISTRY_ADMIN_TOKEN).")
    commands = parser.add_subparsers(dest="command", required=True)

    queue_parser = commands.add_parser("queue", help="List records awaiting review.")
    queue_parser.add_argument("--batch-id", default=None)
    queue_parser.add_argument("--entity-type", choices=ENTITIES, default=None)
    queue_parser.add_argument("--limit", type=int, default=100)
    queue_parser.add_argument("--export", type=Path, default=None,
                              help="Write full record JSON to a file for offline review.")
    queue_parser.add_argument("--json", action="store_true",
                              help="Print full record JSON to stdout instead of a summary.")

    decide_parser = commands.add_parser("decide", help="Post a single review decision.")
    decide_parser.add_argument("record_id")
    decide_parser.add_argument("--action", required=True, choices=ACTIONS)
    decide_parser.add_argument("--reviewer", required=True)
    decide_parser.add_argument("--evidence-ref", default=None)
    decide_parser.add_argument("--target-entity-id", default=None)
    decide_parser.add_argument("--note", default=None)
    decide_parser.add_argument("--override", type=Path, default=None,
                               help="JSON file with canonical_payload_override (create_new only).")

    apply_parser = commands.add_parser("apply", help="Apply decisions from a JSON file.")
    apply_parser.add_argument("file", type=Path)
    apply_parser.add_argument("--dry-run", action="store_true",
                              help="Validate and print decisions without posting them.")

    bootstrap_parser = commands.add_parser(
        "bootstrap",
        help="Generate evidence-backed create_new decisions for provider-reported underlyings.",
    )
    bootstrap_parser.add_argument("--reviewer", required=True)
    bootstrap_parser.add_argument("--batch-id", default=None)
    bootstrap_parser.add_argument("--limit", type=int, default=500)
    bootstrap_parser.add_argument("--out", type=Path, default=None,
                                  help="Write decisions to a JSON file (default stdout).")

    args = parser.parse_args(argv)
    try:
        if args.command == "queue":
            api = build_client(args)
            records = fetch_queue(api, args.batch_id, args.entity_type, args.limit)
            if args.export:
                args.export.write_text(json.dumps(records, indent=2), encoding="utf-8")
                print(f"Wrote {len(records)} record(s) to {args.export}")
            if args.json:
                print(json.dumps(records, indent=2))
            else:
                for record in records:
                    print(format_record_summary(record))
                print(f"\n{len(records)} record(s) awaiting review.")
            return 0

        if args.command == "decide":
            override = _load_json_file(args.override) if args.override else None
            decision = {
                "action": args.action,
                "reviewer": args.reviewer,
                "evidence_ref": args.evidence_ref,
                "target_entity_id": args.target_entity_id,
                "note": args.note,
                "canonical_payload_override": override,
            }
            api = build_client(args)
            result = api.decide_record(args.record_id, build_decision_payload(decision))
            print(json.dumps(result, indent=2))
            return 0

        if args.command == "bootstrap":
            api = build_client(args)
            records = api.review_queue(batch_id=args.batch_id, limit=args.limit)
            decisions, deferred = build_underlying_bootstrap_decisions(records, args.reviewer)
            document = {"reviewer": args.reviewer, "decisions": decisions}
            if args.out:
                args.out.write_text(json.dumps(document, indent=2), encoding="utf-8")
                print(f"Wrote {len(decisions)} underlying decision(s) to {args.out}")
            else:
                print(json.dumps(document, indent=2))
            if deferred:
                print(f"\n{deferred} issuer record(s) are not auto-approved and require "
                      f"independent legal-name evidence.", file=sys.stderr)
            return 0

        document = _load_json_file(args.file)
        if isinstance(document, dict):
            reviewer = document.get("reviewer")
            decisions = document.get("decisions")
            if not isinstance(decisions, list):
                raise ValueError("Decision file must contain a 'decisions' list (or be a bare list).")
        else:
            reviewer = None
            decisions = document if isinstance(document, list) else []
            if not decisions:
                raise ValueError("Decision file must be a list or an object with a 'decisions' list.")

        prepared: list[dict[str, Any]] = []
        for decision in decisions:
            if not isinstance(decision, dict):
                raise ValueError("Every decision entry must be an object.")
            if reviewer is not None and not decision.get("reviewer"):
                decision = {**decision, "reviewer": reviewer}
            prepared.append(decision)
        api = None if args.dry_run else build_client(args)
        results = apply_decisions(api, prepared, dry_run=args.dry_run)
        print(json.dumps(results, indent=2))
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI boundary; surface a clean message.
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
