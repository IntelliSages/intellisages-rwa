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
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
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


def create_product(client, *, issuer_key: str, issuer_name: str, product_id: str):
    existing_underlyings = client.get("/api/v1/registry/underlyings").json()
    underlying = next(
        (item for item in existing_underlyings if item["canonical_key"] == "equity:nvidia"),
        None,
    )
    if underlying is None:
        response = client.post(
            "/api/v1/registry/underlyings",
            json={
                "canonical_key": "equity:nvidia",
                "display_name": "NVIDIA",
                "asset_type": "equity",
            },
        )
        assert response.status_code == 201
        underlying = response.json()
    issuer = client.post(
        "/api/v1/registry/issuers",
        json={"canonical_key": issuer_key, "legal_name": issuer_name},
    )
    assert issuer.status_code == 201
    product = client.post(
        "/api/v1/registry/products",
        json={
            "canonical_key": f"product:{issuer_key}:{product_id.lower()}",
            "issuer_id": issuer.json()["id"],
            "underlying_id": underlying["id"],
            "native_product_id": product_id,
            "display_name": product_id,
            "symbol": product_id,
            "instrument_form": "tokenized_equity",
            "unit_description": "one token",
        },
    )
    assert product.status_code == 201
    classification = client.post(
        "/api/v1/registry/classifications",
        json={
            "entity_type": "issuer_product",
            "entity_id": product.json()["id"],
            "classification": "rwa",
            "effective_from": "2026-01-01",
            "effective_to": "2027-01-01",
            "source": "issuer product register",
            "evidence_ref": "evidence:classification:approved",
            "provider_global_included": None,
        },
    )
    assert classification.status_code == 201
    return underlying, issuer.json(), product.json()


