# Backend — RWAs Intelligence API

First backend increment: a canonical identity registry. It is not a market-data API and contains no seeded/mock assets.

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
- Provider aliases are unique by provider + namespace + external ID and must target an existing canonical entity.
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
- Provider aliases: POST/GET /api/v1/registry/aliases

This increment deliberately omits update/delete endpoints, provider ingestion, public registration, authentication and market metrics. Registry mutations are administrative and must be protected before any shared environment is exposed.
