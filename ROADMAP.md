# RWAs Intelligence — Implementation Roadmap

**Governing baseline:** [MVP_IMPLEMENTATION_BLUEPRINT.md](MVP_IMPLEMENTATION_BLUEPRINT.md). If this roadmap and the blueprint appear inconsistent, the blueprint governs approved MVP scope, page-by-page launch qualifications, work-package order and release gates. This file maps that baseline into the dependency-oriented engineering phases below.

**Status:** proposed delivery sequence. No phase is complete until acceptance evidence is recorded in PROGRESS.md.

## Delivery principles

- Deliver the complete 16-page MVP experience, with live metrics enabled only when individually validated.
- Product correctness and identity precede breadth and aggregation.
- Frontend may proceed against typed fixtures/API contracts, but mock data must never leak into production.
- Start with read-only market intelligence; execution is outside MVP.
- Build an end-to-end vertical slice before scaling providers/pages.
- A phase exit requires tests and evidence, not merely merged code or a rendered screen.
- Keep documentation completeness, application readiness and data readiness separate.

## Work-package sequence

The governing dependency chain is:

**Scope/acceptance baseline → canonical identity registry → provider adapters/raw evidence → normalization/coverage/history → metric calculation/availability API → shared UI → all 16 pages → regression/acceptance → controlled MVP launch → post-launch coverage expansion → deeper intelligence engines.**

The source blueprint estimates approximately 8–12 weeks for a small experienced team. This is a planning envelope, not a delivery commitment.

## Phase 0 — Scope, repository and prototype baseline

**Goal:** freeze the MVP and establish what exists before selecting/changing technology.

Work:
- Freeze all 16 approved pages and their launch qualifications.
- Inspect repository branches, files, package manifests, framework, deployment config, tests, CI and current commit.
- Inspect supplied HTML and inventory page objects, navigation, controls, current/proposed differences, sample data and removed/deferred elements.
- Turn inherited QA-01 through QA-10 into explicit acceptance tests.
- Establish per-page/per-metric readiness and source evidence inventory.
- Preserve HTML reference evidence; identify functional, mocked, hard-coded or inaccessible UI.
- Record architecture, dependency, security, licensing and operational risks.

Exit criteria:
- Baseline audit records exact commit/ref and repository tree.
- No inferred stack or assumed running backend.
- Screen inventory, mock/live separation, defects and decisions documented.
- No ambiguity about approved MVP scope.

## Phase 1 — Canonical identity and classification registry

**Goal:** establish the identity foundation for trustworthy discovery and aggregation.

Work:
- Model underlyings, issuers, issuer products, networks, deployments, venues, spot markets, perpetual contracts, pools, loan markets and provider aliases.
- Define effective-dated identity, classification, bridge/wrapper and unit relationships.
- Implement approved inclusion/exclusion and double-counting rules.
- Resolve native IDs, network/domain context and product-specific deployment mappings.
- Add economic-supply groups and evidence references.
- Test symbol collisions, NVDAx/NVDAon, bridges, wrappers, duplicate venues, independent issuers, multi-network products and unknown IDs.

Exit criteria:
- Schema/migrations and typed models reviewed.
- Identity fixtures pass.
- Declared eligible catalogue reconciles or missing scope is explicit; no completeness claims from partial evidence.

## Phase 2 — Provider adapters, raw evidence and ingestion

**Goal:** ingest only permitted, validated observations with traceable source evidence.

Work:
- Prioritize Tier A candidates and selected Tier B subsets in MVP_IMPLEMENTATION_BLUEPRINT.md; Tier C remains blocked/unverified until evidence changes.
- Confirm exact route, auth, entitlement, terms, units, native identifiers and redistribution/export rights.
- Build adapter interfaces, sanitized raw fixtures and request metadata.
- Implement pagination checkpoints, bounded retries, quota controls, idempotency, quarantine and explicit partial/blocked states.
- Separate source-native records from normalized observations.
- Run provider onboarding checklist before production approval.

Exit criteria:
- Each enabled launch metric has a reproducible input path and documented coverage.
- Failed pagination cannot publish complete totals.
- Raw evidence and normalized values are traceable.

## Phase 3 — Normalization, history, coverage and metric engine

