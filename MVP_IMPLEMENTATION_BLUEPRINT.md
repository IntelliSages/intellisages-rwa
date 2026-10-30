# RWAs Intelligence — MVP Implementation Blueprint

**Version:** 1.0  
**Source:** Product-owner supplied “RWAs Intelligence — MVP Implementation Blueprint” (17 October 2026).  
**Status:** Governing MVP execution baseline. Product-owner approval is required to change scope or acceptance gates.

> This document translates the approved MVP into an implementation sequence. It is not evidence that integrations, calculations, application features or QA have passed. Keep product scope, application readiness and data readiness as separate statuses.

## 1. Launch objective and governing decisions

Launch a working, evidence-backed intelligence product—not a visual replica of the HTML prototype. Users must be able to discover tokenized assets, understand the products and venues behind them, compare relevant market observations, and identify meaningful gaps in coverage.

The following decisions govern implementation:

1. Keep all 16 approved navigation pages. A page may display an explicit unavailable state for an individual metric; it must not silently disappear because a source is incomplete.
2. Build the production application against approved specifications. Treat the HTML review artifact as a reference, not proof of production readiness or a required source-code foundation.
3. Make canonical identity foundational: underlying asset, issuer product, network deployment, venue and contract are distinct entities.
4. Never use mock values as production fallbacks. Every production value needs a defensible source, timestamp, unit and coverage status.
5. Launch validated subsets honestly. A verified sample may be displayed with its exact scope and date; it must not be represented as a complete market-wide total.
6. Do not expand into speculative intelligence before the data foundation is sound. Deep Trader Intelligence accounting and advanced Event Feed scoring/detection remain later engineering work.
7. No trading execution, order placement, custody or guaranteed profitability is part of the MVP.

**Launch principle:** validate the complete 16-page experience while making live-data claims only where source, identity, formula, coverage and permissions have been verified.

## 2. MVP user outcomes

At launch, users should be able to:

- Discover assets and products through Home, Crypto Screener and Tokenized RWA Screener.
- Understand an instrument's underlying, issuer product, verified deployment and actual trading venue.
- Inspect supported price, market activity, funding, open interest and liquidity observations.
- Navigate from an observation to issuer-specific, deployment-specific, builder-specific perpetual or DeFi market context.
- Compare only compatible observations (identity, unit, timestamp, window and market scope).
- Filter, sort, expand, collapse and export supported tables without changing their meaning.
- Understand unavailable, partial-coverage, stale-data and access-blocked states.
- Use the product on desktop and mobile, subject to acceptance tests.

### Product validation goals

Measure whether users can find products, distinguish products from underlyings and venues, interpret metric disclosures, understand partial/unavailable states, and identify pages/metrics useful for repeat research. Instrument search, asset-page visits, screener filters, expansions, CSV exports, repeat sessions, unavailable-state encounters and failed navigation. These measures do not replace data-quality acceptance.

## 3. MVP scope — all 16 pages

