# RWAs Intelligence — Progress and Decision Log

**Last updated:** 2026-10-30  
**Status:** PR #7 is merged. The Home dashboard, Crypto Screener, page-specific workspaces and Tokenized RWA Screener/catalogue API are in `main`. Sprint 3 product-detail navigation and exact product lookup are in progress on `feat/rwa-product-detail-navigation`; validation and PR review remain pending.

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


## 10. Perpetual contract migration history — merged in PR #5

Branch: `feat/perpetual-contract-migration-history`.

The current increment adds evidence-bearing migration events with predecessor/successor links and native identifier snapshots. Symbol-only changes retain the same canonical contract and record previous/new symbols; native market ID changes, venue migrations and replacements link distinct contract records; delisting/expiry are terminal events. Self-links, missing references, duplicate events and lineage cycles are rejected. The events do not assert economic equivalence or rewrite historical observations.

The event date is a calendar date. Intraday cutover precision, observation-to-contract lineage, contract lifecycle effective periods and source reconciliation remain outside this increment. Migration evidence is required and verification defaults to false.

PR #5 merged at `10349dec896de876fcb3ffb697345943a5fbefe3`. Final push run `40988240946` and PR run `40988381700` passed; backend Ruff, 28 tests, Alembic upgrade/downgrade and frontend dependency install, ESLint, TypeScript and production build passed.

## 10. Frontend Sprint 1 — Home and Crypto Screener

Merged in PR #6 at `b9540bd599f681a31448d1dd0f35390ed8d49dd7`.

Scope:
- Home includes separate Trending Crypto and Trending Tokenized Assets workspaces alongside headline metric cards, provider coverage, discovery links and the approved 16-page directory.
- Crypto Screener has a dedicated route, search, category/network filter controls, sort field/direction, reset behaviour, semantic table columns, responsive table layout and explicit unavailable state.
- No market rows, rankings, prices, volumes, market caps, counts or historical series are fabricated. CSV export and pagination remain disabled until a validated dataset exists.
- The proposed screener API is documented as a logical contract only; no deployed read endpoint is assumed.

This increment does not complete all sixteen detailed page workspaces or connect live data. Subsequent work includes shared provenance/status components, tokenized RWA discovery, remaining page-specific screens and backend API integration. See `docs/FRONTEND_SPRINT_1.md`.

## 11. Product-page workspace design

PR #6 also replaced the generic readiness-only route content with page-specific workspace configurations for the remaining approved surfaces. Each page receives its own metric labels, table columns, filter dimensions and interpretation note. Trader Intelligence and Event Feed remain explicitly reserved; their metrics are not activated before their specifications are approved. All data tables remain empty/unavailable until supported read APIs provide validated records.

## 12. Tokenized RWA Screener and catalogue read API

Implementation branch: `feat/tokenized-rwa-screener`.

This increment adds a dedicated Tokenized RWA Screener page, shared availability/provenance components, a same-origin Next.js API proxy, and a read-only FastAPI catalogue endpoint. The endpoint returns effective RWA-classified registry products once each, joins underlying and issuer identity, exposes classification evidence, lists product-level deployment records and applies network filters only to verified deployments. Registry counts are explicitly not represented as provider-complete universe coverage. Market metrics remain unavailable because no validated observations are connected.

Frontend automated tests cover shared status/provenance disclosures, product identity display, deployment expansion, verified-network filter requests and API-not-configured state. Backend tests cover product distinctness, effective classification, verified-network filtering, search, facets, pagination and input validation. Implementation commit `00cf89fb6ca9e3e330eeb2bd74efad09a25f4691` passed push workflow `40991605769`: backend Ruff, 33 pytest tests and Alembic upgrade/downgrade passed; frontend dependency install, ESLint, TypeScript, 7 Vitest tests and Next.js production build passed. The final documentation commit and PR-triggered workflow remain required before review.


## 8. Vercel preview deployment and security remediation — 2026-10-30

