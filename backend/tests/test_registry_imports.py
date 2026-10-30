import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base


def stage(client, rows, source="provider-x"):
    return client.post("/api/v1/registry/imports", json={
        "source": source, "source_version": "2026-10-30", "submitted_by": "operator@example.test",
        "records": rows,
    })


def row(entity_type, external_id, payload, namespace="product-id"):
    return {"entity_type": entity_type, "source_namespace": namespace,
            "external_id": external_id, "payload": payload}


def test_import_api_is_disabled_without_server_token(monkeypatch):
    monkeypatch.delenv("REGISTRY_ADMIN_TOKEN", raising=False)
    response = TestClient(app).get("/api/v1/registry/imports")
    assert response.status_code == 503


def test_stage_queue_and_audit(client):
    response = stage(client, [row("underlying", "nvda", {
        "canonical_key": "equity:nvidia", "display_name": "NVIDIA", "asset_type": "equity"
    }, "native-asset-id")])
    assert response.status_code == 201
    batch = response.json()
    assert batch["status"] == "reviewing"
    assert len(client.get("/api/v1/registry/imports/queue").json()) == 1
    audit = client.get(f"/api/v1/registry/imports/{batch['id']}/audit").json()
    assert [event["action"] for event in audit] == ["record_staged"]


def test_exact_canonical_key_is_candidate_not_auto_approved(client):
    client.post("/api/v1/registry/underlyings", json={
        "canonical_key": "equity:nvidia", "display_name": "NVIDIA", "asset_type": "equity"})
    batch = stage(client, [row("underlying", "nvda-feed-1", {
        "canonical_key": "equity:nvidia", "display_name": "NVIDIA", "asset_type": "equity"
    }, "asset-id")]).json()
    record = client.get(f"/api/v1/registry/imports/{batch['id']}").json()["records"][0]
    assert record["status"] == "needs_review"
    assert "exact_canonical_key" in record["candidates"][0]["match_basis"]
    assert record["resolved_entity_id"] is None


def test_symbol_only_product_candidate_is_weak(client):
    underlying = client.post("/api/v1/registry/underlyings", json={
        "canonical_key": "equity:nvidia", "display_name": "NVIDIA", "asset_type": "equity"}).json()
    issuer = client.post("/api/v1/registry/issuers", json={
        "canonical_key": "issuer:ondo", "legal_name": "Ondo"}).json()
    product = client.post("/api/v1/registry/products", json={
        "canonical_key": "product:ondo:nvdax", "issuer_id": issuer["id"],
        "underlying_id": underlying["id"], "native_product_id": "NVDAx", "display_name": "NVDAx",
        "symbol": "NVDA", "instrument_form": "tokenized_equity", "unit_description": "one issuer-defined token"})
    assert product.status_code == 201
    batch = stage(client, [row("issuer_product", "NVDA", {
        "canonical_key": "product:unknown:nvda", "issuer_id": issuer["id"],
        "underlying_id": underlying["id"], "native_product_id": "different-id",
        "display_name": "NVDA", "symbol": "NVDA", "instrument_form": "tokenized_equity",
        "unit_description": "unknown"}, "symbol")]).json()
    record = client.get(f"/api/v1/registry/imports/{batch['id']}").json()["records"][0]
    weak = [c for c in record["candidates"] if c["match_basis"] == "symbol_only_do_not_auto_link"]
    assert len(weak) == 1 and weak[0]["confidence"] == 0.1
    assert record["status"] == "needs_review"


def test_approval_create_new_requires_evidence_and_creates_verified_alias(client):
    batch = stage(client, [row("underlying", "NVDA-001", {
        "canonical_key": "equity:nvidia", "display_name": "NVIDIA", "asset_type": "equity"
    }, "asset-id")]).json()
    record = client.get(f"/api/v1/registry/imports/{batch['id']}").json()["records"][0]
    endpoint = f"/api/v1/registry/imports/records/{record['id']}/decision"
    assert client.post(endpoint, json={"action": "create_new", "reviewer": "reviewer"}).status_code == 422
    approved = client.post(endpoint, json={"action": "create_new", "reviewer": "reviewer",
        "evidence_ref": "https://issuer.example/legal/asset"})
    assert approved.status_code == 200 and approved.json()["status"] == "approved"
    assert approved.json()["resolution_method"] == "human_approved_new_entity"
    aliases = client.get("/api/v1/registry/aliases").json()
    matching = [a for a in aliases if a["external_id"] == "NVDA-001"]
    assert len(matching) == 1 and matching[0]["is_verified"] is True
    assert client.get(f"/api/v1/registry/imports/{batch['id']}").json()["batch"]["status"] == "completed"


