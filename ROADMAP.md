# RWAs Intelligence — Implementation Roadmap

**Status:** proposed delivery sequence. No phase is complete until its acceptance evidence is recorded in PROGRESS.md.

## Delivery principles

- Product correctness and identity precede breadth.
- Frontend can be developed alongside backend using typed fixtures, but mock data must remain unmistakably non-production.
- Start with read-only market intelligence; execution is outside MVP.
- Build a vertical slice end-to-end before scaling providers/pages.
- A phase exit requires tests and evidence, not merely merged code or a rendered screen.

## Phase 0 — Repository and prototype baseline

**Goal:** know what exists before selecting or changing technology.

Work:
- Inspect repository branches, files, package manifests, framework, deployment config, tests, CI and current commit.
- Inspect supplied HTML and extract page inventory, navigation, controls, current/proposed differences, sample data and removed/deferred elements.
- Identify which UI components are functional, mocked, hard-coded or inaccessible.
- Map existing docs to source evidence; retain the original HTML as a visual reference.
- Record architecture, dependency and security risks.

Exit criteria:
- Baseline audit completed with exact commit/ref and repository tree.
- No inferred stack or assumed running backend.
- Screen inventory and mock/live separation documented.
- Known defects and decisions logged.

## Phase 1 — Domain model and data governance

**Goal:** establish canonical identity and reliable metric semantics.

Work:
- Define stable IDs for underlying, issuer, issuer product, deployment, network, venue, spot market, perpetual contract, pool and provider alias.
- Define effective-dated identity, classification, bridge and unit relationships.
- Implement metric dictionary and availability/coverage model.
- Define Option B economic supply, issuer separation, execution deduplication and mutually exclusive Crypto/RWA universe.
- Define source observation, retrieval, calculation and freshness timestamps.

Exit criteria:
- Database migrations and typed domain models reviewed.
- Fixtures pass symbol collision, bridge, independent issuer, network duplication and classification cases.
- No metric can be represented without unit/scope/status metadata.

## Phase 2 — Data platform foundation

**Goal:** ingest and preserve observations without making unsupported claims.

Work:
- Choose server-side adapter framework after Phase 0 audit.
- Implement provider registry/configuration, secrets management, request logging and source budgets.
- Build raw response storage, normalized observation storage, idempotent ingestion, checkpointed pagination and retry policy.
- Implement validation and quarantine for malformed/unmapped/incompatible observations.
- Build materialized snapshots and source coverage records.

Exit criteria:
- Repeat ingestion is idempotent.
- Failed pagination remains partial and cannot publish complete totals.
- Raw evidence and normalized values can be traced to provider/request/version.
- Auth/rate-limit/schema failures are distinct.

## Phase 3 — First vertical slice: Home + canonical discovery

**Goal:** prove the end-to-end product architecture with limited, evidence-backed scope.

Work:
- Implement Crypto and tokenized RWA catalogue adapters.
- Implement complete eligibility/pagination for declared scope or label covered universe honestly.
- Implement Home read models and top-ten ranking after full eligible ingestion.
- Implement underlying discovery, issuer product expansion, verified deployments and exact detail navigation.
- Implement CSV with IDs, units and coverage.

Exit criteria:
- NVIDIA example keeps NVDAx/NVDAon distinct.
- Same product across networks appears once in All Networks.
- Trending ranking includes eligible assets from later pages.
- Incomplete or unavailable totals do not display as complete.
- Back/reopen retains identity and context.

## Phase 4 — Issuer and venue vertical slices

**Goal:** add issuer-specific catalogues and exact spot/perpetual contexts.

Suggested order, subject to access readiness:
1. CoinGecko RWA catalogue and provider alias mapping.
2. xStocks / issuer products and deployments.
3. Robinhood Tokenized Assets.
4. Backpack securities with RFQ/listed-market distinction.
5. Ondo and bStocks when authenticated/authorized access is available.
6. PreStocks and Paimon with explicit source/legal limitations.
7. GeckoTerminal pool discovery and exact onchain spot observations.
8. Hyperliquid HIP-3, Lighter RH/Core, Kraken and Backpack perps with exact market/builder IDs.

Exit criteria:
- Each issuer has its own coverage/readiness report.
- No provider category is treated as a legal issuer catalogue.
- Each product's network membership is verified per product.
- Perp market IDs include venue/domain/builder context.
- Five-entry preview expands/collapses after eligibility filtering.

## Phase 5 — History, correlation and funding

**Goal:** enable comparisons only where history and semantics support them.

Work:
- Build completed-bar/funding history collectors.
- Store effective-dated membership, multipliers, corporate actions and instrument metadata.
- Align UTC series and enforce minimum observation/gap rules.
- Implement approved market-value correlation and individual-price correlation.
- Normalize funding units, intervals and sign orientation.
- Implement cost scenarios only when four execution legs, fee tier, quotes, impact and assumptions are present.

Exit criteria:
- No synthetic history or forward-fill.
- Correlation tests include +1, −1, constant, missing and insufficient-overlap cases.
- Funding rates from different native intervals normalize correctly.
- Gross funding and net scenario costs are clearly separated.

## Phase 6 — DeFi, Trader Intelligence and Event Feed

**Goal:** implement remaining intelligence surfaces with jointly approved definitions.

DeFi:
- Exact pool/reserve/loan-market identities.
- Loan asset vs collateral semantics.
- Rates, reserves, available liquidity and collateral configuration.
- No user-specific borrow allowance inference.

Trader Intelligence:
- Jointly specify account/wallet identity, data permissions, realized/unrealized PnL, fees, funding, deposits/withdrawals, positions, volume, exposure, windows and win-rate methodology.
- Prove ledger completeness before profitability claims.
- No ranking/scoring until approved and validated.

Event Feed:
- Jointly specify event taxonomy, source hierarchy, timestamp, entity relevance, deduplication and evidence.
- Integrate macro publishers only after source and release-calendar validation.
- No impact/urgency score, causal claim or alerts without approved methodology.

Exit criteria:
- Each domain has a signed metric/specification and acceptance fixtures.
- Deferred systems remain unavailable until then.

## Phase 7 — Production hardening and launch

Work:
- Security review, dependency and secret scanning, authz review and privacy review.
- Load/performance tests, provider quota tests, retry/circuit-breaker tests and recovery drills.
- Database backup/restore and migration rehearsal.
- Monitoring for ingestion lag, freshness, coverage, page failures, mapping failures and metric availability.
- Operational runbooks, incident response, provider change process and data-quality dashboard.
- Production environment and release/rollback plan.

Exit criteria:
- Production entitlement and export rights documented.
- All release-blocking tests pass.
- No critical/high unresolved security issue.
- SLOs are measured and approved rather than guessed.
- Rollback and recovery tested.

## Cross-phase release gates

A feature is not production-ready until:
- identity is resolved;
- source and access are authorized;
- units and formula are validated;
- coverage is declared and sufficient for the claim;
- historical readiness is proven where history is displayed;
- aggregation/deduplication fixtures pass;
- API and UI expose unavailable/partial/stale states;
- QA evidence is recorded.
