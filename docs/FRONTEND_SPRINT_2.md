# Frontend Sprint 2 — Tokenized RWA Screener

**Status:** implementation increment on `feat/tokenized-rwa-screener`; release is gated on push and pull-request CI.

## Delivered frontend

- Dedicated `/tokenized-rwa-screener` page with responsive catalogue table.
- Search across underlying, issuer, product and symbol; issuer and verified-network facets; deterministic sort controls; page navigation.
- One row per issuer product, with expandable canonical identity, classification evidence and product-level deployments.
- Verified deployments are displayed as verified network chips; unverified deployment records are disclosed separately and do not satisfy network filters.
- Shared availability, unavailable-metric and evidence/provenance components.
- Explicit loading, empty, API-not-configured, upstream-unavailable and request-error states.
- Price, tokenized value, volume, liquidity, 24H/7D/30D performance, versions and perpetual availability remain unavailable until validated observation/read services exist.

## Backend catalogue route

`GET /api/v1/catalogue/tokenized-products`

- Returns products with a currently effective `rwa` classification.
- Joins issuer and underlying identity without collapsing distinct products issued against the same underlying.
- Returns classification source/evidence/effective period and all product-specific deployment records with verification state.
- Supports search, issuer filter, verified network filter, sort, direction, limit, offset and optional `as_of`.
- Provides issuer and verified-network facets.
- Marks provider-universe coverage as `unknown`; total counts refer only to matching canonical registry records.
- Returns no market observations and makes no claim of provider completeness.

## Frontend API boundary

The browser calls a same-origin Next.js route at `/api/catalogue/tokenized-products`. The route proxies to the FastAPI service using server-only `RWA_API_BASE_URL`. It does not expose the upstream API URL through `NEXT_PUBLIC_*` variables.

## Automated tests

Backend tests cover:
- distinct issuer products sharing one underlying;
- one row per product across multiple verified deployments;
- effective-dated RWA classification and exclusion of non-RWA/unclassified records;
- verified-only network filtering;
- search, issuer/network facets, sorting, pagination and invalid bounds;
- explicit unknown provider coverage.

Frontend tests cover:
- shared availability/provenance rendering;
- canonical product display and deployment detail expansion;
- verified network filter request behaviour;
- unavailable market metric disclosure;
- explicit API-not-configured state.

## Known limitations

- The catalogue is only as complete as the current identity registry; it is not a full provider universe.
- There is no provider ingestion or normalized market-observation store yet.
- The current registry's write routes remain administrative and unauthenticated; do not expose registry mutation routes on a shared/public deployment.
- Deployment evidence is not a full legal/backing review. A verified deployment flag is a registry verification state only.
