# RWAs Intelligence — Progress and Decision Log

**Last updated:** 2026-10-30  
**Status:** Frontend foundation and canonical identity registry increments PRs #2, #3 and #4 are merged. Perpetual contract migration history is implemented on `feat/perpetual-contract-migration-history`; initial implementation CI passed on commit `8289736fe72924855c16d47be4fd3401d0613355`. Final documentation-commit and PR-triggered CI remain mandatory before review.

## 1. Verified implementation evidence

| Increment | Evidence | Result |
|---|---|---|
| Frontend foundation | PR #1 merged to main; merge commit b23f2b9a54d5b8a470fbc122b34a249da8b31c12 | Merged |
| Frontend quality | GitHub Actions run 40981455334 on merge commit | Passed: dependency install, ESLint, TypeScript and Next.js production build |
| Canonical identity registry | PR #2 merged at b1ca3171b1495e0c1516408567b653182e6815fa | Merged |
| Registry PR quality | GitHub Actions PR run 40983315689 | Passed: frontend and backend jobs |
| Backend lint/tests/migrations | Run 40983315689, Backend quality job | Ruff passed; 10 tests passed; Alembic upgrade and downgrade passed |
| Frontend regression gates | Run 40983315689, Frontend quality job | Dependency install, ESLint, TypeScript and production build passed |

The backend test run emitted one upstream deprecation warning from the Starlette/AnyIO test-client dependency chain. It did not fail the suite. The warning is recorded for dependency maintenance; no test failure remains on the current PR head.

## 2. Frontend baseline

The merged application uses Next.js 15, React 19 and TypeScript. It contains the responsive shell, global overview, all 16 approved navigation destinations, shared readiness-gated page workspaces and explicit not-found behaviour. It deliberately contains no production market-data claims or mock market-data fallback.

Frontend CI runs dependency installation, ESLint, TypeScript and production build.

## 3. Canonical identity registry — current implementation scope

The merged backend increment introduces a FastAPI + SQLAlchemy 2.x + Alembic foundation with PostgreSQL as the intended shared-environment database and SQLite isolated to tests.

Initial entities:
- Underlying asset
- Issuer
- Issuer product
- Network
- Product deployment
- Venue
- Perpetual contract
- Provider alias

Enforced behaviours:
- Issuer products are unique by issuer + native product ID.
- Different issuers may create distinct products referencing the same underlying.
- Deployments are scoped by product and network; EVM addresses are validated and normalized, while non-EVM identifiers preserve case.
- Provider aliases are exact and unique by provider + namespace + external ID.
- Builder-scoped perpetuals require an exact domain and preserve native market ID separately from display symbol.
- Unknown canonical IDs return not found; no default asset fallback.
- Unverified deployments remain explicitly unverified.

The merged implementation includes economic-supply groups, evidence-bearing memberships, effective-dated classifications, provider-global inclusion evidence and effective-dated provider alias history. It does not yet include evidence-backed bridge equivalence, spot/pool/loan-market entities, registry import/reconciliation, authentication or provider ingestion.

## 4. Governing product decisions

1. Count unique economic supply across networks (Option B).
2. Keep different issuers' products distinct (Option B).
3. Count each executed trade once (Option B).
4. Separate ordinary Crypto from tokenized RWA products (Option B).
5. Keep all 16 approved navigation pages present; page-level metrics may be unavailable/restricted with explicit reasons.
6. All Networks displays one row per issuer product with verified network names.
7. Exact builder/domain context is mandatory for HIP-3 and other scoped perps.
8. Market-wide correlation uses aligned aggregate market-value returns; individual assets use price returns.
9. No synthetic history, fake totals or illustrative fallback.
10. No execution service in MVP.
11. Trader accounting and deeper Event Feed engines remain reserved for joint specification.
12. Application readiness and data readiness are separate from documentation completeness.

## 5. Remaining canonical identity work

- Perpetual contract migration history (current feature branch; CI and review pending).
- Economic-supply groups and evidence-backed bridge/wrapper equivalence.
- Versioned Crypto/RWA classification and provider-global inclusion evidence.
- Spot-market, pool and lending-market identities.
- Registry bulk import, reconciliation and unresolved-mapping workflow.
- Authentication, authorization and audit logging before shared deployment.

## 6. Source readiness and limitations

No provider integration, production market observation, metric calculation or production data entitlement is asserted by this implementation. A registry record's existence does not prove its identity, backing, rights, deployment or source evidence; those remain explicit review responsibilities.

The MVP implementation blueprint remains the governing scope. See docs/IDENTITY_REGISTRY.md for the registry contract and omitted scope.

## 7. Merged identity extension — PR #3

PR #3 merged at `85558c8bf95c28f3b78dddcee00549e37c4b4160`. It adds economic-supply groups, evidence-bearing product memberships, effective-dated classifications and provider-global inclusion evidence. Its backend and frontend quality gates passed on commit `6005ea60ee620ab6cbe282834b3e356fa76dcaab` (push run `40985320170`, PR run `40985326916`).

## 8. Merged identity extension — PR #3 details

Branch `feat/identity-supply-classification` adds:
- Economic-supply groups and product memberships with effective dates, evidence references and explicit verification status.
- Overlap prevention so a product cannot be assigned to two concurrent economic-supply memberships.
- Versioned classification records for underlying assets and issuer products, including nullable provider-global inclusion evidence.
- Date-range overlap validation and filtered classification reads.

The merged work does not establish that two products are economically equivalent: membership requires evidence and remains unverified by default. Provider-global inclusion is nullable, not inferred.

## 9. Effective-dated provider aliases — merged in PR #4

Branch `feat/effective-dated-provider-aliases` adds effective start/end dates to provider aliases, exact symbol/name namespaces, a controlled close-period endpoint, non-overlapping alias reassignment and historical resolution using an explicit `as_of` date. Existing rows retain a null start date because their historical start is unknown. Contract migration history remains a separate follow-on task.

Final implementation commit `626ea47bc3de761a893a06bef73b2c79247c31a3` passed push run `40986565711` and PR run `40986712177`. Backend: Ruff passed, 22 tests passed, Alembic upgrade/downgrade passed. Frontend: dependency install, ESLint, TypeScript and production build passed. PR #4 is merged at `28ac009c88c9062657a422d01f80e83b91188456`.


## 10. Perpetual contract migration history — implementation in progress

Branch: `feat/perpetual-contract-migration-history`.

The current increment adds evidence-bearing migration events with predecessor/successor links and native identifier snapshots. Symbol-only changes retain the same canonical contract and record previous/new symbols; native market ID changes, venue migrations and replacements link distinct contract records; delisting/expiry are terminal events. Self-links, missing references, duplicate events and lineage cycles are rejected. The events do not assert economic equivalence or rewrite historical observations.

The event date is a calendar date. Intraday cutover precision, observation-to-contract lineage, contract lifecycle effective periods and source reconciliation remain outside this increment. Migration evidence is required and verification defaults to false.

Initial implementation validation on commit `8289736fe72924855c16d47be4fd3401d0613355`: GitHub Actions push run `40988066268` passed both quality jobs. Backend: Ruff passed, 28 tests passed, Alembic upgrade/downgrade passed. Frontend: dependency install, ESLint, TypeScript and production build passed. The final documentation commit must be revalidated before PR creation.
