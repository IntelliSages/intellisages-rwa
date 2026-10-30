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


## Staged registry imports and reconciliation

All import administration routes require X-Registry-Admin-Token; configure the server-only REGISTRY_ADMIN_TOKEN secret before use. If it is absent, the import API returns 503 and remains disabled. Never put this token in frontend code or expose it to a browser.

- POST /api/v1/registry/imports stages a batch of up to 500 records. Each row carries an entity type, source namespace, source-native external ID and source payload.
- GET /api/v1/registry/imports lists recent batches.
- GET /api/v1/registry/imports/queue lists unresolved records and their candidates.
- GET /api/v1/registry/imports/{batch_id} reads a batch and its rows.
- GET /api/v1/registry/imports/{batch_id}/audit reads append-only audit events.
- POST /api/v1/registry/imports/records/{record_id}/decision supports link_existing, create_new and reject.

Matching is source-aware and exact: active provider aliases, canonical keys, issuer + native product ID, and network + normalized deployment identifier. Name and symbol equality can surface weak candidates but never authorizes an automatic link. Every row remains pending until a reviewer decides. Approval requires a reviewer identity and evidence reference; accepted source identifiers are written as verified provider aliases in the same database transaction. Rejected rows require a reason. Repeated source identities within one batch are retained and marked duplicate rather than silently dropped.

Batch payloads preserve the original source row as JSON. Audit events record staging, duplicate detection, approval and rejection; there is no update/delete API for audit events. Imports create canonical issuer products and deployments only after review. Product and deployment rows must reference already-existing canonical parent IDs, so import dependencies should be staged/reviewed in order (underlyings and issuers, then products, then deployments).

The import endpoints are administrative and intentionally do not provide a public upload UI. Configure authentication, authorization, secret rotation, audit retention and operational monitoring before connecting them to any shared or production environment. Evidence references are pointers supplied by the reviewer; the API does not independently validate the legal or factual claims at those URLs.


## CoinGecko RWA pilot: snapshot → staged import → human reconciliation

The initial provider adapter uses CoinGecko's dedicated RWA API as a **discovery source**. The provider exposes a tracked RWA list, per-underlying detail with issuer tokens and platform addresses, and an issuer list. The issuer list is corroborating/optional; issuer details embedded in each RWA response are also captured. This pipeline measures CoinGecko's tracked universe only, not every tokenized asset in the market.

