import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import Base

ADMIN = {"X-Registry-Admin-Token": "test-admin-token"}
EVIDENCE = "Issuer token list lists this mint address for NVDA."
CONTRACT = "0x" + "ab" * 20


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
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


def make_deployment(client):
    post = client.post
    underlying = post("/api/v1/registry/underlyings", json={
        "canonical_key": "equity:nvidia", "display_name": "NVIDIA", "asset_type": "equity"}).json()
    issuer = post("/api/v1/registry/issuers", json={
        "canonical_key": "issuer:ondo", "legal_name": "Ondo"}).json()
    product = post("/api/v1/registry/products", json={
        "canonical_key": "product:ondo:nvdaon", "issuer_id": issuer["id"],
        "underlying_id": underlying["id"], "native_product_id": "NVDAon",
        "display_name": "NVIDIA on Ondo", "symbol": "NVDA",
        "instrument_form": "tokenized_equity", "unit_description": "issuer-defined unit",
        "representation_type": "independent_issuance"}).json()
    network = post("/api/v1/registry/networks", json={
        "namespace": "eip155:1", "display_name": "Ethereum", "family": "evm"}).json()
    deployment = post("/api/v1/registry/deployments", json={
        "issuer_product_id": product["id"], "network_id": network["id"],
        "native_identifier": CONTRACT}).json()
    return deployment, network


def body(verified=True, evidence=EVIDENCE):
    return {"verified": verified, "evidence_ref": evidence, "verified_by": "reviewer"}


def test_verification_requires_admin_token(client, monkeypatch):
    deployment, _ = make_deployment(client)
    url = f"/api/v1/registry/deployments/{deployment['id']}/verification"
    assert client.post(url, json=body()).status_code == 401
    assert client.post(url, json=body(), headers={"X-Registry-Admin-Token": "wrong"}).status_code == 401
    monkeypatch.delenv("REGISTRY_ADMIN_TOKEN")
    assert client.post(url, json=body(), headers=ADMIN).status_code == 503


def test_verification_needs_evidence_and_known_deployment(client):
    deployment, _ = make_deployment(client)
    url = f"/api/v1/registry/deployments/{deployment['id']}/verification"
    assert client.post(url, json=body(evidence="short"), headers=ADMIN).status_code == 422
    assert client.post(url, json={"verified_by": "x"}, headers=ADMIN).status_code == 422
    missing = "/api/v1/registry/deployments/does-not-exist/verification"
    assert client.post(missing, json=body(), headers=ADMIN).status_code == 404


def classify_as_rwa(client, deployment):
    return client.post("/api/v1/registry/classifications", json={
        "entity_type": "issuer_product", "entity_id": deployment["issuer_product_id"],
        "classification": "rwa", "effective_from": "2026-01-01",
        "source": "test", "evidence_ref": "test classification evidence"})


def test_verified_deployment_satisfies_network_filter_and_facet(client):
    deployment, network = make_deployment(client)
    assert classify_as_rwa(client, deployment).status_code == 201
    catalogue = "/api/v1/catalogue/tokenized-products"
    before = client.get(catalogue, params={"network_id": network["id"]}).json()
    assert before["total"] == 0
    assert before["facets"]["networks"] == []
    url = f"/api/v1/registry/deployments/{deployment['id']}/verification"
    assert client.post(url, json=body(), headers=ADMIN).status_code == 201
    after = client.get(catalogue, params={"network_id": network["id"]}).json()
    assert after["total"] == 1
    assert [n["id"] for n in after["facets"]["networks"]] == [network["id"]]
    assert after["items"][0]["deployments"][0]["is_verified"] is True


def test_revocation_keeps_history_and_clears_flag(client):
    deployment, _ = make_deployment(client)
    base = f"/api/v1/registry/deployments/{deployment['id']}"
    assert client.post(base + "/verification", json=body(), headers=ADMIN).status_code == 201
    revoke = body(verified=False, evidence="Issuer removed this address from its list.")
    assert client.post(base + "/verification", json=revoke, headers=ADMIN).status_code == 201
    events = client.get(base + "/verification-events").json()
    assert [e["verified"] for e in events] == [True, False]
    assert events[0]["evidence_ref"] == EVIDENCE
    deployments = client.get("/api/v1/registry/deployments").json()
    assert deployments[0]["is_verified"] is False
