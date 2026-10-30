# RWAs Intelligence — Product Requirements Document

**Product owner:** Analytic Sages  
**Product type:** RWA market-data, discovery and research intelligence platform  
**Status:** MVP product scope derived from supplied vision and supporting specifications.  
**Primary users:** traders, researchers and institutions.

## 1. Product vision

RWAs Intelligence is the shared place for understanding tokenized real-world assets and their trading markets. It connects asset discovery, issuer products, network activity, spot and perpetual markets, funding, DeFi opportunities, trader intelligence and relevant events.

Users should move from a market-wide question to the precise product, instrument and venue behind an observation. The platform should reveal which platforms are growing, where activity and liquidity are moving, and how tokenized assets relate to crypto and traditional markets.

The product is an intelligence and discovery surface, not an execution terminal. It must not imply that a market value, price, liquidity number or correlation is more complete or predictive than its evidence supports.

## 2. Users and jobs to be done

### Traders
- Identify the exact instrument and venue behind a ticker.
- Compare supported spot and perpetual venues.
- Inspect price, volume, open interest, funding, spread, depth and market context where validated.
- Avoid confusing issuer products with underlyings or spot assets with perpetuals.

### Researchers
- Use consistent definitions and reproducible historical comparisons.
- Track issuer/product/network coverage and adoption.
- Investigate changes in volume, liquidity, funding and market structure with provenance.
- Distinguish economic change from new listings, coverage changes or duplicated representations.

### Institutions
- Understand product identity, issuer, deployment and instrument rights/limitations.
- See exactly which networks, venues and observations are covered.
- Reproduce calculations and understand data limitations.
- Avoid unsupported market-wide claims.

## 3. Product identity model

The product preserves these distinct layers:

Underlying → Issuer → Issuer Product → Deployment(s) → Venue / Market → Observation / Execution

An underlying may be referenced by several issuer products. One product may have multiple deployments. A deployment may be listed in multiple pools/venues. A perpetual references an underlying or product but remains a distinct derivative instrument. A provider record is an external alias/observation, not the canonical entity.

Example: NVIDIA is an underlying. NVDAx and NVDAon are separate issuer products. Their deployments, pools and perpetual references must not collapse into one ticker record.

## 4. MVP screen inventory

| Screen / page | Primary user purpose |
|---|---|
| Home | Covered crypto and tokenized RWA overview; trending discovery |
| Crypto Screener | Discover and compare eligible ordinary crypto assets |
| Tokenized RWA Screener | Discover tokenized underlyings and navigate to distinct issuer products |
| Correlation | Compare aligned crypto and RWA return series |
| HIP-3 | Explore builder-deployed perpetual contracts in exact builder context |
| Ondo | Issuer-specific products, networks, markets and platform context |
| bStocks | Issuer/product-specific tokenized stock discovery |
| xStocks | Issuer-specific tokenized assets, deployments and trading activity |
| Backpack | Securities catalogue, RFQ/listed-market distinction and supported trading context |
| Robinhood Tokenized Assets | Issuer catalogue, tokenized products and covered DEX/market observations |
| PreStocks | Pre-IPO token product discovery and approved basket/index research fields |
| Paimon | Separate issued products; deals/events remain deferred/unavailable |
| Funding Rates | Compare supported perpetual funding observations and costs with explicit assumptions |
| DeFi | Discover relevant pools and lending markets; distinguish reserves, rates and borrow availability |
| Trader Intelligence | PnL, win rate, trading activity, volume and exposure; accounting to be specified |
| Event Feed | Market, onchain, trading, company/catalyst and macro observations; deeper engine reserved |

### Explicit exclusions
- No execution, order placement, custody or wallet signing.
- No standalone Pre-IPO page; pre-IPO information belongs inside platform pages.
- No Spot–Perp Carry/arbitrage subsystem.
- No restored removed order-book/Sources controls or deferred columns.
- No Paimon Launchpad Deals or Events/Settlements data beyond specified unavailable state.
- No unsupported event ranking, scoring, alerts or automated predictions.
- No complete Trader Intelligence accounting engine until jointly defined.

## 5. Core user journeys

