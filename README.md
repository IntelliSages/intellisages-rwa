# RWAs Intelligence

**Analytic Sages' market-data and research intelligence platform for tokenized real-world assets (RWAs).**

RWAs Intelligence connects asset discovery, issuer products, blockchain deployments, spot and perpetual markets, funding, DeFi opportunities, trader intelligence and relevant market/onchain/macro events. It helps users move from a market-wide question to the exact instrument, issuer, network, venue and observation behind an answer.

> **Product principle:** a number is useful only when its meaning, identity, scope, time and coverage are clear. Partial or missing observations must remain visible; a successful API response is not proof of complete market coverage.

## Documentation map

| Document | Purpose |
|---|---|
| [RULES.md](RULES.md) | Binding identity, metric, evidence, aggregation, safety and implementation rules |
| [PRD.md](PRD.md) | Product vision, users, MVP scope, journeys and functional requirements |
| [ROADMAP.md](ROADMAP.md) | Delivery phases, dependencies, milestones and release gates |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Proposed system architecture, domain model, ingestion and serving design |
| [TASKS.md](TASKS.md) | Engineering work breakdown and acceptance tasks |
| [PROGRESS.md](PROGRESS.md) | Verified implementation status and decision log |
| [docs/BASELINE_AUDIT.md](docs/BASELINE_AUDIT.md) | Repository and supplied prototype baseline; known gaps |
| [docs/FRONTEND_SPEC.md](docs/FRONTEND_SPEC.md) | Screen inventory, interaction rules and UI states |
| [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md) | Shared metric meanings, units, formulas and availability rules |
| [docs/DATA_IDENTITY_AND_AGGREGATION.md](docs/DATA_IDENTITY_AND_AGGREGATION.md) | Canonical identity, classification, supply, volume and deduplication |
| [docs/PROVIDER_ENDPOINT_REGISTRY.md](docs/PROVIDER_ENDPOINT_REGISTRY.md) | Provider routes, retained evidence, access and remaining validation |
| [docs/API_CONTRACTS.md](docs/API_CONTRACTS.md) | Proposed internal read APIs and typed response contracts |
| [docs/VALIDATION_MATRIX.md](docs/VALIDATION_MATRIX.md) | Metric readiness, source coverage, blockers and QA criteria |
| [docs/RESEARCH_AND_OPEN_DECISIONS.md](docs/RESEARCH_AND_OPEN_DECISIONS.md) | External context, research implications and unresolved product decisions |

## Product scope

The supplied MVP inventory includes Home, Crypto Screener, Tokenized RWA Screener, Correlation, HIP-3, Ondo, bStocks, xStocks, Backpack, Robinhood Tokenized Assets, PreStocks, Paimon, Funding Rates, DeFi, Trader Intelligence and Event Feed.

The detailed page and metric scope is governed by PRD.md, FRONTEND_SPEC.md and DATA_DICTIONARY.md. A feature being visible in a mockup does not prove its backend is implemented or its data is production-ready.

## Current status

Documentation is being established from the product-owner brief, supplied MVP review HTML, Home specification, shared metric dictionary, identity/aggregation rules, provider endpoint registry and backend-contract proposal.

**No production implementation, deployed backend, live collector, complete universe coverage, production API entitlement or passing integration test is asserted by these documents.** See PROGRESS.md and VALIDATION_MATRIX.md for evidence-based status.

## Engineering approach

1. Preserve approved product decisions and source evidence.
2. Audit the actual repository and prototype before choosing or replacing a stack.
3. Build canonical identity and data-quality foundations before market-wide aggregation.
4. Implement provider adapters independently from domain calculations and UI.
5. Serve typed, provenance-aware read models; never let the UI infer missing data as zero.
6. Deliver incrementally, with reproducible fixtures, regression tests and release gates.

## External research references

- [CoinGecko API](https://www.coingecko.com/en/api) — crypto, tokenized RWA, onchain and historical market-data families.
- [Hyperliquid HIP-3](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals) — builder-deployed perp DEX and market context.
- [Hyperliquid perpetual API](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals) — native perp market data and builder-specific request context.
- [ERC-3643 specification](https://eips.ethereum.org/EIPS/eip-3643) — permissioned token transfer and identity/compliance interfaces; a technical standard is not legal approval.
- [ERC-3643 overview](https://www.erc3643.org/the-standard) — identity and compliance concepts.

## Working agreement

Classify every new statement as **approved product decision**, **retained source evidence**, **proposal**, **unverified assumption**, **deferred scope** or **implementation result**. Update relevant documents together and keep the progress log honest.
