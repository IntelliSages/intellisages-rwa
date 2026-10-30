# Baseline Audit — RWAs Intelligence

**Audit date:** 2026-10-30  
**Scope:** product brief, supplied files and accessible GitHub repository metadata.  
**Important:** this is an initial documentation audit, not a source-code audit.

## 1. Repository findings

- Repository: IntelliSages/intellisages-rwa
- Default branch: main
- Repository is private and accessible through the connected GitHub integration.
- README.md existed as a minimal starter and has been expanded.
- A complete tree/code/deployment/test inspection has not yet been completed.
- No frontend framework, backend framework, database, hosting platform, CI status or running service is asserted here.

**Required next step:** inspect the repository tree and each existing source/configuration file before implementation planning is treated as stack-specific.

## 2. Supplied source inventory

| Source | Contents | How to use it |
|---|---|---|
| Product vision in conversation | Vision, users, journeys, MVP scope and implementation principles | Product north star |
| Home Screener Specification | Home purpose, headline metrics, columns, interactions, CoinGecko sample evidence and proposed backend steps | Home acceptance source |
| Shared Metric Dictionary | Shared metric definitions; 218 rendered table/card fields across fifteen pages plus Correlation/headline families | Metric reference; retain each page's validation boundary |
| Asset Identity, Classification and Double-Counting Rules | Four approved Option B decisions, entity relationships, formulas and fixtures | Binding data-model/aggregation rules |
| Provider Endpoint Registry | Provider endpoints, retained sample findings, access limits, cadence targets and blockers | Adapter planning and source-validation checklist |
| Data Integration and Backend Contracts | Shared record semantics, ingestion steps, read-service/filter behaviour, history/error contracts and acceptance fixtures | Proposed internal contract, not deployed API |
| Final MVP Review HTML | Interactive current/proposed review shell, embedded product reference and original/current-baseline data | Visual/interaction reference; sample values are not live |

## 3. HTML prototype interpretation

The supplied file is titled “RWAs Intelligence — Final MVP Review Candidate”. Its review shell distinguishes a Current baseline from a Proposed MVP view and provides metric evidence/review/export controls. The review instructions explicitly say product figures and chart shapes are illustrative, and that decisions exported from the review are local review choices until shared.

The HTML also documents prior prototype corrections:
- Unknown asset/market IDs should display not found rather than falling back to BTC/NVDA.
- Previously unbound crypto dropdowns were wired to filter original mock rows.
- No new market data is fetched by the review shell.
- Legacy visual logo approximation is retained in Current for comparison and hidden in Proposed until the exact master logo is supplied.
- Some fields/columns reappearing in the HTML are known defects, not new scope.

The review shell must not be mistaken for a production frontend or backend.

## 4. Known product/data risks from supplied materials

### Identity and aggregation
- Underlying, issuer, issuer product, deployment, venue, pool and perp contract are distinct.
- Different issuer products cannot be merged because they reference the same company.
- Multi-network representations can duplicate economic supply.
- Router/provider/pool reports can overlap execution volume.
- Crypto and tokenized RWA universes require internal verified classification.
- Provider global totals cannot be adjusted without proof of constituent inclusion.

### Source and coverage
- CoinGecko global/coin/RWA sample calls succeeded in retained tests; full adjusted Crypto and whole RWA coverage remain unverified.
- Several issuer endpoints are blocked, partially paginated, authenticated or undocumented.
- Provider access, purchased tier, quota, cache, historical retention, licensing and redistribution remain separate checks.
- A first page or a small successful sample does not establish complete catalogue coverage.

### History and calculations
- Market-wide aggregate histories are not established.
- Some individual-asset histories exist only for subsets.
- Current values do not imply historical readiness.
- Correlation needs aligned, comparable returns and sufficient overlap.
- Funding rates need native unit, interval and sign normalization.

### Deferred systems
- Trader Intelligence accounting is not fully specified.
- Event Feed detection/ranking/alert engine is not specified.
- Paimon Deals and Events/Settlements remain unavailable/deferred.
- No execution, custody or wallet signing service is in MVP.

## 5. Audit limitations

This baseline does not assert:
- that every supplied linked specification or Google Doc was freshly opened;
- that every provider endpoint was re-tested on 2026-10-30;
- that API credentials or paid entitlements exist;
- that any prototype metric is live;
- that repository code is empty or complete;
- that a deployment is functioning.

## 6. Audit checklist

- [ ] List complete repository tree and branch commit.
- [ ] Inspect package manifests, source files and environment templates.
- [ ] Identify routes/screens and compare with supplied HTML.
- [ ] Identify current mock-data sources and live API calls.
- [ ] Inspect DB schema/migrations and seed data.
- [ ] Inspect tests, CI, lint/typecheck and build.
- [ ] Inspect deployment/runtime configuration and secrets handling.
- [ ] Capture screenshots of current running UI, if a running app exists.
- [ ] Reconcile source-level findings with this document and PROGRESS.md.