### A — Underlying to issuer product
1. Researcher opens Home and Tokenized RWA Screener.
2. Searches/selects NVIDIA.
3. Broad NVIDIA page exposes separate issuer products such as NVDAx and NVDAon.
4. Expanding a product reveals verified deployments and actual venues.
5. Opening the product leads to its issuer-specific detail.
6. User inspects markets without losing issuer/product identity.

Acceptance: products are not merged; deployments do not multiply product counts or economic value; navigation uses canonical IDs.

### B — Issuer screener and network
1. Trader opens an issuer screener and selects a network.
2. Table shows one row per eligible issuer product with a verified deployment on that network.
3. Trading observations are network-specific where supported.
4. All Networks shows each product once, its verified network names and incomplete aggregation labels.
5. Opening a HIP-3 contract retains exact builder context.

Acceptance: no issuer-wide network inference; no duplicate All Networks product rows; selected network filters verified deployment membership.

### C — Historical comparison
1. Researcher chooses instruments/series and a window.
2. System verifies matching timestamps, units, history and membership coverage.
3. System computes approved returns/correlation.
4. Missing or insufficient history produces unavailable with an explanation.

Acceptance: a present-day API response alone does not enable a historical chart; no synthetic data or forward filling.

### D — Funding comparison
1. Trader chooses supported perpetual instruments/venues.
2. System preserves native rate units, sign convention and payment interval.
3. Comparisons use a fixed orientation and explain the period.
4. Cost estimates remain unavailable unless execution assumptions and required fee/quote inputs exist.

Acceptance: funding-only gross income is not described as net profit; estimated costs are not presented as observed costs.

## 6. Product-wide functional requirements

- Search by canonical identity, name, symbol and verified aliases; resolve collisions to distinct instruments.
- Filter by asset class, issuer, network, venue, instrument type and page-specific approved dimensions.
- Show exact source coverage, freshness and availability state at metric/table level.
- Support expandable compact Spot venue views on broad underlying pages.
- Show at most five Perpetual market entries initially, with View all and Collapse.
- Keep issuer-specific and builder-specific pages scoped to their instruments.
- Provide historical controls only when source history exists for the selected series.
- Provide metric tooltips and provenance/coverage explanations.
- Provide CSV export with raw values, canonical IDs, units, windows and coverage metadata.
- Support accessible responsive layouts and stable navigation/back behaviour.

## 7. Non-functional requirements

**Correctness:** stable/effective-dated canonical IDs, preserved decimals/native units, deterministic versioned aggregation and explicit partial coverage.

**Reliability:** idempotent/checkpointed ingestion, no complete totals from failed crawls, explicit stale state, and no outage-to-zero conversion.

**Security/privacy:** server-side secrets; separate privacy/authorization model for Trader Intelligence account data; no credentials or unnecessary personal data in exports/logs.

**Performance:** metric-specific caches and refresh plans after entitlement testing; materialized read models for long provider crawls; no unmeasured freshness SLA.

## 8. Metric governance

Every metric documents user purpose, exact entity scope, definition, unit, window, timezone, provider/endpoint/native field/entitlement, formula/denominator/valuation/rounding, identity and overlap rules, observation/retrieval/calculation timestamps, coverage/freshness/availability, history requirements, evidence and readiness. See DATA_DICTIONARY.md.

## 9. MVP success criteria

A user can discover an underlying and distinguish issuer products; inspect verified deployments and venues; compare supported instruments without ticker collisions; understand metric scope/limitations; reproduce calculations from saved observations and method versions; navigate without losing identity/context; export interpretable data; and receive honest partial/unavailable states.

Prefer a smaller verified universe over a larger misleading one.

## 10. Product-owner decisions still required

- Final metric-by-metric acceptance and unresolved historical UI differences.
- Trader Intelligence PnL accounting, account identity, fees/funding treatment, windows, exposure and win-rate definitions.
- Event Feed taxonomy, source policy, deduplication, relevance, ranking and alert requirements.
- PreStocks index constituent eligibility, rebalance and missing-data methodology approval.
- Exact CSV schema and export rights.
- Final source/coverage disclosures and minimum-history thresholds.
- Product-specific legal/rights disclosures and review ownership.