| # | Page | MVP responsibility | Launch qualification |
|---|---|---|---|
| 1 | Home / Global Market Overview | High-level crypto and tokenized-asset market view | Verified snapshot metrics only. No definitive exclusion-adjusted crypto total or combined tokenized value until inclusion, overlap and aggregation reconcile. |
| 2 | Crypto Screener | Discover eligible ordinary crypto assets | Documented paginated universe, validated fields, filters and sorting. Crypto-only market cap and longer history depend on universe/history readiness. |
| 3 | Tokenized RWA Screener | Discover underlyings, issuer products, classes, networks and venues | Identity-resolved products only. Each product once, not once per deployment. Each metric independently gated. |
| 4 | Correlation | Compare approved market-value series and explain relationships | Restricted until histories align and membership is stable. Market-wide correlation remains unavailable until prerequisites pass. |
| 5 | HIP-3 Markets | Discover builder-specific perpetual contracts | Exact builder and contract identity. Resolve known `km:NVDA` mismatch; exclude unrelated `xyz`/`mkts` contracts from that context. |
| 6 | Ondo | Inspect Ondo-issued products and market context | Verified identities and authorized tested data. Official API payload/access not validated; do not imply live direct coverage until confirmed. |
| 7 | bStocks | Explore approved bStocks products and observations | Documented Binance/bStocks path is blocked. Keep page; show only independently validated/permitted information and honest blocked fields. |
| 8 | xStocks | Inspect xStocks products, venues and observations | First 100 products retained in prior evidence; subsequent access failed. No complete-catalogue claim. Verify identity and redistribution rights. |
| 9 | Backpack | Inspect Backpack spot/perpetual context | Exact NVDA perp mark validated; broader inputs/coverage remain partial. A mark is not a complete catalogue or executable order book. |
| 10 | Robinhood Tokenized Assets | Map tokenized products to underlyings and market data | Reconcile 194-issuer vs 192-matched discrepancy and missing/unrelated mappings. Do not call `dailyTradingVolume` token turnover without evidence. Correct breadcrumb/title. |
| 11 | PreStocks | Explore products, mint identities, supply and issuer valuation estimates | Eight current products/mint accounts and snapshot inputs validated. Snapshots are dated; complete historical multiplier, bridge or mint coverage is unproven. |
| 12 | Paimon | Display approved asset and market information | Core snapshot validated; full pagination and legal/legacy workflows not. Disclose scope; do not claim completeness. |
| 13 | Funding Rates | Compare available perpetual funding observations | Current rates only where instrument, unit, interval, timestamp and source are verified. History/net cost needs additional validation. |
| 14 | DeFi | Show lending/pool markets and asset/collateral context | Validated Morpho/Kamino subsets with coverage disclosures. Jupiter execution estimates remain blocked. |
| 15 | Trader Intelligence | PnL, win rate, activity, volume and exposure concepts | Keep page/purpose. Enable only metrics with agreed accounting, validated input scope and reproducible calculations. Deeper accounting is later jointly specified. |
| 16 | Intelligence Event Feed | Market, onchain, trading and macro events/indicators | Show sourced validated events/indicators only. Scoring, detection, ranking and alerts require an agreed contract. |

“Conditional” means a verified subset and truthful unavailable states may launch. “Restricted” means the page remains present but advanced behaviour or broad coverage waits for evidence.

### Explicit non-promises

- Complete global tokenized-RWA universe unless pagination and eligible coverage are verified.
- Defensible crypto-only aggregate market cap until provider inclusion is reconciled.
- Complete cross-market correlation without comparable aggregate histories and stable membership.
- Comprehensive issuer/venue coverage; launch validated subsets.
- Complete Trader Intelligence accounting.
- Advanced Event Feed scoring, detection, ranking and alerts.
- Execution or guaranteed profitability.
- Fabricated history, filled missing bars or synthetic live values.

## 4. Shared behaviours required across the 16 pages

| Shared capability | Required behaviour |
|---|---|
| Identity/navigation | Resolve underlying → issuer product → deployment → venue/contract. Ticker-only matching is insufficient. Unknown IDs return not found, never a default asset. |
| Provenance/status | Show source, observation time, freshness, units, coverage and the correct unavailable/partial/stale/blocked state. |
| Cards/tables | One metric definition per field; numeric sorting; nulls last; clear units and consistent formatting. |
| Network/builder context | All Networks shows each product once with verified networks. Selected network shows only verified deployments. HIP-3 filters exact builder context. |
| Market lists | Filter eligible records before ranking; show at most five eligible perpetual entries initially where specified; working View all/Collapse. |
| Charts/history | Plot only actual compatible observations. Show gaps; never fill missing/incomplete bars. |
| CSV | Export active scope/filter, units, timestamps and relevant identifiers; do not include hidden/unrelated rows. |
| Search/filter/sort | Preserve correct context across asset changes, navigation, back/reopen, filters and exports. |
| Loading/failure | Distinguish empty, no eligible data, provider error, blocked access and interrupted pagination. Temporary error is not zero. |
| Responsive UI | Tables, sticky headers, charts, controls and disclosures usable on desktop and mobile. |

## 5. Data-source strategy and onboarding gates

Choose a small number of proven integrations with good identity and coverage controls—not the maximum number of APIs.

### Tier A — candidates for initial live data

- CoinGecko
- GeckoTerminal
- Selected official venue endpoints
- Validated Solana RPC reads

Use only individually validated routes, fields, products and histories with confirmed production access and usage rights. CoinGecko snapshots and specific GeckoTerminal pools/token subsets do not prove complete universe/deployment coverage. Solana RPC evidence for eight PreStocks mint accounts does not prove full ecosystem history.

### Tier B — validated subsets only

- Hyperliquid
- Kraken
- Lighter
- Backpack
- Robinhood
- PreStocks
- Paimon
- Morpho
- Kamino

