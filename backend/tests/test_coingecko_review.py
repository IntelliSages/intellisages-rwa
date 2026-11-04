import pytest

from app.providers.coingecko_review import (
    apply_decisions,
    build_decision_payload,
    build_network_bootstrap_decisions,
    build_underlying_bootstrap_decisions,
    format_record_summary,
)


class FakeReviewApi:
    def __init__(self):
        self.decisions = []

    def decide_record(self, record_id, decision):
        self.decisions.append((record_id, decision))
        return {"id": record_id, "status": "approved", **decision}

    def review_queue(self, batch_id=None, limit=100):
        return []


def test_create_new_requires_evidence_and_allows_override():
    body = build_decision_payload({
        "action": "create_new",
        "reviewer": "reviewer@example.com",
        "evidence_ref": "https://evidence.example/1",
        "canonical_payload_override": {"legal_name": "Acme Issuer Ltd"},
    })
    assert body["evidence_ref"] == "https://evidence.example/1"
    assert body["canonical_payload_override"] == {"legal_name": "Acme Issuer Ltd"}
    assert set(body) == {"action", "reviewer", "evidence_ref", "target_entity_id",
                         "note", "canonical_payload_override"}


def test_create_new_without_evidence_is_rejected():
    with pytest.raises(ValueError, match="evidence_ref"):
        build_decision_payload({"action": "create_new", "reviewer": "r"})


def test_link_existing_requires_target_and_evidence():
    body = build_decision_payload({
        "action": "link_existing",
        "reviewer": "reviewer@example.com",
        "evidence_ref": "ref",
        "target_entity_id": "underlying-1",
    })
    assert body["target_entity_id"] == "underlying-1"

    with pytest.raises(ValueError, match="target_entity_id"):
        build_decision_payload({"action": "link_existing", "reviewer": "r", "evidence_ref": "ref"})


def test_link_existing_rejects_override():
    with pytest.raises(ValueError, match="canonical_payload_override"):
        build_decision_payload({
            "action": "link_existing", "reviewer": "r", "evidence_ref": "ref",
            "target_entity_id": "x", "canonical_payload_override": {"legal_name": "Acme"},
        })


def test_reject_requires_note_and_rejects_override():
    body = build_decision_payload({"action": "reject", "reviewer": "r", "note": "Not RWA"})
    assert body["note"] == "Not RWA"
    assert body["evidence_ref"] is None

    with pytest.raises(ValueError, match="note"):
        build_decision_payload({"action": "reject", "reviewer": "r"})


def test_invalid_action_is_rejected():
    with pytest.raises(ValueError, match="Invalid action"):
        build_decision_payload({"action": "approve", "reviewer": "r"})


def test_apply_decisions_posts_validated_payloads():
    api = FakeReviewApi()
    results = apply_decisions(api, [
        {"record_id": "rec-1", "action": "create_new", "reviewer": "r",
         "evidence_ref": "ref", "canonical_payload_override": {"legal_name": "Acme"}},
        {"record_id": "rec-2", "action": "link_existing", "reviewer": "r",
         "evidence_ref": "ref", "target_entity_id": "underlying-1"},
    ])
    assert len(results) == 2
    assert [call[0] for call in api.decisions] == ["rec-1", "rec-2"]
    assert api.decisions[0][1]["canonical_payload_override"] == {"legal_name": "Acme"}


def test_apply_decisions_dry_run_does_not_post():
    api = FakeReviewApi()
    results = apply_decisions(api, [
        {"record_id": "rec-1", "action": "reject", "reviewer": "r", "note": "nope"},
    ], dry_run=True)
    assert api.decisions == []
    assert results[0]["dry_run"] is True
    assert results[0]["payload"]["action"] == "reject"


def test_apply_decisions_requires_record_id():
    with pytest.raises(ValueError, match="record_id"):
        apply_decisions(FakeReviewApi(), [{"action": "reject", "reviewer": "r", "note": "nope"}])


def test_format_record_summary_uses_display_name_and_asset_type():
    record = {
        "id": "rec-1",
        "entity_type": "underlying",
        "external_id": "gold",
        "payload": {"canonical_payload": {"display_name": "Gold", "asset_type": "commodity"}},
        "candidates": [],
    }
    summary = format_record_summary(record)
    assert "Gold" in summary
    assert "commodity" in summary
    assert "ext_id=gold" in summary


def test_bootstrap_decisions_approve_underlyings_and_defer_issuers():
    records = [
        {"id": "u1", "entity_type": "underlying", "payload": {"source_metadata": {
            "endpoint": "/rwas/gold?tokens=true", "source_sha256": "abc",
            "retrieved_at": "2026-10-30T00:00:00Z",
        }}},
        {"id": "i1", "entity_type": "issuer", "payload": {"source_metadata": {}}},
        {"id": "u2", "entity_type": "underlying", "payload": {"source_metadata": {
            "discovery_endpoint": "/rwas/list",
        }}},
    ]
    decisions, deferred = build_underlying_bootstrap_decisions(records, "r@example.com")
    assert deferred == 1
    assert len(decisions) == 2
    assert decisions[0]["record_id"] == "u1"
    assert decisions[0]["action"] == "create_new"
    assert decisions[0]["reviewer"] == "r@example.com"
    assert "source_sha256:abc" in decisions[0]["evidence_ref"]
    assert decisions[1]["evidence_ref"].startswith("CoinGecko /rwas/list")


def test_bootstrap_network_decisions_use_mapping_evidence():
    records = [
        {"id": "n1", "entity_type": "network", "external_id": "ethereum", "payload": {
            "source_metadata": {"mapping_basis": "explicit CoinGecko platform-to-CAIP-2 mapping"},
        }},
        {"id": "u1", "entity_type": "underlying", "payload": {}},
    ]
    decisions = build_network_bootstrap_decisions(records, "r@example.com")
    assert len(decisions) == 1
    assert decisions[0]["record_id"] == "n1"
    assert decisions[0]["action"] == "create_new"
    assert "platform slug 'ethereum'" in decisions[0]["evidence_ref"]