- Created the dedicated Vercel project `intellisages-rwa` in the `apostleoffinance's projects` workspace and targeted the `IntelliSages/intellisages-rwa` repository.
- First preview build was blocked by Vercel because Next.js `15.5.6` was flagged as vulnerable (CVE-2025-66478). The deployment was not exposed as a successful preview.
- Updated the frontend runtime to Next.js `15.5.28`, React/React DOM `19.1.10`, and Sharp `0.35.5`; aligned `eslint-config-next` to `15.5.28`. Added a PostCSS override to `8.5.32` and updated Vitest to `4.1.12` to clear dependency audit findings.
- Updated Vitest JSX transformation to the current Oxc configuration and removed existing unused-import / anonymous-export lint warnings.
- Local sandbox validation after remediation: 7 frontend tests passed; ESLint passed; TypeScript passed; Next.js production build passed; `npm audit --audit-level=low` reported 0 vulnerabilities.
- Vercel and GitHub Actions are configured to use Node.js 24.x because npm 10 on Node 22 failed dependency-tree construction (`Cannot read properties of null (reading 'edgesOut')`); npm 11 on Node 24 generated the lockfile and completed dependency audit successfully.\n- The remediation is committed to the Tokenized RWA Screener PR branch. A fresh Vercel preview must still complete successfully before a preview URL is treated as ready. Production deployment remains out of scope.


## 13. Sprint 3 — canonical tokenized product detail (in progress)

Branch: `feat/rwa-product-detail-navigation`.

PR #7 is merged. This increment adds:
- Exact `GET /api/v1/catalogue/tokenized-products/{product_id}` lookup for one currently RWA-classified issuer product.
- Effective-date filtering and a strict 404 for unknown IDs, symbol-only lookups and products without an effective RWA classification.
- Product detail payload containing issuer and underlying identity, classification source/evidence, provider-global inclusion state, and product-level deployment records.
- A same-origin Next.js proxy route and a canonical product detail page linked from each screener result.
- Explicitly unavailable market metrics; registry identity and classification do not imply live market coverage, legal verification or asset backing.

**Validation status:** implementation has been committed to the feature branch. Backend Ruff/pytest/Alembic, frontend ESLint/TypeScript/Vitest/production build and both GitHub Actions workflows are not yet verified for this increment. Do not mark the work complete until those checks pass on the final commit.


## 14. Sprint 3 CI investigation — 2026-10-30

PR #8 frontend pull-request and push jobs failed in the Vitest step only. Dependency installation, ESLint and TypeScript completed successfully; the production-build step was skipped because tests failed. Backend quality succeeded in both trigger contexts.

Root cause from both job logs: `tests/tokenized-rwa-screener.test.tsx` used `screen.getByText(/NVDAx/)`, which became ambiguous after the screener correctly added an anchor to the canonical detail route while retaining the symbol label. The test now asserts the accessible link name and exact destination `/tokenized-rwa-screener/product-a`, and separately verifies the issuer text. This preserves the intended navigation behaviour instead of suppressing the duplicate-match failure.

Vercel preview deployment for the feature branch completed with state READY. This confirms the frontend build/deploy path, not backend connectivity or full application data readiness.


## 15. Sprint 3 CI remediation confirmed — 2026-10-30

- Root cause: frontend test used an ambiguous text query `getByText(/NVDAx/)` after the product name became a canonical detail link and remained alongside the symbol label.
- Correction: test now asserts the accessible link by role/name and exact route `/tokenized-rwa-screener/product-a`, plus the issuer display.
- CI rerun on commit `66f66f78b15ef5b3e1ef8106fcea4a977559f0e7` completed successfully: Backend quality passed; Frontend quality passed dependency installation, ESLint, TypeScript, Vitest and Next.js production build.
- The original failing run is superseded by the successful PR-triggered run `40999586576`. Vercel Preview Comments passed.
- The Vercel preview deployment is READY for the PR head. Backend hosting/configuration remains a separate dependency; a successful frontend preview does not make the API live.


## 16. Final verification of PR #8 — 2026-10-30

Validated PR head: `47d9ba0d580f65688206bb4a6b9000deebd7c5e1`.

- Pull-request quality workflow `40999685045`: completed successfully.
- Push quality workflow `40999682515`: completed successfully.
- Frontend quality: dependency installation, ESLint, TypeScript, Vitest and Next.js production build all passed.
- Backend quality: dependency installation, Ruff, pytest and Alembic migration verification all passed.
- Vercel deployment for the validated head: READY; preview comments report zero unresolved feedback.
- No open inline review threads or review submissions were returned for PR #8.
- The initial red checks were caused by one ambiguous Testing Library text query following intentional link navigation; the test was corrected to assert the canonical link route.


## 17. Sprint 4 — Registry import & reconciliation (implementation branch)

Branch: feat/registry-import-reconciliation, based on merged PR #8 commit 34208d88dcf427556541a54e291a651a53972885.