Use exact tested observations and narrow claims. Existing evidence includes a Hyperliquid hourly-history pilot, selected Kraken history, direct USD OI for a specific Lighter RH instrument, an exact Backpack mark, Robinhood mapping subsets, PreStocks snapshots, Paimon core snapshot, a Morpho lending/collateral subset and selected Kamino reserves. Reconfirm permissions, freshness and coverage before launch.

### Tier C — blocked or unsuitable for full-coverage claims

- Official Ondo API
- Binance/bStocks access path
- Full xStocks catalogue
- Jupiter execution estimates
- Macro integrations pending validation
- Unverified Ondo/Enclave perpetual endpoints

Do not build a production dependency on an endpoint whose access, payload or permitted use is unverified. Keep the feature present with truthful status or use another independently validated source with genuinely matching semantics.

### Provider onboarding checklist

Before production approval, record and test:

1. Provider, exact route, HTTP method, parameters/body, authentication and native instrument/domain/network ID.
2. Sanitized request/response fixture.
3. Native field, normalized field, unit, scale/decimal rules and formula.
4. Observation timestamp vs retrieval timestamp.
5. Pagination completeness, rate limits, error behaviour and history coverage.
6. Entitlement, redistribution, caching, retention and applicable terms.
7. Repeatable tests for identity, missing values, duplicates, unit conversion and interrupted requests.

A docs page or successful sample response is not proof of complete catalogue, unlimited history, production reliability or redistribution permission.

### Initial refresh proposal

These are scheduling proposals, not guaranteed provider capabilities:

| Data family | Proposed cadence | Qualification |
|---|---|---|
| Crypto global aggregate | 10 min | No definitive crypto-only total until inclusion reconciles. |
| Leading crypto quotes | 60 sec | Verified universe and authorized quota only. |
| Long-tail crypto quotes | Hourly | Show freshness; no minute-level coverage claim. |
| Tokenized RWA value materialization | 5 min | Only after values and overlap rules validate. |
| Eligible RWA price/volume inputs | 60 sec | Permissions, cost and quota must support it. |
| Product/issuer snapshots | Hourly; eligibility daily | Snapshot is not historical coverage. |
| Current funding | 30–60 sec | Supported authorized sources and verified instruments only. |
| Contract metadata/identity | Daily plus controlled updates | Detect new, delisted, remapped and renamed instruments. |
| Funding history | Initial backfill, then hourly completed-history updates | No fabricated intervals or unfinished bars as final. |
| Correlation inputs | 5-min collection; aligned hourly calculations | Only compatible series and membership. |

A slower verified refresh is preferable to an advertised high-frequency refresh that fails silently or exceeds permitted use.

## 6. Proposed technical architecture

The supplied blueprint proposes (not mandates) this lean architecture, subject to the actual repository audit:

- Frontend: Next.js + React + TypeScript.
- Backend API: Python FastAPI.
- Primary database: PostgreSQL.
- Object storage: versioned raw responses, fixtures, exports and selected archives.
- Separate ingestion workers/scheduler: adapters, quotas, retries, normalization, deduplication, backfills and monitoring.
- Authorized external data providers.

Do not choose or replace the existing stack until the repository is audited. The frontend must not call secret-bearing provider endpoints directly.

### Core data entities

- `underlying_asset`
- `issuer_product`
- `deployment`
- `perp_contract`
- `pool_market` / `loan_market`
- `source_observation`
- `history_observation`
- `metric_output`
- `coverage_record`
- `refresh_job_state`
- `validation_record`

### Ingestion and calculation lifecycle

1. Schedule refresh/backfill within provider quota.
2. Fetch via provider adapter with timeout, rate limit and bounded retries.
3. Preserve sanitized raw response and request/retrieval metadata.
4. Normalize native IDs, decimal scales, units and timestamps.
5. Resolve canonical identity.
6. Validate units, identity, duplicates and interval completeness.
7. Calculate only approved metrics using versioned formulas.
8. Publish with availability, freshness, scope and coverage.
9. Monitor failures, lag, missing fields, row-count anomalies and catalogue membership changes.

For MVP, PostgreSQL time-indexed observations are sufficient as the starting proposal. Add time-series extensions or specialized infrastructure only when measured workloads justify them. Do not introduce Kafka, Redpanda, Iceberg, ClickHouse or graph databases without a measured need.

### Environments and deployment proposal

- Frontend: Vercel or equivalent managed Next.js hosting.
- API: managed container hosting for FastAPI.
- Database: managed PostgreSQL with automated backups.
- Ingestion: separate persistent worker/container.
- Raw storage: S3-compatible object storage or equivalent.
- Monitoring: structured logs, error monitoring and ingestion alerts.
- Environments: development, staging and production with separate credentials/data.
- CI/CD: lint, type checks, unit/integration tests, migrations and controlled releases.