Official provider guide: https://www.coingecko.com/learn/tokenized-rwa-data-api-guide  
Relevant endpoints:
- \`GET /api/v3/rwas/list\` — provider-tracked underlying list.
- \`GET /api/v3/rwas/{id}?tokens=true&tokenized_market_data=true\` — underlying detail, issuer tokens and platform-address mappings.
- \`GET /api/v3/rwas/issuers/list\` — optional issuer-list cross-check.

### Configure credentials

Obtain a CoinGecko Demo or Pro API key and configure it in the local shell or secret manager. Never commit it, add it to a snapshot, or paste it into a chat.

\`\`\`bash
export COINGECKO_API_KEY='your-key'
export COINGECKO_BASE_URL='https://api.coingecko.com/api/v3'
export RWA_API_BASE_URL='http://127.0.0.1:8000'
export REGISTRY_ADMIN_TOKEN='the-same-server-side-registry-admin-token'
\`\`\`

The adapter uses the Demo key header for the public API host and the Pro key header for the Pro API host. It uses Python's standard library; no additional runtime dependency is required.

### 1. Fetch a resumable raw snapshot

Run from the \`backend/\` directory:

\`\`\`bash
python -m app.providers.coingecko_pilot snapshot \\
  --output-dir data/provider_snapshots/coingecko/2026-10-30
\`\`\`

The full provider list is used by default. For a small smoke test only, add \`--limit 10\`; a limited snapshot can never be reported as full coverage. The adapter:
- saves the raw list, optional issuer list and each per-RWA detail response;
- checkpoints after every detail call and resumes matching snapshots;
- spaces requests conservatively (default 2.1 seconds), retries 429 and transient 5xx/network failures, and caps each response at 5 MB;
- records failed IDs, source timestamps, endpoint references, response hashes and a manifest;
- never stores the API key in the snapshot.

Raw snapshots are excluded from Git by \`.gitignore\`. Use a new output directory for each new provider snapshot once staging has begun; staged snapshots are immutable.

### 2. Stage underlyings and issuers

\`\`\`bash
python -m app.providers.coingecko_pilot stage \\
  --snapshot-dir data/provider_snapshots/coingecko/2026-10-30 \\
  --phase foundations --submitted-by 'operator@your-company'
\`\`\`

This creates review batches for underlying assets and distinct provider-reported issuers. The legacy \`legal_name\` field receives CoinGecko's issuer label, explicitly marked in source metadata as **not independently verified legal identity**. A reviewer must verify the correct legal entity using issuer/official evidence before approving it.

### 3. Stage network identities

\`\`\`bash
python -m app.providers.coingecko_pilot stage \\
  --snapshot-dir data/provider_snapshots/coingecko/2026-10-30 \\
  --phase networks --submitted-by 'operator@your-company'
\`\`\`

The adapter includes only explicit platform-to-chain mappings (Ethereum, BNB Smart Chain, Polygon PoS, Arbitrum One, Base, Optimism, Avalanche C-Chain and Solana). Unknown CoinGecko platform slugs are reported and are not guessed. Add verified mappings using a JSON object keyed by the exact provider platform slug, then rerun the phase. The selected map is saved in the snapshot manifest and reused automatically during deployment staging:

\`\`\`json
{
  "provider-platform-slug": {
    "namespace": "eip155:12345",
    "display_name": "Verified Chain Name",
    "family": "evm"
  }
}
\`\`\`

Use the actual canonical chain namespace and family; the example values above are illustrative, not a real network mapping.

### 4. Approve foundations and stage issuer products

Inspect the unresolved queue with \`GET /api/v1/registry/imports/queue\`. Approve or reject each row using the evidence-led decision endpoint documented above. Products are not staged until both the exact CoinGecko RWA ID and issuer ID have active, verified provider aliases.

\`\`\`bash
python -m app.providers.coingecko_pilot stage \\
  --snapshot-dir data/provider_snapshots/coingecko/2026-10-30 \\
  --phase products --submitted-by 'operator@your-company'
\`\`\`

Each product is scoped by canonical issuer + CoinGecko token ID and linked to the canonical underlying. The CoinGecko token ID is explicitly recorded as a provisional provider-native product identifier; it is not represented as the issuer's internal product ID. Symbol equality is never used as an identity key. The unit description explicitly leaves legal entitlement and conversion ratio unknown.

### 5. Approve products and stage deployments

After product review, the token IDs have verified provider aliases. Stage deployments only after the platform/network aliases are also approved:

\`\`\`bash
python -m app.providers.coingecko_pilot stage \\
  --snapshot-dir data/provider_snapshots/coingecko/2026-10-30 \\
  --phase deployments --submitted-by 'operator@your-company'
\`\`\`

A deployment is keyed by canonical network + normalized native address/mint. Imported deployments remain \`is_verified=false\` and \`representation_type=unknown\`; a provider platform address is not proof of issuer control, backing, bridge equivalence or legal rights.

### 6. Reconcile and review coverage

After reviewing all staged records:

\`\`\`bash
python -m app.providers.coingecko_pilot reconcile \\
  --snapshot-dir data/provider_snapshots/coingecko/2026-10-30
\`\`\`

The command writes \`coverage.json\` and updates the persistent \`provider_ingestion_runs\` record. It reports:
- provider RWA list count and detail success/failure ratio;
- issuer-list vs token-level issuer ID differences;
- token/product count, platform-contract entries and unsupported platform slugs;
- staged batches and per-entity review status;
- unresolved parent mappings, rejected/duplicate rows and remaining review queue;
- whether all four phases are complete.

A run is only marked completed when the full provider list was requested, every detail succeeded, all four phases are complete, all review decisions are resolved, and no unsupported platform or unresolved parent mapping remains. Otherwise it stays partial/awaiting review. Completion means reconciliation against CoinGecko's tracked dataset—not proof of total market coverage.

The importer only stages records. It never creates or verifies canonical entities automatically. All canonical records and provider aliases continue through human approval with evidence. A CoinGecko-reported issuer name must not be presented as a verified legal entity without independent evidence.
