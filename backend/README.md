# Backend — RWAs Intelligence API

The backend provides a canonical identity registry and a read-only tokenized-product catalogue. It is not a market-data API and contains no seeded/mock assets.

## Requirements

- Python 3.12+
- PostgreSQL 16+ for shared, staging and production environments
- SQLite is supported only for isolated automated tests and local experiments

## Local setup

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements-dev.txt
export DATABASE_URL='postgresql+psycopg://postgres:postgres@localhost:5432/rwa_intelligence'
cd backend
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Open /docs for the generated OpenAPI contract and /healthz for process health.

## Identity rules implemented

- Underlyings, issuers, issuer products, deployments, networks, venues and perpetual contracts have separate internal UUIDs.
- An issuer product is unique by issuer + native product ID. Products from different issuers may share one underlying without merging.
- A deployment is unique by network + normalized native contract/mint identifier.
- EVM addresses are validated as 20-byte hexadecimal addresses and normalized to lowercase for identity comparison.
- Non-EVM identifiers are preserved exactly; Solana mint identifiers are case-sensitive.
- Provider aliases target an existing canonical entity and are effective-dated; the same provider + namespace + external ID cannot have overlapping periods.
- Alias resolution is exact and accepts an optional `as_of` date. Use provider namespaces such as `symbol` and `name` for exact aliases; no fuzzy matching is performed.
- Builder-scoped perpetual contracts require an exact domain. Native market IDs remain distinct from display symbols.
- Unknown IDs are not redirected to a default asset.

The API does not infer legal ownership, backing, redemption rights, bridge equivalence or complete network support. Verification and representation type are explicit inputs and require evidence review before operational use.

## Routes

- Underlyings: POST/GET /api/v1/registry/underlyings
- Issuers: POST/GET /api/v1/registry/issuers
- Issuer products: POST/GET /api/v1/registry/products
- Networks: POST/GET /api/v1/registry/networks
- Deployments: POST/GET /api/v1/registry/deployments
- Venues: POST/GET /api/v1/registry/venues
- Perpetual contracts: POST/GET /api/v1/registry/perpetual-contracts
- Provider aliases: POST/GET /api/v1/registry/aliases (effective_from required; effective_to optional)
- Close an alias period once: PATCH /api/v1/registry/aliases/{alias_id}/close with `effective_to`.
- Exact alias resolution: GET /api/v1/registry/aliases/resolve?provider=...&namespace=...&external_id=...&as_of=YYYY-MM-DD

This increment deliberately omits general update/delete endpoints, provider ingestion, public registration, authentication and market metrics. The close-period endpoint is the sole controlled temporal correction for aliases. Registry mutations are administrative and must be protected before any shared environment is exposed.

## Read-only tokenized product catalogue

`GET /api/v1/catalogue/tokenized-products` returns issuer products with an effective RWA classification, canonical underlying and issuer identity, and product-specific deployment records.

Supported query parameters: `q`, `issuer_id`, `network_id`, `sort` (`underlying|issuer|product`), `direction` (`asc|desc`), `limit` (1–100), `offset` and optional `as_of` date.

Important semantics:
- One result row represents one issuer product, not one network deployment.
- Network filters match only product-specific deployments marked verified.
- Unverified deployments remain visible in product detail but do not satisfy a network filter.
- Classification source, evidence reference and effective period are returned.
- The response explicitly marks provider-universe coverage as unknown. `total` counts matching registry records only.
- Price, tokenized value, supply, volume, liquidity and return history are not included because validated observation services do not yet exist.

This is a read-only catalogue route, not permission to expose the current unauthenticated registry mutation routes publicly.
