# RWAs Intelligence — Progress and Decision Log

**Last updated:** 2026-10-30  
**Status:** initial product research and documentation baseline committed; source-code implementation audit remains pending.

## 1. Verified inputs received

| Input | What it establishes | What it does not establish |
|---|---|---|
| Product vision and overview in conversation | Product purpose, users, journeys, MVP page inventory and governing principles | Deployed implementation or complete metric-level acceptance |
| Home Screener Specification | Home purpose, headline/table definitions, interactions, retained sample endpoint evidence and proposed implementation | Complete Crypto/RWA universes, adjusted global totals, historical correlation or production entitlement |
| Shared Metric Dictionary | 218 rendered table/card fields across fifteen pages plus Correlation/headline families | Production readiness of all listed metrics |
| Asset Identity, Classification and Double-Counting Rules | Four approved Option B decisions and detailed identity/aggregation rules | Completed registry or validated production collectors |
| Provider Endpoint Registry | Provider endpoints, retained sample findings, access limits, cadence targets and blockers | Fresh certification, full access, quota, licensing or complete source coverage |
| Data Integration and Backend Contracts | Proposed record semantics, normalization, read-service/filter contracts, history/error contracts and acceptance fixtures | Deployed API schema or tested production code |
| Final MVP Review HTML | Interactive current/proposed review shell, embedded product reference and original/current-baseline data | Live data, backend integration or production functionality |

## 2. Repository baseline

- Repository: IntelliSages/intellisages-rwa
- Default branch: main
- Repository is private and accessible through the connected GitHub integration.
- README.md existed as a minimal starter and was expanded.
- Initial repository metadata reported size 0; README was the only source file confirmed before this documentation work.
- Probes for package.json, pyproject.toml, requirements.txt, index.html, src/main.tsx, app/page.tsx and .gitignore returned 404 at the time of audit.
- Therefore no application framework, backend, database, deployment, CI or tests have been identified.
- The supplied HTML is a product-review/mock reference, not code found in the repository.

## 3. Documentation status

| Document | Status |
|---|---|
| README.md | [x] Expanded and linked |
| RULES.md | [x] Established |
| PRD.md | [x] Established |
| ROADMAP.md | [x] Established |
| ARCHITECTURE.md | [x] Proposed target architecture |
| TASKS.md | [x] Initial engineering backlog |
| PROGRESS.md | [x] Established |
| docs/BASELINE_AUDIT.md | [x] Established |
| docs/FRONTEND_SPEC.md | [x] Established |
| docs/DATA_DICTIONARY.md | [x] Metric definitions and grouped page families |
| docs/SCREEN_METRIC_INVENTORY.md | [x] Screen/field inventory index |
| docs/DATA_IDENTITY_AND_AGGREGATION.md | [x] Established |
| docs/PROVIDER_ENDPOINT_REGISTRY.md | [x] Established |
| docs/API_CONTRACTS.md | [x] Proposed read contracts |
| docs/VALIDATION_MATRIX.md | [x] Retained readiness and QA matrix |
| docs/RESEARCH_AND_OPEN_DECISIONS.md | [x] External research and decisions |

The supplied HTML embeds 20 page objects and 1,061 review records. Review recommendations are IMPROVE 781, KEEP 156, REMOVE 76, DEFER 44 and ADD 4. The page inventory includes sixteen intended product surfaces, two legacy pages (Cross-Token Arbitrage and standalone Pre-IPO Markets) and two detail templates. The HTML also contains Spot–Perp Carry and Paimon Deals/Events tabs that conflict with settled scope. The Home HTML's +0.61 24H correlation is illustrative; approved Home state is unavailable market-wide history with returns-based 30D methodology. See docs/BASELINE_AUDIT.md and docs/FRONTEND_SPEC.md.

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

- CoinGecko publicly describes API families for coins/tokens, RWAs, exchanges/derivatives, onchain data/trades and history. This supports source-family fit, not our entitlement or coverage.
- Hyperliquid HIP-3 documentation describes builder-deployed perp DEXs with deployer-defined market/oracle specifications and independent DEX settings. This reinforces builder-scoped contract identity.
- ERC-3643 defines permissioned token and identity/compliance interfaces; the standard itself does not certify legal compliance or confer shareholder rights.
- SEC staff's 28 January 2026 tokenized securities statement distinguishes issuer-sponsored and third-party tokenization models and notes that structures/rights vary. It is a staff statement, not a Commission rule.
- BIS Annual Economic Report 2026 discusses interoperability fragmentation and bridge-related operational risks.

See docs/RESEARCH_AND_OPEN_DECISIONS.md for links and implications.

## 6. Current blockers / next actions

1. Complete source-code audit after code is added to the repository.
2. Inspect and map every embedded page/interaction in the supplied HTML to final screen requirements.
3. Reconcile every source metric/feature ID against DATA_DICTIONARY.md and SCREEN_METRIC_INVENTORY.md.
4. Validate provider access, quota, licensing and refresh feasibility.
5. Approve product legal/rights metadata model and disclosure review.
6. Agree reserved Trader Intelligence and Event Feed specifications.
7. Create domain schema and first vertical-slice implementation plan.

## 7. Decision log

| Date | Decision / finding | Status |
|---|---|---|
| 2026-10-30 | Use comprehensive product/rules/roadmap/architecture/tasks/progress and domain reference docs | Established |
| 2026-10-30 | Keep source evidence, proposals and implementation results explicitly separate | Binding |
| 2026-10-30 | Repository has no application source/config files confirmed at baseline; implementation stack remains open | Verified baseline |
| 2026-10-30 | Do not claim code or production readiness before implementation and tests are audited | Binding |
| 2026-10-30 | Add tokenization model/claim-rights metadata as a research recommendation, not an approved legal classifier | Proposal |

Update this file whenever a task changes status. Link commits, test runs, source fixtures or QA artifacts. Do not mark a task complete based only on a plan or code change.