Essential ingestion must not run only inside a frontend deployment or short-lived web request.

## 7. Metric readiness and API contract

Readiness is per metric and per series, not inherited from a page or provider.

- **READY:** exact identity, source, units, formula, coverage, freshness and permissions passed reproducible tests.
- **CONDITIONAL:** subset/additional checks required; publish only within verified scope with visible qualifications.
- **UNAVAILABLE:** do not display a live number while a dependency, formula, history, permission or coverage proof is missing.

Initial metric gates:

| Metric | Initial status | Launch rule |
|---|---|---|
| Exact current price/mark | Conditional → Ready per instrument | Exact product/contract ID, quote, unit, timestamp and permitted access. |
| 24h price change | Conditional | Source definition and comparison window verified. |
| Market cap / FDV | Conditional | Supply, price, units, methodology and scope verified; issuer estimates labelled separately. |
| Crypto-only aggregate cap | Unavailable | Reconcile tokenized-product inclusion in provider global total. |
| RWA catalogue | Conditional | Pagination and identity reconciliation for declared universe. |
| Product value/supply | Conditional | Economic supply, decimals, wrappers, bridges and deduplication verified. |
| 24h trading volume | Conditional | Unique execution coverage and overlap treatment established. |
| Liquidity | Conditional | Concept, venue scope, quote and timestamp defined; reserves are not automatically executable liquidity. |
| Network/deployment | Conditional | Product-specific verified deployment/native IDs. |
| Perpetual availability | Conditional | Exact contract, venue, builder/domain, status and underlying mapping. |
| Open interest | Conditional | Native unit, multiplier, quote conversion and exact contract. |
| Funding rate | Conditional | Fraction/percentage, interval, timestamp and annualization assumptions verified. |
| Funding history | Conditional/unavailable per series | Completed aligned history and visible gaps. |
| Funding arbitrage/net cost | Unavailable as complete opportunity claim | Compatible instruments, direction, intervals, fees, impact and required legs. |
| Selected-asset correlation | Conditional | Compatible aligned returns and declared window. |
| Market-wide correlation | Unavailable | Aligned aggregate histories and stable exclusive membership. |
| DeFi lending/collateral | Conditional | Exact market/reserve/pair/token identities and units; disclose protocol coverage. |
| PreStocks supply/valuation | Conditional | Dated snapshots and exact mint; no unproven historical multipliers. |
| Trader metrics | Conditional/unavailable per metric | Agreed accounting, complete input scope and reproducible calculations. |
| Event observations | Conditional | Validated source, event time and evidence. |
| Event scores/rankings/detections/alerts | Unavailable | Agreed logic and evaluation criteria required. |
| Historical returns/comparisons | Conditional/unavailable per series | Compatible observations and effective membership; no fabricated history. |

Every metric response must carry a nullable value and explain its status. Proposed shape:

```json
{
  "metric": "funding_rate",
  "value": null,
  "unit": "fraction_per_interval",
  "status": "unavailable",
  "reason": "history_not_validated",
  "source": "provider_name",
  "observed_at": null,
  "retrieved_at": null,
  "coverage": {
    "scope": "specific_instrument",
    "complete": false
  },
  "formula_version": "1"
}
```

This is illustrative, not an implemented API. Null with a reason is preferable to fake zero.

## 8. Implementation work packages and sequence

The dependency chain is:

**Scope/acceptance baseline → canonical identity registry → provider adapters/raw evidence → normalization/coverage/history → metric calculation/availability API → shared UI → all 16 pages → regression/acceptance → controlled MVP launch → post-launch coverage expansion → deeper intelligence engines.**

### WP0 — Scope, fixtures and acceptance baseline (3–5 working days)

- Freeze 16-page navigation and approved behaviour.
- Turn ten known QA failures into explicit defect tickets.
- Establish per-page/per-metric readiness and source evidence inventory.
- Preserve HTML reference evidence and inherited test requirements.

Deliverables: backlog, test baseline, identity fixtures, metric readiness register and acceptance plan.  
Exit: no ambiguity about approved scope.

### WP1 — Canonical identity/classification registry (1–2 weeks)

