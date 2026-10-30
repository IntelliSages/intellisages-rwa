import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import get_db
from app.main import app
from app.models import Base

@pytest.fixture()
def client():
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

def base_product(client):
    u = client.post("/api/v1/registry/underlyings", json={"canonical_key":"equity:nvidia","display_name":"NVIDIA","asset_type":"equity"}).json()
    i = client.post("/api/v1/registry/issuers", json={"canonical_key":"issuer:ondo","legal_name":"Ondo"}).json()
    p = client.post("/api/v1/registry/products", json={"canonical_key":"product:ondo:nvdax","issuer_id":i["id"],"underlying_id":u["id"],"native_product_id":"NVDAx","display_name":"NVDAx","instrument_form":"tokenized_equity","unit_description":"one token"})
    assert p.status_code == 201
    return u, p.json()

def test_supply_group_requires_evidence_and_preserves_product_identity(client):
    u, p = base_product(client)
    group = client.post("/api/v1/registry/supply-groups", json={"canonical_key":"supply:nvidia","display_name":"NVIDIA economic supply","methodology_notes":"Group only after documented equivalence evidence."})
    assert group.status_code == 201
    payload = {"group_id":group.json()["id"],"issuer_product_id":p["id"],"membership_type":"wrapper","effective_from":"2026-01-01","evidence_ref":"https://issuer.example/legal/terms","is_verified":False}
    created = client.post("/api/v1/registry/supply-memberships", json=payload)
    assert created.status_code == 201
    assert created.json()["is_verified"] is False
    assert client.post("/api/v1/registry/supply-memberships", json=payload).status_code == 409

def test_supply_membership_periods_cannot_overlap(client):
    _, p = base_product(client)
    group = client.post("/api/v1/registry/supply-groups", json={"canonical_key":"supply:nvidia","display_name":"NVIDIA","methodology_notes":"Evidence-led grouping."}).json()
    base = {"group_id":group["id"],"issuer_product_id":p["id"],"membership_type":"bridge","effective_from":"2026-01-01","effective_to":"2026-06-01","evidence_ref":"evidence:1"}
    assert client.post("/api/v1/registry/supply-memberships", json=base).status_code == 201
    adjacent = {**base,"group_id":group["id"],"effective_from":"2026-06-01","effective_to":"2026-08-01"}
    assert client.post("/api/v1/registry/supply-memberships", json=adjacent).status_code == 201

def test_classification_is_versioned_and_periods_do_not_overlap(client):
    u, p = base_product(client)
    base = {"entity_type":"issuer_product","entity_id":p["id"],"classification":"rwa","effective_from":"2026-01-01","effective_to":"2026-06-01","source":"issuer registry","evidence_ref":"evidence:classification:1","provider_global_included":False}
    assert client.post("/api/v1/registry/classifications", json=base).status_code == 201
    next_period = {**base,"classification":"rwa","effective_from":"2026-06-01","effective_to":None,"evidence_ref":"evidence:classification:2","provider_global_included":True}
    assert client.post("/api/v1/registry/classifications", json=next_period).status_code == 201
    overlap = {**base,"effective_from":"2026-05-01","effective_to":"2026-07-01"}
    assert client.post("/api/v1/registry/classifications", json=overlap).status_code == 409
    assert client.get("/api/v1/registry/classifications",params={"entity_type":"issuer_product","entity_id":p["id"]}).json().__len__() == 2

def test_open_ended_classification_period_blocks_later_period(client):
    _, p = base_product(client)
    open_period = {"entity_type":"issuer_product","entity_id":p["id"],"classification":"rwa","effective_from":"2026-01-01","source":"issuer source","evidence_ref":"evidence:open"}
    assert client.post("/api/v1/registry/classifications", json=open_period).status_code == 201
    later = {**open_period,"effective_from":"2027-01-01","evidence_ref":"evidence:later"}
    assert client.post("/api/v1/registry/classifications", json=later).status_code == 409

def test_adjacent_classification_periods_are_allowed(client):
    _, p = base_product(client)
    first = {"entity_type":"issuer_product","entity_id":p["id"],"classification":"rwa","effective_from":"2026-01-01","effective_to":"2026-06-01","source":"issuer source","evidence_ref":"evidence:first"}
    second = {**first,"classification":"other","effective_from":"2026-06-01","effective_to":None,"evidence_ref":"evidence:second"}
    assert client.post("/api/v1/registry/classifications", json=first).status_code == 201
    assert client.post("/api/v1/registry/classifications", json=second).status_code == 201

def test_open_ended_membership_period_blocks_later_membership(client):
    _, p = base_product(client)
    group = client.post("/api/v1/registry/supply-groups", json={"canonical_key":"supply:underlying","display_name":"Supply","methodology_notes":"Evidence controlled."}).json()
    first = {"group_id":group["id"],"issuer_product_id":p["id"],"membership_type":"native","effective_from":"2026-01-01","evidence_ref":"evidence:membership"}
    assert client.post("/api/v1/registry/supply-memberships", json=first).status_code == 201
    later = {**first,"effective_from":"2027-01-01","evidence_ref":"evidence:membership-later"}
    assert client.post("/api/v1/registry/supply-memberships", json=later).status_code == 409
