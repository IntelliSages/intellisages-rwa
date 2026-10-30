# RWAs Intelligence — Engineering Task Register

**Governing baseline:** [MVP_IMPLEMENTATION_BLUEPRINT.md](MVP_IMPLEMENTATION_BLUEPRINT.md).  
**Status:** implementation in progress. Completion requires merged code and linked executed evidence in PROGRESS.md.

Legend: [ ] not started · [~] in progress · [x] completed with evidence · [!] blocked.

## EPIC 0 — MVP freeze, repository and prototype baseline

- [x] Freeze the 16 approved pages and page-level launch qualifications in the MVP blueprint.
- [x] Record repository tree, default branch, framework, dependencies and scripts.
- [~] Inspect frontend routes/components/state/API calls/mock fixtures.
- [~] Inspect backend services, migrations, jobs, secrets and deployment configuration.
- [x] Inspect CI, lint, typecheck, unit/integration/e2e tests and coverage baseline.
- [ ] Inventory every mock page, tab, control, metric, navigation target and modal.
- [x] Separate approved MVP, current baseline, removed features and deferred scope.
- [ ] Convert inherited QA-01–QA-10 into tracked acceptance tests.
- [ ] Establish per-page/per-metric readiness register and provider evidence inventory.
- [ ] Record security, licensing, accessibility and operational risks.

## EPIC 1 — Canonical identity and classification registry

- [x] Define canonical entities/IDs for underlying, issuer, issuer product, network, deployment, venue, perp contract and provider alias.
- [x] Add effective-dated provider aliases and exact symbol/name namespaces.
- [~] Add evidence-bearing perpetual contract migration events with predecessor/successor links and terminal delisting/expiry events.
- [~] Add representation type: independent issuance, bridge/wrapper or unknown.
- [~] Add effective-dated economic-supply groups/memberships with evidence references and explicit verification.
- [~] Add versioned underlying/product classification and provider-global inclusion evidence.
- [x] Add exact builder/domain/market identity for perpetual contracts.
- [ ] Add registry import/reconciliation and unresolved mapping workflow.
- [~] Test NVIDIA/NVDAx/NVDAon distinction, duplicate issuer-native IDs, EVM normalization, non-EVM case preservation and exact alias resolution.
- [~] Verify deployment per product; the API requires an explicit product + network deployment and does not infer issuer-wide support.
- [x] Ensure unknown IDs return not found, never a default asset.

**Current baseline:** PRs #2, #3 and #4 are merged. PR #4 adds effective-dated provider alias history. Perpetual contract migration history is in the current feature branch; spot/pool/loan-market identities, bulk reconciliation and access controls remain open.

## EPIC 2 — Provider adapters, rights and ingestion

- [ ] Prioritize source tiers and validated subsets in MVP_IMPLEMENTATION_BLUEPRINT.md.
- [ ] Confirm exact provider route, method, parameters, auth, native identifiers and entitlement.
- [ ] Confirm commercial use, caching, retention, redistribution, attribution and CSV/export rights.
- [ ] Save sanitized request/response fixtures and retrieval metadata.
- [ ] Define provider adapter interface and secret configuration.
- [ ] Implement raw response persistence with secret redaction.
- [ ] Implement pagination checkpoints and terminal-page validation.
- [ ] Implement bounded retries, rate budgets and idempotency.
- [ ] Implement quarantine for invalid/unmapped records.
- [ ] Implement coverage snapshots, partial/blocked states and job telemetry.
- [ ] Separate source-native records from normalized observations.
- [ ] Validate the proposed refresh cadence against actual quotas and reliability.

## EPIC 3 — Normalization, history and metric readiness

- [ ] Implement normalized observation schema and decimal/unit handling.
- [ ] Preserve observation, retrieval and calculation timestamps separately.
- [ ] Implement completed interval history collection and resumable backfills.
- [ ] Store explicit gaps; never fabricate or silently fill missing bars.
- [ ] Store effective-dated units, multipliers, corporate actions and universe membership.
- [ ] Implement versioned metric calculations and formula fixtures.
- [ ] Implement per-metric READY/CONDITIONAL/UNAVAILABLE status, reason, coverage and freshness.
- [ ] Implement metric availability response contract.
- [ ] Test percentage changes, funding units/intervals, OI units, liquidity semantics and null-vs-zero.
- [ ] Gate charts/comparisons on real compatible series.

## EPIC 4 — Home and broad screeners

- [ ] Implement eligible Crypto universe crawl or explicitly disclose covered universe.
- [ ] Implement tokenized RWA underlying discovery and canonical product catalogue.
- [ ] Implement Crypto/RWA classification and provider-global inclusion checks.
- [ ] Implement Home headline read model with honest partial/unavailable states.
- [ ] Implement ranking after full eligible ingestion and active filters.
- [ ] Implement underlying detail with separate issuer products.
- [ ] Implement product expansion showing verified deployments and actual venues.
- [ ] Ensure All Networks returns each issuer product once.
- [ ] Ensure CSV exports active filters/scope, canonical IDs, units and timestamps.

## EPIC 5 — Issuer, venue and perpetual vertical slices

