# RWAs Intelligence — Engineering Task Register

**Status:** initial work breakdown. Tasks are not complete until evidence is linked in PROGRESS.md.

Legend: [ ] not started · [~] in progress · [x] completed with evidence · [!] blocked.

## EPIC 0 — Repository and prototype audit
- [ ] Record repository tree, default branch, commit, framework, dependencies and scripts.
- [ ] Inspect existing frontend routes, components, state, API calls and mock fixtures.
- [ ] Inspect backend services, migrations, jobs, secrets and deployment configuration.
- [ ] Inspect CI, lint, typecheck, unit/integration/e2e tests and coverage.
- [ ] Inventory every mock page, tab, control, metric, navigation target and modal.
- [ ] Separate current baseline, proposed MVP changes, removed features and deferred scope.
- [ ] Record security, licensing, accessibility and operational risks.

## EPIC 1 — Domain model and registry
- [ ] Define canonical IDs and relational schema for underlying, issuer, issuer product, network, deployment, venue, market, pool and provider alias.
- [ ] Add effective-dated provider aliases, symbol/name aliases and contract migrations.
- [ ] Add representation type: independent issuance, bridge/wrapper or unknown.
- [ ] Add economic-supply groups and evidence references.
- [ ] Add versioned classification registry and provider-global inclusion evidence.
- [ ] Add exact builder/domain/market identity for perpetual contracts.
- [ ] Add registry import/reconciliation and unresolved mapping workflow.
- [ ] Test NVIDIA/NVDAx/NVDAon, duplicate tickers, bridge and multi-network cases.

## EPIC 2 — Data platform foundation
- [ ] Select database, migration and job orchestration technologies after audit.
- [ ] Define provider adapter interface and secret configuration.
- [ ] Implement raw response/fixture persistence with secret redaction.
- [ ] Implement normalized observation schema and decimal/unit handling.
- [ ] Implement pagination checkpoints and terminal-page validation.
- [ ] Implement bounded retries, rate budgets and idempotency.
- [ ] Implement quarantine for invalid/unmapped records.
- [ ] Implement coverage snapshots and job-state telemetry.
- [ ] Implement metric availability/status response contract.

## EPIC 3 — Home and broad screeners
- [ ] Implement complete eligible Crypto universe crawl or explicitly covered universe.
- [ ] Implement tokenized RWA underlying discovery and canonical catalogue.
- [ ] Implement Crypto/RWA classification and provider-global inclusion checks.
- [ ] Implement Home headline read model with honest unavailable/partial states.
- [ ] Implement volume ranking after full eligible ingestion, then top-ten selection.
- [ ] Implement numeric sorting, stable tie-break and null-last behaviour.
- [ ] Implement CSV schema with raw values, canonical IDs and coverage.
- [ ] Implement broad underlying detail and issuer-product expansion.
- [ ] Implement selected-network and All Networks semantics.
- [ ] Implement context-preserving navigation/back/reopen.

## EPIC 4 — Issuer integrations
- [ ] CoinGecko RWA catalogue/underlying/product adapter and entitlement test.
- [ ] xStocks catalogue pagination, contract mapping and supply history.
- [ ] Robinhood issuer catalogue and contract reconciliation.
- [ ] Backpack securities catalogue; separate RFQ and listed orderbooks.
- [ ] Ondo authenticated catalogue and market adapter.
- [ ] Binance/bStocks authorized catalogue and exact instrument mapping.
- [ ] PreStocks product/mint and Solana supply/decimals adapter.
- [ ] Paimon catalogue adapter and legal/terms review.
- [ ] Product-specific network and venue coverage reconciliation.
- [ ] Per-issuer data-quality and readiness report.

## EPIC 5 — Market and derivatives
- [ ] GeckoTerminal exact pool/token and pagination adapter.
- [ ] Execution-level deduplication fixtures across providers/router/pools.
- [ ] Hyperliquid first-DEX and HIP-3 builder-scoped adapter.
- [ ] Lighter RH and Core domain-specific adapter.
- [ ] Kraken futures instrument/funding/orderbook adapter.
- [ ] Backpack listed perp/RFQ distinctions and funding adapter.
- [ ] Normalize mark, index, oracle, mid, bid/ask and last price semantics.
- [ ] Normalize open interest units and contract multipliers.
- [ ] Normalize funding sign, fraction/percent and payment intervals.

## EPIC 6 — History and analytics
- [ ] Implement completed interval history collection and retention.
- [ ] Store effective-dated units, multipliers, corporate actions and universe membership.
- [ ] Implement aligned aggregate market-value history.
- [ ] Implement market-wide and individual-asset correlation per approved method.
- [ ] Implement missing-pair, sample sufficiency and zero-variance checks.
- [ ] Implement funding comparison with fixed orientation.
- [ ] Specify and validate fees, execution assumptions and cost scenarios before net cost outputs.
- [ ] Gate every chart control on real series availability.

## EPIC 7 — DeFi
- [ ] Implement exact chain/pool/reserve identities.
- [ ] Integrate Morpho loan-market and Kamino reserve data.
- [ ] Define loan asset/collateral orientation and decimals.
- [ ] Validate APY units and available-liquidity semantics.
- [ ] Validate collateral-enabled status from actual pair/risk config.
- [ ] Prevent duplicate pool liquidity and unsupported LP earnings estimates.

## EPIC 8 — Trader Intelligence (specification first)
- [ ] Agree account/wallet identity and access-control model.
- [ ] Define realized/unrealized PnL, fees, funding, deposits, withdrawals and transfers.
- [ ] Define reporting window, timezone, exposure, volume, win rate and trade grouping.
- [ ] Establish ledger/fill completeness and reconciliation criteria.
- [ ] Define privacy, retention and user data deletion policy.
- [ ] Only then implement accounting and any scoring/ranking.

## EPIC 9 — Event Feed (specification first)
- [ ] Agree event taxonomy and source hierarchy.
- [ ] Define entity/product relevance and deduplication.
- [ ] Define observed/published/effective timestamps and timezones.
- [ ] Select macro publisher feeds and validate calendars/releases.
- [ ] Define event evidence, summaries and correction handling.
- [ ] Defer ranking, urgency/impact scores, causal claims and alerts until validated.

## EPIC 10 — Frontend, QA and launch
- [ ] Audit design system and create reusable table/card/chart/status components.
- [ ] Implement loading, empty, unavailable, partial, stale and error states.
- [ ] Implement responsive and keyboard-accessible controls.
- [ ] Add unit tests for formulas and normalization.
- [ ] Add integration tests for adapters, pagination and persistence.
- [ ] Add contract tests for API responses and UI state rendering.
- [ ] Add e2e journeys for underlying → issuer product → deployment → venue.
- [ ] Add export, back navigation, filters and sort regression tests.
- [ ] Complete security, performance, recovery and provider quota tests.
- [ ] Prepare production runbooks, monitoring and rollback plan.

## Definition of done

A task is done only when code is merged, tests are executed, evidence is recorded, metric readiness is updated, documentation reflects the implementation and any remaining limitation is explicit. A mock UI or successful one-off request is not completion evidence.