def test_catalogue_returns_one_row_per_issuer_product_and_verified_networks(client):
    _, _, product_a = create_product(
        client, issuer_key="issuer:alpha", issuer_name="Alpha Issuer", product_id="NVDAx"
    )
    # A second issuer product against the same underlying remains a separate row.
    _, _, product_b = create_product(
        client, issuer_key="issuer:beta", issuer_name="Beta Issuer", product_id="NVDAon"
    )
    ethereum = client.post(
        "/api/v1/registry/networks",
        json={"namespace": "eip155:1", "display_name": "Ethereum", "family": "evm"},
    ).json()
    solana = client.post(
        "/api/v1/registry/networks",
        json={"namespace": "solana:mainnet", "display_name": "Solana", "family": "solana"},
    ).json()
    for network in (ethereum, solana):
        response = client.post(
            "/api/v1/registry/deployments",
            json={
                "issuer_product_id": product_a["id"],
                "network_id": network["id"],
                "native_identifier": (
                "0x" + "a" * 40
                if network["id"] == ethereum["id"]
                else "So1anaMintCaseSensitive"
            ),
                "representation_type": "wrapper",
                "is_verified": True,
            },
        )
        assert response.status_code == 201

    response = client.get("/api/v1/catalogue/tokenized-products", params={"as_of": "2026-10-30"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    assert {item["id"] for item in payload["items"]} == {product_a["id"], product_b["id"]}
    alpha = next(item for item in payload["items"] if item["id"] == product_a["id"])
    assert {item["network"]["display_name"] for item in alpha["deployments"]} == {
        "Ethereum",
        "Solana",
    }
    assert payload["coverage"]["status"] == "unknown"
    assert "not a provider-complete" in payload["coverage"]["note"]

    paged = client.get(
        "/api/v1/catalogue/tokenized-products",
        params={"as_of": "2026-10-30", "limit": 1, "sort": "product", "direction": "desc"},
    )
    assert paged.status_code == 200
    assert paged.json()["total"] == 2
    assert len(paged.json()["items"]) == 1
    assert paged.json()["has_more"] is True

    network_filtered = client.get(
        "/api/v1/catalogue/tokenized-products",
        params={"as_of": "2026-10-30", "network_id": ethereum["id"]},
    )
    assert network_filtered.status_code == 200
    assert [item["id"] for item in network_filtered.json()["items"]] == [product_a["id"]]


def test_catalogue_excludes_unclassified_and_non_rwa_products(client):
    _, issuer, product = create_product(
        client, issuer_key="issuer:alpha", issuer_name="Alpha Issuer", product_id="NVDAx"
    )
    non_rwa = client.post(
        "/api/v1/registry/products",
        json={
            "canonical_key": "product:alpha:ordinary",
            "issuer_id": issuer["id"],
            "underlying_id": client.get("/api/v1/registry/underlyings").json()[0]["id"],
            "native_product_id": "ORDINARY",
            "display_name": "Ordinary",
            "instrument_form": "token",
            "unit_description": "one token",
        },
    )
    assert non_rwa.status_code == 201
    response = client.get("/api/v1/catalogue/tokenized-products", params={"as_of": "2026-10-30"})
    assert response.status_code == 200
    assert [item["id"] for item in response.json()["items"]] == [product["id"]]


def test_network_filter_uses_only_verified_product_deployments(client):
    _, _, product = create_product(
        client, issuer_key="issuer:alpha", issuer_name="Alpha Issuer", product_id="NVDAx"
    )
    network = client.post(
        "/api/v1/registry/networks",
        json={"namespace": "eip155:8453", "display_name": "Base", "family": "evm"},
    ).json()
    deployment = client.post(
        "/api/v1/registry/deployments",
        json={
            "issuer_product_id": product["id"],
            "network_id": network["id"],
            "native_identifier": "0x" + "c" * 40,
            "representation_type": "unknown",
            "is_verified": False,
        },
    )
    assert deployment.status_code == 201
    response = client.get(
        "/api/v1/catalogue/tokenized-products", params={"as_of": "2026-10-30", "network_id": network["id"]}
    )
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_catalogue_search_facets_pagination_and_effective_date(client):
    _, issuer, product = create_product(
        client, issuer_key="issuer:alpha", issuer_name="Alpha Issuer", product_id="NVDAx"
    )
    # A later, non-overlapping classification period closes the RWA period.
    close = client.post(
        "/api/v1/registry/classifications",
        json={
            "entity_type": "issuer_product",
            "entity_id": product["id"],
            "classification": "other",
            "effective_from": "2027-01-01",
            "source": "classification review",
            "evidence_ref": "evidence:reclassification",
        },
    )
    assert close.status_code == 201
    current = client.get(
        "/api/v1/catalogue/tokenized-products",
        params={"as_of": "2026-10-30", "q": "Alpha", "issuer_id": issuer["id"], "limit": 1, "offset": 0},
    )
    assert current.status_code == 200
    assert current.json()["total"] == 1
    assert current.json()["has_more"] is False
    future = client.get(
        "/api/v1/catalogue/tokenized-products",
        params={"as_of": "2027-01-01"},
    )
    assert future.status_code == 200
    assert future.json()["total"] == 0


def test_catalogue_validates_sort_and_page_bounds(client):
    invalid_sort = client.get(
        "/api/v1/catalogue/tokenized-products", params={"sort": "market_cap"}
    )
    assert invalid_sort.status_code == 422
    invalid_limit = client.get(
        "/api/v1/catalogue/tokenized-products", params={"limit": 500}
    )
    assert invalid_limit.status_code == 422



def test_product_detail_resolves_exact_canonical_id_and_returns_provenance(client):
    _, _, product = create_product(
        client, issuer_key="issuer:alpha", issuer_name="Alpha Issuer", product_id="NVDAx"
    )
    network = client.post(
        "/api/v1/registry/networks",
        json={"namespace": "eip155:1", "display_name": "Ethereum", "family": "evm"},
    ).json()
    deployment = client.post(
        "/api/v1/registry/deployments",
        json={
            "issuer_product_id": product["id"],
            "network_id": network["id"],
            "native_identifier": "0x" + "a" * 40,
            "is_verified": True,
        },
    )
    assert deployment.status_code == 201

    response = client.get(f"/api/v1/catalogue/tokenized-products/{product['id']}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == product["id"]
    assert payload["issuer"]["legal_name"] == "Alpha Issuer"
    assert payload["underlying"]["display_name"] == "NVIDIA"
    assert payload["classification"]["evidence_ref"] == "evidence:classification:approved"
    assert payload["deployments"][0]["is_verified"] is True
    assert payload["unverified_deployment_count"] == 0


def test_product_detail_does_not_resolve_symbols_or_non_rwa_records(client):
    _, _, product = create_product(
        client, issuer_key="issuer:alpha", issuer_name="Alpha Issuer", product_id="NVDAx"
    )
    symbol_lookup = client.get("/api/v1/catalogue/tokenized-products/NVDA")
    unknown_lookup = client.get("/api/v1/catalogue/tokenized-products/not-a-real-id")
    assert symbol_lookup.status_code == 404
    assert unknown_lookup.status_code == 404

    # The product exists, but its RWA classification is no longer effective.
    client.post(
        "/api/v1/registry/classifications",
        json={
            "entity_type": "issuer_product",
            "entity_id": product["id"],
            "classification": "other",
            "effective_from": "2027-01-01",
            "source": "classification review",
            "evidence_ref": "evidence:reclassification",
        },
    )
    future = client.get(
        f"/api/v1/catalogue/tokenized-products/{product['id']}",
        params={"as_of": "2027-01-01"},
    )
    assert future.status_code == 404
