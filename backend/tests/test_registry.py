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
        "entity_type":"underlying","entity_id":underlying["id"],"effective_from":"2026-01-01","is_verified":True}
    assert client.post("/api/v1/registry/aliases", json=payload).status_code == 201
    assert client.post("/api/v1/registry/aliases", json=payload).status_code == 409
    payload["external_id"] = "unmapped"
    payload["entity_id"] = "not-a-real-id"
    assert client.post("/api/v1/registry/aliases", json=payload).status_code == 404

def test_alias_resolution_is_exact_not_symbol_fuzzy(client):
    underlying, _, _ = create_base_entities(client)
    client.post("/api/v1/registry/aliases", json={"provider":"coingecko","namespace":"coin","external_id":"nvidia-tokenized","entity_type":"underlying","entity_id":underlying["id"],"effective_from":"2026-01-01"})
    found = client.get("/api/v1/registry/aliases/resolve", params={"provider":"coingecko","namespace":"coin","external_id":"nvidia-tokenized"})
    missing = client.get("/api/v1/registry/aliases/resolve", params={"provider":"coingecko","namespace":"coin","external_id":"NVDA"})
    assert found.status_code == 200
    assert missing.status_code == 404

def test_unknown_ids_are_not_resolved_to_default_entities(client):
    response = client.get("/api/v1/registry/entities/underlying/not-a-real-id")
    assert response.status_code == 404

def test_provider_alias_effective_periods_resolve_historical_targets(client):
    underlying, _, _ = create_base_entities(client)
    second = client.post("/api/v1/registry/underlyings", json={
        "canonical_key":"equity:nvidia-adr","display_name":"NVIDIA ADR","asset_type":"equity"
    }).json()
    first_alias = {
        "provider":"coingecko","namespace":"symbol","external_id":"NVDA",
        "entity_type":"underlying","entity_id":underlying["id"],
        "effective_from":"2026-01-01",
    }
    created = client.post("/api/v1/registry/aliases", json=first_alias)
    assert created.status_code == 201
    closed = client.patch(
        f"/api/v1/registry/aliases/{created.json()['id']}/close",
        json={"effective_to":"2026-06-01"},
    )
    assert closed.status_code == 200
    second_alias = {**first_alias,"entity_id":second["id"],"effective_from":"2026-06-01"}
    assert client.post("/api/v1/registry/aliases", json=second_alias).status_code == 201

    before_change = client.get("/api/v1/registry/aliases/resolve", params={
        "provider":"coingecko","namespace":"symbol","external_id":"NVDA","as_of":"2026-05-31"
    })
    after_change = client.get("/api/v1/registry/aliases/resolve", params={
        "provider":"coingecko","namespace":"symbol","external_id":"NVDA","as_of":"2026-06-01"
    })
    before_start = client.get("/api/v1/registry/aliases/resolve", params={
        "provider":"coingecko","namespace":"symbol","external_id":"NVDA","as_of":"2025-12-31"
    })
    assert before_change.status_code == 200
    assert before_change.json()["entity_id"] == underlying["id"]
    assert after_change.status_code == 200
    assert after_change.json()["entity_id"] == second["id"]
    assert before_start.status_code == 404

def test_provider_alias_rejects_overlapping_effective_periods(client):
    underlying, _, _ = create_base_entities(client)
    second = client.post("/api/v1/registry/underlyings", json={
        "canonical_key":"equity:nvidia-adr","display_name":"NVIDIA ADR","asset_type":"equity"
    }).json()
    first = {
        "provider":"coingecko","namespace":"name","external_id":"NVIDIA",
        "entity_type":"underlying","entity_id":underlying["id"],
        "effective_from":"2026-01-01","effective_to":None,
    }
    overlapping = {**first,"entity_id":second["id"],"effective_from":"2027-01-01"}
    assert client.post("/api/v1/registry/aliases", json=first).status_code == 201
    assert client.post("/api/v1/registry/aliases", json=overlapping).status_code == 409

def test_provider_alias_requires_valid_effective_period(client):
    underlying, _, _ = create_base_entities(client)
    invalid = {
        "provider":"coingecko","namespace":"symbol","external_id":"NVDA",
        "entity_type":"underlying","entity_id":underlying["id"],
        "effective_from":"2026-06-01","effective_to":"2026-06-01",
    }
    assert client.post("/api/v1/registry/aliases", json=invalid).status_code == 422

def test_provider_alias_cannot_be_closed_twice_or_before_its_start(client):
    underlying, _, _ = create_base_entities(client)
    created = client.post("/api/v1/registry/aliases", json={
        "provider":"coingecko","namespace":"symbol","external_id":"NVDA",
        "entity_type":"underlying","entity_id":underlying["id"],
        "effective_from":"2026-01-01",
    }).json()
    invalid = client.patch(
        f"/api/v1/registry/aliases/{created['id']}/close",
        json={"effective_to":"2025-12-31"},
    )
    assert invalid.status_code == 422
    closed = client.patch(
        f"/api/v1/registry/aliases/{created['id']}/close",
        json={"effective_to":"2026-06-01"},
    )
    assert closed.status_code == 200
    repeated = client.patch(
        f"/api/v1/registry/aliases/{created['id']}/close",
        json={"effective_to":"2026-07-01"},
    )
    assert repeated.status_code == 409