- [ ] Implement issuer-specific catalogues with coverage reports.
- [ ] Validate xStocks product identity, deployment mapping and redistribution rights.
- [ ] Reconcile Robinhood 194 issuer vs 192 matched discrepancy and volume field semantics.
- [ ] Validate Backpack securities/RFQ/listed-market distinctions.
- [ ] Validate Ondo and bStocks access before enabling live dependencies.
- [ ] Implement PreStocks exact mint/supply snapshots with dated scope.
- [ ] Implement Paimon core snapshot with pagination/legal limitations disclosed.
- [ ] Implement GeckoTerminal exact pool/token observations.
- [ ] Implement Hyperliquid HIP-3 exact builder-specific markets.
- [ ] Implement Lighter RH/Core and Kraken/Backpack perps only for validated IDs.
- [ ] Fix QA-01: km:NVDA must not include unrelated xyz/mkts contracts.
- [ ] Normalize mark/index/oracle/mid/bid/ask/last-price semantics.
- [ ] Normalize open-interest units and contract multipliers.
- [ ] Normalize funding sign, fraction/percent and payment intervals.
- [ ] Implement top-five eligible perp preview with View all/Collapse.

## EPIC 6 — History, correlation and funding

- [ ] Store effective-dated membership, multipliers and corporate actions.
- [ ] Implement aligned aggregate market-value history.
- [ ] Implement market-wide and individual-asset correlation per approved method.
- [ ] Test +1, −1, constant, missing and insufficient-overlap cases.
- [ ] Enforce aligned timestamps and no forward-fill.
- [ ] Implement funding comparison with fixed orientation and native interval semantics.
- [ ] Specify fees, execution assumptions and cost scenarios before net cost outputs.
- [ ] Keep market-wide correlation unavailable until prerequisites pass.

## EPIC 7 — DeFi

- [ ] Implement exact chain/pool/reserve/loan-market identities.
- [ ] Integrate validated Morpho loan-market and Kamino reserve subsets.
- [ ] Define loan asset/collateral orientation and decimals.
- [ ] Validate APY units and available-liquidity semantics.
- [ ] Validate collateral-enabled status from actual pair/risk configuration.
- [ ] Prevent duplicate pool liquidity and unsupported LP earnings estimates.
- [ ] Keep Jupiter execution estimates blocked until validated.
- [ ] Fix QA-07 sticky-header alignment on desktop and mobile.

## EPIC 8 — Trader Intelligence (specification first)

- [ ] Agree account/wallet identity and access-control model.
- [ ] Define realized/unrealized PnL, fees, funding, deposits, withdrawals and transfers.
- [ ] Define reporting window, timezone, exposure, volume, win rate and trade grouping.
- [ ] Establish ledger/fill completeness and reconciliation criteria.
- [ ] Define privacy, retention and user data deletion policy.
- [ ] Only then implement accounting and any scoring/ranking.

## EPIC 9 — Intelligence Event Feed (specification first)

- [ ] Agree event taxonomy and source hierarchy.
- [ ] Define entity/product relevance and deduplication.
- [ ] Define observed/published/effective timestamps and timezones.
- [ ] Select macro publisher feeds and validate calendars/releases.
- [ ] Define event evidence, summaries and correction handling.
- [ ] Defer ranking, urgency/impact scores, causal claims and alerts until validated.

## EPIC 10 — Shared frontend, all 16 pages, QA and launch

- [ ] Build reusable identity navigation and data provenance/status components.
- [ ] Build reusable metric cards, tables, charts, filters, sorting and CSV export.
- [ ] Implement loading, empty, unavailable, partial, stale, blocked and error states.
- [ ] Implement responsive and keyboard-accessible controls.
- [ ] Implement all 16 approved pages; none silently removed due to data gaps.
- [ ] Preserve origin, filters, selected network, builder, tab and exact entity context.
- [ ] Fix QA-02 holders fields reappearing where removed/deferred.
- [ ] Fix QA-03 Basis column reappearing where deferred.
- [ ] Fix QA-04 Best Venue Gap column reappearing where deferred.
- [ ] Fix QA-05 Off-Hours Move column reappearing where deferred.
- [ ] Fix QA-06 Robinhood Tokenized Assets breadcrumb/title.
- [ ] Fix QA-08 unknown IDs returning a default asset.
- [ ] Fix QA-09 Crypto dropdown filters and ensure production uses backend data.
- [ ] Fix QA-10 no Carry/arbitrage or standalone Pre-IPO routes.
- [ ] Execute inherited 739-case regression matrix against actual implementation.
- [ ] Add unit, integration, API contract and end-to-end tests.
- [ ] Test exports, back navigation, filters, sorting, provider failures and mobile layouts.
- [ ] Complete security, performance, recovery, quota and data-rights checks.
- [ ] Prepare runbooks, monitoring, backup/restore and rollback plan.
- [ ] Obtain explicit product-owner launch approval.

## Definition of done

A task is done only when code is merged, tests are executed, evidence is recorded, metric readiness is updated, documentation reflects the implementation and remaining limitations are explicit. A mock UI, successful one-off request, written plan or code change without executed evidence is not completion evidence.
