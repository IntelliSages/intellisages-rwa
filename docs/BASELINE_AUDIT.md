# Baseline Audit — RWAs Intelligence

**Audit date:** 2026-10-30  
**Scope:** product brief, supplied source documents, full embedded review-data package in supplied HTML and accessible GitHub repository metadata.  
**Important:** initial product/prototype audit, not a source-code audit.

## 1. Repository findings

- Repository: IntelliSages/intellisages-rwa; default branch: main.
- Private repository is accessible through the connected GitHub integration.
- README.md existed as a minimal starter and has been expanded.
- Before this documentation work, README.md was the only repository source file confirmed. Probes for package.json, pyproject.toml, requirements.txt, index.html, src/main.tsx, app/page.tsx and .gitignore returned 404.
- No application framework, backend, database, deployment, CI or test suite has been identified.
- The supplied HTML is a review/mock artifact, not code found in the repository.

## 2. Supplied source inventory

| Source | Contents | Use |
|---|---|---|
| Product vision in conversation | Product purpose, users, journeys, MVP page inventory and principles | Product north star |
| Home Screener Specification | Home purpose, metrics, interactions, CoinGecko sample evidence and proposed implementation | Home acceptance source |
| Shared Metric Dictionary | 218 rendered table/card fields across fifteen pages plus Correlation/headline families | Metric reference; preserve per-metric readiness |
| Asset Identity, Classification and Double-Counting Rules | Four approved Option B decisions, entity relationships, formulas and fixtures | Binding data-model/aggregation rules |
| Provider Endpoint Registry | Provider endpoints, retained sample findings, access limits, cadence targets and blockers | Adapter planning/source validation |
| Data Integration and Backend Contracts | Proposed record semantics, normalization, read-service/filter contracts, history/error contracts and fixtures | Proposed internal contract, not deployed API |
| Final MVP Review HTML | Review shell plus embedded review package, current/proposed views, 20 page objects, 1,061 review records and original baseline HTML | Visual/interaction/decision reference; mock values are not live |

## 3. What the HTML contains

The HTML title is “RWAs Intelligence — Final MVP Review Candidate”. It contains a hidden review infrastructure wrapper and a separate product view. Its embedded package includes 20 page objects, 1,061 metric/UI review records, baseline hash and original HTML encoded in the package, page/metric family metadata, evidence archive, asset corrections and proposed review decisions.

The review shell supports Current baseline and Proposed MVP modes and per-record KEEP / IMPROVE / REMOVE / DEFER / ADD recommendations.

Recommendation counts: IMPROVE 781; KEEP 156; REMOVE 76; DEFER 44; ADD 4. These are review-tool recommendations, not automatically approved scope. Many records are UI elements, historical duplicate fields, evidence rows or individual metrics; 1,061 is not the number of product features.

The 20 page objects:
- overview (Home), crypto, rwa, correlation, hip3;
- ondo, bstocks, xstocks, backpack, robinhood;
- prestocks, paimon, funding, defi;
- arbitrage, private;
- hip3-detail, asset-detail;
- traders, events.

The product-owner MVP list contains sixteen main surfaces. The extra Cross-Token Arbitrage and standalone Pre-IPO Markets pages are legacy/removed scope, not approved standalone MVP pages. hip3-detail and asset-detail are detail templates/routes, not extra top-level navigation items.

The HTML also contains tabs that conflict with settled scope: Spot–Perp Carry on Ondo/bStocks/xStocks/Backpack/Robinhood; Paimon Launchpad Deals and Events/Settlements; plus older private/Pre-IPO and arbitrage pages. A tab/page is not approved because it remains in baseline HTML.

## 4. Important mock-vs-approved discrepancies

- Home HTML shows illustrative Crypto ↔ RWA correlation +0.61 with a 24H window. Approved Home specification says market-wide history unavailable and uses returns-based 30D. Numeric mock must not ship as live.
- Home mock headline values (Crypto $2.73T, Tokenized RWA $48.2B, volumes/tracked counts and +2.1% performance) are illustrative, not validated current totals.
- Crypto mock shows BTC dominance and RWA correlation median; these are headline families, not proof of full-universe calculation.
- HIP-3 mock includes qualified trader flow, active trader counts and builder/market examples; retained dictionary says qualified trader flow/qualification is not validated and exact mapping is partial.
- Issuer mock pages show issuance, holder, mint/redeem, off-hours, carry, basis, valuation and deal fields that are removed, deferred, blocked or unvalidated in source decisions.
- PreStocks mock has implied valuations, private ranges, dislocation and catalyst fields; do not turn these into live market valuation or validated index output.
- Paimon mock includes deal capacity, subscription/allocation, settlement and event fields; approved core view has no headline cards and retains unavailable/deferred states.
- DeFi mock includes fee APR/range/concentration concepts; retained dictionary does not approve personal LP return estimates from current fee × historical volume.
- Trader mock shows PnL/trade/win-rate/profit-factor/drawdown/exposure; accounting and several numeric methods remain reserved.
- Event mock is illustrative; no validated universal event API or automatic detector exists.

## 5. Prototype behaviour and known corrections

The review shell help text states that product figures/chart shapes are illustrative; review decisions are local until shared; unknown asset/market IDs show not found rather than falling back to BTC/NVDA; previously unbound crypto dropdowns filter original mock rows; no new market data is fetched; and legacy logo approximation is hidden in Proposed until the exact master logo is supplied. Known removed/deferred columns reappearing in original HTML are defects, not new scope.

## 6. Known risks

**Identity/aggregation:** underlying, issuer, issuer product, deployment, venue, pool and perp contract are distinct. Different issuer products cannot be merged because they reference one company. Multi-network representations can duplicate economic supply. Router/provider/pool reports can overlap volume. Crypto and RWA universes require internal verified classification. Provider global totals cannot be adjusted without proof of constituent inclusion.

**Source/coverage:** CoinGecko global/coin/RWA sample calls succeeded in retained tests; full adjusted Crypto and whole RWA coverage remain unverified. Several issuer endpoints are blocked, partially paginated, authenticated or undocumented. Access, tier, quota, cache, history, licensing and redistribution are separate checks. A first page is not a complete catalogue.

**History/calculations:** market-wide aggregate histories are not established. Some individual histories exist only for subsets. Current values do not imply historical readiness. Correlation needs aligned comparable returns and sufficient overlap. Funding needs native unit, interval and sign normalization.

**Reserved systems:** Trader Intelligence accounting and Event Feed detection/ranking/alerts are not specified. Paimon Deals and Events/Settlements remain unavailable/deferred. No execution, custody or wallet signing service is in MVP.

## 7. Audit limitations

This baseline does not assert every linked Google Doc was freshly opened, every provider endpoint was re-tested on 2026-10-30, credentials or paid entitlements exist, prototype metrics are live, a deployment is functioning, or code exists beyond files confirmed in the repository.

## 8. Next audit checklist

- [x] Confirm default branch and README baseline.
- [x] Probe common frontend/backend manifests and source entrypoints; none found.
- [x] Parse embedded review package and enumerate page objects/records.
- [ ] Obtain separate source repo/branch or push frontend source into this repo.
- [ ] Inspect source routes/components/state/API calls once code is present.
- [ ] Inspect DB schema/migrations, tests, CI, deployment and secrets handling.
- [ ] Capture running UI screenshots if a running app exists.