def create_perpetual(client, venue, market_id, symbol, key, domain="", builder_id=None):
    return client.post("/api/v1/registry/perpetual-contracts", json={
        "canonical_key": key,
        "venue_id": venue["id"],
        "native_market_id": market_id,
        "native_symbol": symbol,
        "domain": domain,
        "builder_id": builder_id,
    })


def test_perpetual_contract_migration_preserves_distinct_native_identities(client):
    venue = client.post("/api/v1/registry/venues", json={
        "canonical_key": "venue:hyperliquid", "display_name": "Hyperliquid", "venue_type": "perp_dex"
    }).json()
    predecessor = create_perpetual(
        client, venue, "0x123", "NVDA-PERP", "perp:hl:nvda-old", domain="km", builder_id="km"
    ).json()
    successor = create_perpetual(
        client, venue, "0x456", "NVDA-USD-PERP", "perp:hl:nvda-new", domain="km", builder_id="km"
    ).json()
    assert predecessor["id"] != successor["id"]
    created = client.post("/api/v1/registry/perpetual-contract-migrations", json={
        "predecessor_contract_id": predecessor["id"],
        "successor_contract_id": successor["id"],
        "event_type": "market_id_changed",
        "effective_at": "2026-07-01",
        "source": "official_venue_notice",
        "evidence_ref": "https://venue.example/market-migration",
        "is_verified": True,
    })
    assert created.status_code == 201
    assert created.json()["predecessor_contract_id"] == predecessor["id"]
    assert created.json()["successor_contract_id"] == successor["id"]
    listed = client.get("/api/v1/registry/perpetual-contract-migrations")
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    # The migration is a relationship record; it does not rewrite either contract.
    contracts = {item["id"]: item for item in client.get("/api/v1/registry/perpetual-contracts").json()}
    assert contracts[predecessor["id"]]["native_market_id"] == "0x123"
    assert contracts[successor["id"]]["native_market_id"] == "0x456"
    assert contracts[predecessor["id"]]["domain"] == contracts[successor["id"]]["domain"] == "km"


def test_perpetual_contract_migration_rejects_cycles_and_self_links(client):
    venue = client.post("/api/v1/registry/venues", json={
        "canonical_key": "venue:hyperliquid", "display_name": "Hyperliquid", "venue_type": "perp_dex"
    }).json()
    first = create_perpetual(client, venue, "1", "A-PERP", "perp:a").json()
    second = create_perpetual(client, venue, "2", "A2-PERP", "perp:a2").json()
    third = create_perpetual(client, venue, "3", "A3-PERP", "perp:a3").json()

    def migration(source, target, date_value):
        return {
            "predecessor_contract_id": source,
            "successor_contract_id": target,
            "event_type": "replaced",
            "effective_at": date_value,
            "source": "venue_notice",
            "evidence_ref": "notice-123",
        }

    assert client.post("/api/v1/registry/perpetual-contract-migrations", json=migration(first["id"], second["id"], "2026-01-01")).status_code == 201
    assert client.post("/api/v1/registry/perpetual-contract-migrations", json=migration(second["id"], third["id"], "2026-02-01")).status_code == 201
    cycle = client.post("/api/v1/registry/perpetual-contract-migrations", json=migration(third["id"], first["id"], "2026-03-01"))
    assert cycle.status_code == 409
    self_link = client.post("/api/v1/registry/perpetual-contract-migrations", json=migration(first["id"], first["id"], "2026-04-01"))
    assert self_link.status_code == 422


def test_perpetual_contract_delisting_is_terminal_and_evidence_bearing(client):
    venue = client.post("/api/v1/registry/venues", json={
        "canonical_key": "venue:kraken", "display_name": "Kraken", "venue_type": "centralized_exchange"
    }).json()
    contract = create_perpetual(client, venue, "PI_XBTUSD", "XBT/USD:USD", "perp:kraken:xbt").json()
    payload = {
        "predecessor_contract_id": contract["id"],
        "successor_contract_id": None,
        "event_type": "delisted",
        "effective_at": "2026-08-01",
        "source": "official_venue_notice",
        "evidence_ref": "notice-delisting",
    }
    created = client.post("/api/v1/registry/perpetual-contract-migrations", json=payload)
    assert created.status_code == 201
    assert created.json()["successor_contract_id"] is None
    invalid = {**payload, "successor_contract_id": contract["id"]}
    assert client.post("/api/v1/registry/perpetual-contract-migrations", json=invalid).status_code == 422
    missing_successor = {**payload, "event_type": "replaced"}
    assert client.post("/api/v1/registry/perpetual-contract-migrations", json=missing_successor).status_code == 422


def test_perpetual_contract_migration_requires_existing_contracts_and_evidence(client):
    payload = {
        "predecessor_contract_id": "missing",
        "successor_contract_id": "missing-too",
        "event_type": "replaced",
        "effective_at": "2026-01-01",
        "source": "venue",
        "evidence_ref": "notice",
    }
    assert client.post("/api/v1/registry/perpetual-contract-migrations", json=payload).status_code == 404
    del payload["evidence_ref"]
    assert client.post("/api/v1/registry/perpetual-contract-migrations", json=payload).status_code == 422
