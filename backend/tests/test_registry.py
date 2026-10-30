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

def create_base_entities(client):
    underlying = client.post("/api/v1/registry/underlyings", json={"canonical_key":"equity:nvidia","display_name":"NVIDIA","asset_type":"equity"})
    issuer_a = client.post("/api/v1/registry/issuers", json={"canonical_key":"issuer:ondo","legal_name":"Ondo Finance"})
    issuer_b = client.post("/api/v1/registry/issuers", json={"canonical_key":"issuer:backed","legal_name":"Backed"})
    assert underlying.status_code == issuer_a.status_code == issuer_b.status_code == 201
    return underlying.json(), issuer_a.json(), issuer_b.json()

def create_product(client, issuer, underlying, native_id="NVDAx", key="product:ondo:nvdax"):
    return client.post("/api/v1/registry/products", json={
        "canonical_key":key,"issuer_id":issuer["id"],"underlying_id":underlying["id"],
        "native_product_id":native_id,"display_name":native_id,"symbol":"NVDA",
        "instrument_form":"tokenized_equity","unit_description":"one token represents issuer-defined exposure",
        "representation_type":"independent_issuance"})

def test_distinct_issuer_products_share_underlying_without_merging(client):
    underlying, issuer_a, issuer_b = create_base_entities(client)
    product_a = create_product(client, issuer_a, underlying)
    product_b = create_product(client, issuer_b, underlying, "NVDAon", "product:backed:nvdaon")
    assert product_a.status_code == product_b.status_code == 201
    assert product_a.json()["id"] != product_b.json()["id"]
    assert product_a.json()["underlying_id"] == product_b.json()["underlying_id"] == underlying["id"]

def test_same_issuer_native_product_cannot_be_registered_twice(client):
    underlying, issuer, _ = create_base_entities(client)
    assert create_product(client, issuer, underlying).status_code == 201
    assert create_product(client, issuer, underlying, "NVDAx", "product:duplicate:nvdax").status_code == 409

def test_product_requires_real_issuer_and_underlying(client):
    response = client.post("/api/v1/registry/products", json={
        "canonical_key":"product:unknown","issuer_id":"missing-issuer","underlying_id":"missing-underlying",
        "native_product_id":"unknown","display_name":"Unknown","instrument_form":"token","unit_description":"unknown"})
    assert response.status_code == 404

def test_evm_deployment_normalizes_address_and_prevents_duplicate(client):
    underlying, issuer, _ = create_base_entities(client)
    product = create_product(client, issuer, underlying).json()
    network = client.post("/api/v1/registry/networks", json={"namespace":"eip155:1","display_name":"Ethereum","family":"evm"}).json()
    address = "0x" + "A" * 40
    created = client.post("/api/v1/registry/deployments", json={"issuer_product_id":product["id"],"network_id":network["id"],"native_identifier":address})
    assert created.status_code == 201
    assert created.json()["normalized_identifier"] == address.lower()
    duplicate = client.post("/api/v1/registry/deployments", json={"issuer_product_id":product["id"],"network_id":network["id"],"native_identifier":address.lower()})
    assert duplicate.status_code == 409

def test_invalid_evm_address_is_rejected(client):
    underlying, issuer, _ = create_base_entities(client)
    product = create_product(client, issuer, underlying).json()
    network = client.post("/api/v1/registry/networks", json={"namespace":"eip155:1","display_name":"Ethereum","family":"evm"}).json()
    response = client.post("/api/v1/registry/deployments", json={"issuer_product_id":product["id"],"network_id":network["id"],"native_identifier":"0x1234"})
    assert response.status_code == 422

def test_non_evm_identifiers_are_preserved_case_sensitively(client):
    underlying, issuer, _ = create_base_entities(client)
    network = client.post("/api/v1/registry/networks", json={"namespace":"solana:mainnet","display_name":"Solana","family":"solana"}).json()
    product = create_product(client, issuer, underlying, "sample-mint", "product:solana:sample").json()
    mint = "AbCdEf123456"
    response = client.post("/api/v1/registry/deployments", json={"issuer_product_id":product["id"],"network_id":network["id"],"native_identifier":mint})
    assert response.status_code == 201
    assert response.json()["normalized_identifier"] == mint

def test_builder_scoped_perpetual_requires_domain(client):
    venue = client.post("/api/v1/registry/venues", json={"canonical_key":"venue:hyperliquid","display_name":"Hyperliquid","venue_type":"perp_dex"}).json()
    response = client.post("/api/v1/registry/perpetual-contracts", json={
        "canonical_key":"perp:km:nvda","venue_id":venue["id"],"native_market_id":"NVDA",
        "native_symbol":"NVDA-PERP","builder_id":"km","domain":""})
    assert response.status_code == 422

def test_provider_alias_is_unique_and_target_must_exist(client):
    underlying, _, _ = create_base_entities(client)
    payload = {"provider":"coingecko","namespace":"coin","external_id":"nvidia-tokenized",
        "entity_type":"underlying","entity_id":underlying["id"],"is_verified":True}
    assert client.post("/api/v1/registry/aliases", json=payload).status_code == 201
    assert client.post("/api/v1/registry/aliases", json=payload).status_code == 409
    payload["external_id"] = "unmapped"
    payload["entity_id"] = "not-a-real-id"
    assert client.post("/api/v1/registry/aliases", json=payload).status_code == 404

def test_alias_resolution_is_exact_not_symbol_fuzzy(client):
    underlying, _, _ = create_base_entities(client)
    client.post("/api/v1/registry/aliases", json={"provider":"coingecko","namespace":"coin","external_id":"nvidia-tokenized","entity_type":"underlying","entity_id":underlying["id"]})
    found = client.get("/api/v1/registry/aliases/resolve", params={"provider":"coingecko","namespace":"coin","external_id":"nvidia-tokenized"})
    missing = client.get("/api/v1/registry/aliases/resolve", params={"provider":"coingecko","namespace":"coin","external_id":"NVDA"})
    assert found.status_code == 200
    assert missing.status_code == 404

def test_unknown_ids_are_not_resolved_to_default_entities(client):
    response = client.get("/api/v1/registry/entities/underlying/not-a-real-id")
    assert response.status_code == 404