- Model underlyings, issuer products, deployments, perp contracts, pools and loan markets.
- Implement inclusion/exclusion and double-counting rules.
- Resolve native IDs, network/domain context, relationships and supported mappings.
- Test symbol collisions, bridges, wrappers, duplicate venues and unsupported IDs.

Deliverables: schema, migrations, registry import, versioned fixtures and identity tests.  
Exit: declared eligible catalogue reconciles or its missing scope is explicit; no completeness claim.

### WP2 — Provider adapters and ingestion (1–2 weeks for initial integrations)

- Start with highest-value permitted validated routes.
- Save sanitized raw fixtures and request metadata.
- Implement pagination, bounded retries, quota controls and partial/blocked states.
- Separate native data from normalized observations.

Deliverables: adapter interfaces, initial integrations, worker/scheduler, logs and replayable fixtures.  
Exit: each launch metric has reproducible inputs and documented coverage.

### WP3 — History, normalization and metric engine (1–2 weeks; partly parallel)

- Normalize timestamps, decimals, units, funding intervals and market IDs.
- Build historical backfill and completed-interval ingestion.
- Implement metric dictionary as versioned calculations.
- Attach coverage, freshness, formula version and availability metadata.

Deliverables: normalized observations, history tables, metric services, gap detection and calculation tests.  
Exit: enabled metrics reproduce from known inputs and pass unit/formula tests.

### WP4 — Shared UI and all 16 pages (2–3 weeks)

- Implement shared identity navigation, status displays, tables, charts, filters and CSV export.
- Build page layouts against approved specifications.
- Connect each page to readiness-aware backend APIs.
- Keep unavailable metrics visible with explanations.

Deliverables: working responsive app, page integrations and user analytics.  
Exit: all 16 pages reachable/usable; no mock or unrelated production fallback.

### WP5 — Regression, operations and controlled launch (1–2 weeks)

- Resolve inherited reference defects.
- Execute inherited 739-case matrix against actual implementation in batches.
- Test provider failure, stale data, interrupted pagination, mobile and exports.
- Verify backups, access control, logs, alerts and provider-use permissions.

Deliverables: executed test evidence, retests, deployment runbook, backup/restore evidence and launch decision.  
Exit: critical behaviours pass, no known critical failure remains, and every live claim is supported.

**Planning envelope:** approximately 8–12 weeks for a small experienced team, subject to provider access, reconciliation and regression findings. This is an estimate, not a committed delivery date.

### Safe parallel work

UI may start against typed fixtures/API contracts while adapters are built; identity fixtures and tests may accompany schema work; entitlement checks can run in parallel with application development; page layouts may proceed before all metrics are ready if mock data cannot leak into production.

### Do not parallelize prematurely

Do not finalize aggregates before identity/inclusion/overlap rules; enable market-wide correlation before compatible history/membership; build deep Trader Intelligence accounting before semantics; advertise complete catalogues from sample endpoints; or treat visual completeness as acceptance.

## 9. Inherited QA defects — retain IDs

| ID | Required correction | Acceptance evidence |
|---|---|---|
| QA-01 | HIP-3 `km:NVDA` shows only eligible `km` builder contracts for NVIDIA; zero unrelated `xyz`/`mkts` contracts. | Automated tests for km:NVDA, other builders and broad discovery. |
| QA-02 | Remove reappearing holders fields from applicable active tables where removed/deferred. | DOM/table assertion and visual regression. |
| QA-03 | Remove reappearing Basis column where deferred. | Table schema and CSV assertions. |
| QA-04 | Remove reappearing Best Venue Gap column where deferred. | Table schema and CSV assertions. |
| QA-05 | Remove reappearing Off-Hours Move column where deferred. | Table schema and CSV assertions. |
| QA-06 | Correct Robinhood Tokenized Assets breadcrumb/title. | Navigation test and screenshot/readback. |
| QA-07 | Fix DeFi sticky-header alignment. | Desktop and mobile scrolling regression. |
| QA-08 | Unknown asset/market IDs resolve to not found, never BTC/NVDA/default row. | API and UI negative tests. |
| QA-09 | Crypto dropdowns filter intended reference rows in reference mode; production uses real backend data. | Filter assertions and production API integration test. |
| QA-10 | No deferred Carry/arbitrage functionality or standalone Pre-IPO page. | Navigation and route assertions. |

Do not replace original IDs or call a defect retested without evidence.

## 10. Acceptance matrix and release gate

Execute the inherited 739-case matrix against the actual implementation. It is a historical requirement set, not evidence that tests pass.