Implemented scope:
- Staged bulk import batches for underlying assets, issuers, issuer products and deployments (up to 500 source records per batch).
- Source-aware exact matching against active provider aliases, canonical keys, issuer + native product ID, and network + normalized deployment identifier.
- Weak exact-name and symbol candidates are labelled and cannot auto-resolve records. All rows remain in the human review queue, including exact provider-alias matches.
- Duplicate source identities in a batch are retained and marked as duplicates rather than silently dropped.
- Evidence-required reviewer decisions to link an existing canonical entity or create a new canonical entity; rejection requires a reason.
- Approved source identifiers are registered as verified provider aliases within the approval transaction.
- Append-only audit events for staged rows, duplicate detection, approval and rejection.
- Import API disabled unless a server-side REGISTRY_ADMIN_TOKEN is configured; requests require X-Registry-Admin-Token. The token must never be sent to browser code.
- Alembic migration 0005_registry_import_reconciliation adds batch, record, candidate and audit tables.

Validation status: final implementation commit `5a9b91ede61b8b5d5197fd3d6cba72ebace9f655` passed both push workflow `41046236485` and pull-request workflow `41046247755`. Backend Ruff passed; 50 pytest tests passed; Alembic upgrade and downgrade passed. Frontend dependency installation, ESLint, TypeScript, Vitest and Next.js production build passed. Vercel Preview Comments passed with zero unresolved feedback. PR #9 remains open and awaits review/merge. No provider feed is connected and no live data has been imported. This increment does not implement identity-provider-backed authentication, role provisioning, audit retention controls, provider rights validation or a browser upload UI.


## 18. Sprint 4 — final CI verification — 2026-10-30

Validated PR #9 head: `5a9b91ede61b8b5d5197fd3d6cba72ebace9f655`.

- Push quality workflow `41046236485`: completed successfully.
- Pull-request quality workflow `41046247755`: completed successfully.
- Backend: Ruff passed; 50 pytest tests passed; Alembic upgrade and downgrade passed.
- Frontend: dependency installation, ESLint, TypeScript, Vitest and Next.js production build passed.
- Vercel Preview Comments passed; no unresolved feedback was reported.
- PR #9 is open and unmerged. Merge remains a product-owner action.
- The first test run exposed duplicate candidate rows and stale batch status due to disabled SQLAlchemy autoflush. Candidate deduplication now preserves all match signals, and the status/count queries explicitly flush before reading. The final test run covers these cases, alias approval, parent-reference validation, duplicate rows, payload limits, and deployment normalization.
- The admin import API remains disabled until a server-side `REGISTRY_ADMIN_TOKEN` is configured. The supplied reviewer label is not an authenticated user identity; production use still requires identity-provider integration and role-based authorization.


## 19. Sprint 5 — CoinGecko RWA pilot ingestion (implementation branch)

Branch: \`feat/coingecko-rwa-pilot-ingestion\`, based on merged PR #9 commit \`fd8f8ebb49bb8073f42bdb3e6dea14557adbe0e4\`.

Implemented in this increment:
- CoinGecko RWA snapshot client for \`/rwas/list\`, optional \`/rwas/issuers/list\`, and per-underlying \`/rwas/{id}?tokens=true\`.
- API-key handling through environment variables only; demo/pro headers selected from the configured base URL. No secret is written to raw snapshots or manifests.
- Resumable raw JSON snapshots, per-record checkpoints, SHA-256 response hashes, bounded response size, conservative request pacing and retry handling.
- Normalization into underlying, issuer, network, issuer-product and deployment import records with raw provider payload and source metadata retained in the import envelope.
- Explicit platform-to-CAIP-2 network map; unknown slugs remain unresolved instead of guessed.
- Four phased stage operations. Products require approved underlying + issuer aliases; deployments require approved product + network aliases. Partial phases can be rerun after review without re-staging already staged source identities.
- Provider ingestion run API/table for persistent coverage, batch references and reconciliation status.
- Coverage report for CoinGecko-tracked RWA count, detail success/failure, issuer cross-check, tokens, platforms, staged batches, review queue, unresolved mappings and unsupported networks.
- Human review remains mandatory. Issuer labels are explicitly not verified legal names; products have no inferred entitlement/conversion ratio; deployments remain unverified and representation type unknown.

Validation status: automated adapter, phased dependency and migration tests are added. CI is pending. No live provider snapshot has been fetched in this environment because no CoinGecko API key or deployed registry admin endpoint was supplied. No production records have been staged.