**Goal:** make every enabled metric reproducible and readiness-aware.

Work:
- Normalize timestamps, decimals, units, funding intervals and market identifiers.
- Preserve source time, retrieval time and calculation time separately.
- Build completed-interval history ingestion/backfill and explicit gap detection.
- Implement metric dictionary as versioned calculations.
- Attach status, reason, coverage, freshness, formula version and source provenance.
- Implement approved deduplication and aggregation only after identity rules pass.

Exit criteria:
- Every enabled metric reproduces from known inputs.
- Unit/formula/history tests pass.
- Missing or incompatible observations remain unavailable/partial rather than fabricated.

## Phase 4 — Shared UI and all 16 MVP pages

**Goal:** build the complete product experience against readiness-aware APIs.

Work:
- Implement shared identity navigation, data status/provenance, cards, tables, charts, filters, sorting, CSV, loading/failure states and responsive layouts.
- Build all 16 pages against approved specifications.
- Keep each page visible even where particular metrics are unavailable/restricted.
- Enforce compact Spot venue expansion on broad underlying pages and at-most-five Perpetual preview with View all/Collapse where specified.
- Preserve issuer-specific and builder-specific contexts.
- Ensure production never falls back to illustrative/mock values.

Exit criteria:
- All 16 pages are reachable and usable.
- Shared behaviours pass cross-page tests.
- No page silently substitutes mock or unrelated values.

## Phase 5 — Regression, operational readiness and controlled launch

**Goal:** prove critical behaviour and operational ability to support live claims.

Work:
- Resolve inherited QA-01–QA-10.
- Execute the inherited 739-case matrix against the actual implementation, in batches; retain test IDs/status/evidence.
- Test provider failures, stale observations, interrupted pagination, mobile, exports and navigation.
- Verify secrets/access controls, data rights, monitoring, backup/restore, incident handling and ingestion ownership.
- Prepare deployment, rollback and runbooks.

Exit criteria:
- Critical behaviours pass and no known critical QA failure remains open.
- Every live claim is supported by validated semantics, units, source and coverage/freshness.
- Provider permissions and usage/redistribution requirements are confirmed.
- Non-critical failures are documented and accepted by product owner.
- Monitoring and recovery are tested; product owner approves release.

## Post-launch phases

### Phase 6 — Coverage and reliability expansion
Complete eligible catalogue pagination/reconciliation, resolve quotas and rights, expand product/deployment mappings, improve history backfills, and resolve crypto-only aggregate, RWA overlap and volume deduplication blockers.

### Phase 7 — Deeper analytical comparisons
Enable historical performance/correlation, funding-cost comparisons, broader DeFi coverage and historical product supply/valuation only when compatible inputs and accepted methodologies exist.

### Phase 8 — Trader Intelligence and Event Feed depth
Jointly specify and validate trader accounting, event taxonomy, source quality, macro/onchain/trading integrations, and any scoring/detection/ranking/alerts. No inferred engine behaviour becomes approved scope.

### Phase 9 — Scale operations
Optimize storage/query/refresh, improve recovery and monitoring, and add specialized streaming/storage only when measured workloads justify them. Review provider and hosting costs against usage.

## Safe parallel work

- UI development against typed fixtures/API contracts while adapters are built.
- Identity fixtures and tests alongside registry schema.
- Provider entitlement checks alongside application development.
- Page layout work before every metric is ready, provided mock data cannot leak into production.

## Work that must wait

- Aggregate totals until identity, inclusion and overlap rules are implemented.
- Market-wide correlation until compatible history and stable membership exist.
- Deep Trader Intelligence accounting until semantics are jointly defined.
- Complete provider-catalogue claims until pagination/coverage are proven.
- Acceptance claims until tests run against the actual application.

## Cross-phase feature/release gates

A feature is not production-ready until identity is resolved; source/access is authorized; units/formula are validated; coverage is declared and sufficient for the claim; history is proven where displayed; aggregation fixtures pass; API/UI expose unavailable/partial/stale states; and QA evidence is recorded.

## Change control

Any scope, methodology, provider, cadence or release-gate change must be recorded in PROGRESS.md and approved by the product owner. The governing MVP blueprint and RULES.md remain binding.