def test_link_existing_requires_evidence_and_correct_entity_type(client):
    issuer = client.post("/api/v1/registry/issuers", json={
        "canonical_key": "issuer:ondo", "legal_name": "Ondo Finance"}).json()
    batch = stage(client, [row("issuer", "ondo-native", {
        "canonical_key": "issuer:ondo", "legal_name": "Ondo Finance"}, "issuer-id")]).json()
    record = client.get(f"/api/v1/registry/imports/{batch['id']}").json()["records"][0]
    response = client.post(f"/api/v1/registry/imports/records/{record['id']}/decision", json={
        "action": "link_existing", "reviewer": "reviewer", "target_entity_id": issuer["id"],
        "evidence_ref": "https://issuer.example/identity"})
    assert response.status_code == 200 and response.json()["resolved_entity_id"] == issuer["id"]


def test_rejection_requires_reason_and_is_audited(client):
    batch = stage(client, [row("issuer", "issuer-1", {
        "canonical_key": "issuer:example", "legal_name": "Example"}, "issuer-id")]).json()
    record = client.get(f"/api/v1/registry/imports/{batch['id']}").json()["records"][0]
    endpoint = f"/api/v1/registry/imports/records/{record['id']}/decision"
    assert client.post(endpoint, json={"action": "reject", "reviewer": "reviewer"}).status_code == 422
    rejected = client.post(endpoint, json={"action": "reject", "reviewer": "reviewer",
        "note": "Insufficient issuer evidence"})
    assert rejected.status_code == 200 and rejected.json()["status"] == "rejected"
    events = client.get(f"/api/v1/registry/imports/{batch['id']}/audit").json()
    assert events[-1]["action"] == "record_rejected"


def test_duplicate_source_rows_are_retained_and_marked_duplicate(client):
    payload = {"canonical_key": "equity:nvidia", "display_name": "NVIDIA", "asset_type": "equity"}
    batch = stage(client, [row("underlying", "same-source-id", payload, "asset-id"),
        row("underlying", "same-source-id", payload, "asset-id")]).json()
    records = client.get(f"/api/v1/registry/imports/{batch['id']}").json()["records"]
    assert [record["status"] for record in records] == ["needs_review", "duplicate"]


def test_decision_cannot_be_applied_twice(client):
    batch = stage(client, [row("issuer", "issuer-1", {
        "canonical_key": "issuer:example", "legal_name": "Example"}, "issuer-id")]).json()
    record = client.get(f"/api/v1/registry/imports/{batch['id']}").json()["records"][0]
    endpoint = f"/api/v1/registry/imports/records/{record['id']}/decision"
    decision = {"action": "create_new", "reviewer": "reviewer", "evidence_ref": "evidence:1"}
    assert client.post(endpoint, json=decision).status_code == 200
    assert client.post(endpoint, json=decision).status_code == 409


def test_import_routes_require_admin_token(client):
    assert TestClient(app).get("/api/v1/registry/imports").status_code == 401




@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("REGISTRY_ADMIN_TOKEN", "test-admin-token")
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    testing_session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        test_client.headers.update({"X-Registry-Admin-Token": "test-admin-token"})
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

 
 
def test_exact_unverified_provider_alias_requires_human_approval_and_is_promoted(client):
    underlying = client.post("/api/v1/registry/underlyings", json={
        "canonical_key": "equity:nvidia", "display_name": "NVIDIA", "asset_type": "equity"}).json()
    alias = client.post("/api/v1/registry/aliases", json={
        "provider": "provider-x", "namespace": "asset-id", "external_id": "nvda-feed",
        "effective_from": "2026-01-01", "entity_type": "underlying",
        "entity_id": underlying["id"], "evidence_ref": "evidence:initial", "is_verified": False})
    assert alias.status_code == 201
    batch = stage(client, [row("underlying", "nvda-feed", {
        "canonical_key": "equity:nvidia", "display_name": "NVIDIA", "asset_type": "equity"
    }, "asset-id")]).json()
    record = client.get(f"/api/v1/registry/imports/{batch['id']}").json()["records"][0]
    assert record["status"] == "needs_review"
    assert any("exact_provider_alias_unverified" in c["match_basis"] for c in record["candidates"])
    decision = client.post(f"/api/v1/registry/imports/records/{record['id']}/decision", json={
        "action": "link_existing", "reviewer": "reviewer", "target_entity_id": underlying["id"],
        "evidence_ref": "https://issuer.example/asset-identity"})
    assert decision.status_code == 200
    aliases = [a for a in client.get("/api/v1/registry/aliases").json() if a["external_id"] == "nvda-feed"]
    assert len(aliases) == 1 and aliases[0]["is_verified"] is True
    assert aliases[0]["evidence_ref"] == "https://issuer.example/asset-identity"



