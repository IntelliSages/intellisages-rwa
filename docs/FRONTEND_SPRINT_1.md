# Frontend Sprint 1 — Home and Crypto Screener

**Status:** implementation increment; live-data integration remains blocked on backend read services and validated provider observations.

## Delivered UI scope

- A dedicated Crypto Screener route at `/crypto-screener`, taking precedence over the generic workspace route.
- Search input, category and network filter controls, sort field and direction controls, reset behaviour, semantic table headers, responsive table overflow and disabled export/pagination until a validated dataset exists.
- Explicit empty/unavailable state. The screen does not ship sample assets, fake counts, prices, market caps, volume, percentage changes or fabricated coverage.
- Existing global navigation and all sixteen approved page destinations remain intact.

## API integration boundary

The screener is intentionally not wired to an invented endpoint. The proposed `GET /api/v1/screeners/{screenId}` contract in `docs/API_CONTRACTS.md` is a logical contract, not a deployed route. Before connecting it, backend implementation must provide canonical asset IDs, eligibility/classification, complete pagination metadata, metric availability/provenance and deterministic sorting.

## Acceptance checks

- Search, filter drawer, category/network selection, sort direction and reset controls update local UI state.
- Export and pagination remain disabled while there are no eligible rows.
- The empty state explains that no catalogue records are connected and does not imply a zero-asset universe.
- No mock market data is rendered.
- Existing navigation continues to expose all approved pages.

## Remaining frontend work

This is the first visible product increment, not completion of all sixteen detailed workspaces. Home dashboard visual refinement, shared reusable table/metric/provenance components, tokenized RWA discovery and the remaining page-specific workspaces continue in subsequent increments.
