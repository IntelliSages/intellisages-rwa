# RWAs Intelligence — Progress and Decision Log

**Last updated:** 2026-10-30  
**Status:** documentation baseline established; implementation status not yet audited.

## 1. Verified inputs received

| Input | What it establishes | What it does not establish |
|---|---|---|
| Product vision and overview in conversation | Product purpose, users, journeys, MVP page inventory and governing principles | Deployed implementation or complete metric-level acceptance |
| Home Screener Specification | Home purpose, headline/table definitions, interaction rules, retained sample endpoint evidence and proposed implementation | Complete Crypto/RWA universes, adjusted global totals, historical correlation or production entitlement |
| Shared Metric Dictionary | Broad metric inventory and page-specific definitions/readiness notes | Production readiness of all listed metrics |
| Asset Identity, Classification and Double-Counting Rules | Four approved Option B decisions and detailed identity/aggregation rules | Completed registry or validated production collectors |
| Provider Endpoint Registry | Retained endpoint investigation and provider-specific validation boundaries | Fresh certification, full access, quota, licensing or complete source coverage |
| Data Integration and Backend Contracts | Proposed record semantics, normalization, read-service/filter contracts and acceptance fixtures | Deployed API schema or tested production code |
| Final MVP Review HTML | Interactive visual review candidate, current/proposed presentation, illustrative/sample-data warnings and documented prototype corrections | Live data, backend integration, complete production functionality |

## 2. Repository baseline

- Repository: IntelliSages/intellisages-rwa
- Default branch: main
- Repository is accessible through the connected GitHub account.
- README.md existed as a minimal starter and has been expanded.
- Full source tree and code implementation have not yet been audited in this documentation pass.
- No framework, backend, database, deployment, tests or running service is asserted until inspected.

## 3. Documentation status

| Document | Status |
|---|---|
| README.md | [x] Expanded |
| RULES.md | [x] Established |
| PRD.md | [x] Established |
| ROADMAP.md | [ ] Pending |
| ARCHITECTURE.md | [ ] Pending |
| TASKS.md | [ ] Pending |
| PROGRESS.md | [x] Established |
| docs/BASELINE_AUDIT.md | [ ] Pending |
| docs/FRONTEND_SPEC.md | [ ] Pending |
| docs/DATA_DICTIONARY.md | [ ] Pending |
| docs/DATA_IDENTITY_AND_AGGREGATION.md | [ ] Pending |
| docs/PROVIDER_ENDPOINT_REGISTRY.md | [ ] Pending |
| docs/API_CONTRACTS.md | [ ] Pending |
| docs/VALIDATION_MATRIX.md | [ ] Pending |
| docs/RESEARCH_AND_OPEN_DECISIONS.md | [ ] Pending |

## 4. Confirmed product decisions carried forward

1. Count unique economic supply across networks (Option B).
2. Keep different issuers' products distinct (Option B).
3. Count each executed trade once (Option B).
4. Separate ordinary Crypto from tokenized RWA products (Option B).
5. All Networks displays one row per issuer product with verified network names.
6. Exact builder/domain context is mandatory for HIP-3 and other scoped perps.
7. Market-wide correlation uses aligned aggregate market-value returns; individual assets use price returns.
8. No synthetic history, fake totals or illustrative fallback.
9. No execution service in MVP.
10. Trader accounting and deeper Event Feed engines remain reserved for joint specification.

## 5. External research checked

- CoinGecko currently describes its API as covering coins/tokens, RWAs, exchanges, derivatives, onchain pools/trades and historical charts. This supports a broad source-family fit, not the exact entitlements or full coverage of our saved requests.
- Hyperliquid HIP-3 documentation describes builder-deployed perp DEXs with deployer-defined market/oracle specifications and independent DEX settings. This reinforces builder-scoped contract identity.
- ERC-3643 defines permissioned token and identity/compliance interfaces. The standard itself does not certify that a particular token is legally compliant or confer shareholder rights.

See docs/RESEARCH_AND_OPEN_DECISIONS.md for links and implications.

## 6. Current blockers / next actions

1. Complete repository tree and code audit.
2. Compare current frontend implementation against the supplied HTML review candidate.
3. Recover/inspect the full source metric dictionary and preserve all page-specific definitions.
4. Map every metric to source endpoint, field, units, formula, evidence and validation status.
5. Validate provider access, quota, licensing and refresh feasibility.
6. Agree reserved Trader Intelligence and Event Feed specifications.
7. Create initial domain schema and vertical-slice implementation plan.

## 7. Decision log

| Date | Decision / finding | Status |
|---|---|---|
| 2026-10-30 | Use a documentation hierarchy with product, rules, roadmap, architecture, tasks/progress and domain reference docs | Established |
| 2026-10-30 | Keep source evidence, proposals and implementation results explicitly separate | Binding |
| 2026-10-30 | Do not claim code or production readiness before repository/test audit | Binding |

Update this file whenever a task changes status. Link commits, test runs, source fixtures or QA artifacts. Do not mark a task complete based only on a plan or a code change.