def test_issuer_scoped_native_product_id_is_an_exact_candidate(client):
    underlying = client.post("/api/v1/registry/underlyings", json={
        "canonical_key": "equity:nvidia", "display_name": "NVIDIA", "asset_type": "equity"}).json()
    issuer = client.post("/api/v1/registry/issuers", json={
        "canonical_key": "issuer:ondo", "legal_name": "Ondo"}).json()
    product = client.post("/api/v1/registry/products", json={
        "canonical_key": "product:ondo:nvdax", "issuer_id": issuer["id"],
        "underlying_id": underlying["id"], "native_product_id": "NVDAx",
        "display_name": "NVDAx", "symbol": "NVDA", "instrument_form": "tokenized_equity",
        "unit_description": "one token"}).json()
    batch = stage(client, [row("issuer_product", "source-nvdax", {
        "canonical_key": "product:incoming:nvdax", "issuer_id": issuer["id"],
        "underlying_id": underlying["id"], "native_product_id": "NVDAx",
        "display_name": "NVDAx token", "symbol": "NVDA", "instrument_form": "tokenized_equity",
        "unit_description": "one token"}, "native-product-id")]).json()
    record = client.get(f"/api/v1/registry/imports/{batch['id']}").json()["records"][0]
    assert any("exact_issuer_native_product_id" in c["match_basis"]
               and c["candidate_entity_id"] == product["id"] for c in record["candidates"])
    assert record["status"] == "needs_review"


def test_deployment_import_creates_normalized_record_only_after_approval(client):
    underlying = client.post("/api/v1/registry/underlyings", json={
        "canonical_key": "equity:nvidia", "display_name": "NVIDIA", "asset_type": "equity"}).json()
    issuer = client.post("/api/v1/registry/issuers", json={
        "canonical_key": "issuer:ondo", "legal_name": "Ondo"}).json()
    product = client.post("/api/v1/registry/products", json={
        "canonical_key": "product:ondo:nvdax", "issuer_id": issuer["id"],
        "underlying_id": underlying["id"], "native_product_id": "NVDAx",
        "display_name": "NVDAx", "instrument_form": "tokenized_equity",
        "unit_description": "one token"}).json()
    network = client.post("/api/v1/registry/networks", json={
        "namespace": "eip155:1", "display_name": "Ethereum", "family": "evm"}).json()
    address = "0x" + "A" * 40
    batch = stage(client, [row("deployment", "nvda-deployment-1", {
        "issuer_product_id": product["id"], "network_id": network["id"],
        "native_identifier": address, "representation_type": "independent_issuance",
        "is_verified": False}, "contract-address")]).json()
    record = client.get(f"/api/v1/registry/imports/{batch['id']}").json()["records"][0]
    assert record["status"] == "needs_review"
    decision = client.post(f"/api/v1/registry/imports/records/{record['id']}/decision", json={
        "action": "create_new", "reviewer": "reviewer", "evidence_ref": "evidence:deployment"})
    assert decision.status_code == 200
    deployments = client.get("/api/v1/registry/deployments").json()
    created = [item for item in deployments if item["native_identifier"] == address]
    assert len(created) == 1 and created[0]["normalized_identifier"] == address.lower()
    assert created[0]["is_verified"] is False


def test_oversized_import_payload_is_rejected_without_creating_batch(client):
    response = stage(client, [row("underlying", "large-row", {
        "canonical_key": "equity:large", "display_name": "X" * 50_100, "asset_type": "equity"
    }, "asset-id")])
    assert response.status_code == 413
    assert client.get("/api/v1/registry/imports").json() == []



def test_create_new_product_rejects_unknown_parent_references(client):
    batch = stage(client, [row("issuer_product", "new-product-id", {
        "canonical_key": "product:missing:nvda", "issuer_id": "missing-issuer",
        "underlying_id": "missing-underlying", "native_product_id": "NVDAx",
        "display_name": "NVDAx", "instrument_form": "tokenized_equity",
        "unit_description": "one token"}, "native-product-id")]).json()
    record = client.get(f"/api/v1/registry/imports/{batch['id']}").json()["records"][0]
    response = client.post(f"/api/v1/registry/imports/records/{record['id']}/decision", json={
        "action": "create_new", "reviewer": "reviewer", "evidence_ref": "evidence:product"})
    assert response.status_code == 404
    assert client.get("/api/v1/registry/products").json() == []