Minimum areas: navigation/context; identity resolution; networks/aggregation; exact markets/contracts; metric units/formulas; historical intervals; funding direction/costs; DeFi identity/coverage; CSV scope; responsive UI; provider failure states; security/operations; and data rights.

Test status vocabulary:
- **PASS:** executed against actual implementation and passed.
- **FAIL:** executed and disagreed with expected behaviour.
- **BLOCKED:** demonstrated external dependency prevents execution/acceptance.
- **NOT TESTED:** no execution evidence.

MVP controlled launch requires:
- All 16 pages represented and usable.
- Critical navigation/shared behaviours pass.
- No known critical QA failure open.
- Each displayed metric has validated semantics, units, source and appropriate coverage/freshness.
- Unavailable states work; no production mock fallback.
- Provider access and usage/redistribution rights confirmed.
- Inherited regression suite executed; remaining non-critical failures documented and product-owner accepted.
- Monitoring, backup/restore, incident handling and ingestion ownership established.
- Product-owner release approval.

A blocked individual metric may remain unavailable. If a dependency prevents a core page functioning honestly or creates a critical false claim, delay release.

## 11. Post-launch phases

1. **Coverage/reliability:** complete pagination/reconciliation, resolve quotas/rights, expand product/deployment mappings, improve backfills, resolve crypto-only aggregate, RWA overlap and volume deduplication.
2. **Analytical comparisons:** aligned historical performance/correlation, validated funding costs, broader DeFi collateral/liquidity and reliable historical product supply/valuation.
3. **Deeper intelligence:** jointly specified Trader accounting; Event taxonomy, macro/onchain/trading feeds; scoring/detection/ranking/alerts only with evaluation plan.
4. **Scale operations:** optimize from measured workload, improve retries/failover where permitted, monitoring/performance/mobile QA, add specialized storage/streaming only when justified, review unit economics.

Review usage weekly during controlled launch: page engagement, zero-result searches, unavailable metrics, causes of unavailable states, repeat visits/exports and highest-value coverage improvements. Prioritize reliability and coverage before new features.

## 12. Budget and operating model

The supplied blueprint's planning allowances (USD/month) are indicative only, not vendor quotes or approved spend:

| Cost item | Planning allowance | Qualification |
|---|---:|---|
| Frontend hosting | $0–20 | Free tier only if limits and commercial terms fit. |
| API + ingestion runtime | $10–40 | Separate API/worker workloads. |
| Managed PostgreSQL | $0–30 | Verify persistence, backups, connections and recovery. |
| Object storage/backups | $0–10 | Depends on retention/export volume. |
| Monitoring/logging | $0–15 | Bounded retention and ingestion alerts. |
| Domain/basic overhead | $0–5 equivalent | Excludes one-off registration. |
| Illustrative subtotal | $10–120/month | Excludes paid market-data entitlements and labour. |

Indicative scenarios: controlled validation pilot $10–50/month; minimum sustainable production $50–150/month; expanded coverage budget only after provider quotes and measurement. These are planning envelopes, not price claims. Data licensing/entitlement costs are separate and cannot be credibly fixed until routes and display rights are confirmed.

Assign ownership for product decisions, backend/data, frontend, QA/release, operations and provider entitlements. The operational dashboard should show last successful refresh, observation age, expected refresh completion, pagination/backfill progress, provider errors/rate limits/auth failures, row-count and identity changes, DB/backup/hosting/data spend and critical defects.

## 13. Execution checklist

- [ ] Freeze 16-page scope and convert inherited defects to acceptance tests.
- [ ] Implement canonical asset, issuer-product, deployment, contract and DeFi identities.
- [ ] Confirm provider permissions and implement first validated adapters.
- [ ] Build normalization, pagination, history, coverage and metric availability.
- [ ] Implement shared UI and connect all 16 pages to production APIs.
- [ ] Resolve critical reference defects and execute inherited regression matrix.
- [ ] Verify live-data claims, operations, backups, access controls and owner approval.
- [ ] Prioritize post-launch coverage/intelligence from user evidence.

## 14. Governance and change control

This blueprint is the governing MVP implementation baseline. Any proposed change must state the user problem, affected pages/entities/metrics, evidence, formula, coverage impact, double-counting risk, migration/backfill impact, acceptance tests and product-owner approval. Preserve rejected/deferred decisions.

Keep three statuses separate at all times:
1. **Documentation completeness**
2. **Application readiness**
3. **Data readiness**

A finished-looking interface is not a reliable intelligence product unless its live claims are independently supported.
