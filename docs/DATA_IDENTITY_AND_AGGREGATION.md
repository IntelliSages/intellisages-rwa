# Data Identity, Classification and Aggregation Rules

**Authority:** preserves the four settled Option B decisions from the supplied identity/aggregation document.

## 1. Four approved decisions

### Decision 1 — Unique economic supply across networks
A product deployed on Ethereum and Solana may have two representations of the same issued supply. Preserve each deployment but count the economic units once. Use verified issuer-wide totals where possible. Unknown bridge relationships make consolidated value unavailable or explicitly partial.

### Decision 2 — Different issuers' products remain distinct
NVDAx and NVDAon are distinct issuer products. Preserve issuer, product ID, supply, backing, rights, deployments and markets. A broad NVIDIA page may add verified non-overlapping product values once each. The result is tokenized NVIDIA value, not NVIDIA's traditional equity market cap.

### Decision 3 — Each execution is counted once
A DEX execution reported by a router or market-data provider remains one execution. A transaction can contain multiple real execution legs, so transaction hash alone is not a universal key. Exclude failed executions and non-trading transfers.

### Decision 4 — Crypto and tokenized RWA products are mutually exclusive
Classification is internal and based on verified provider IDs, networks, contracts/mints and issuer mappings. Ordinary infrastructure coins associated with RWAs remain Crypto. A tokenized security belongs in its RWA category. If adjusted provider-global coverage is unresolved, label provider-reported figures rather than claim a complete adjusted total.

## 2. Entity taxonomy

| Entity | Identity key / meaning |
|---|---|
| Underlying | Stable economic reference, e.g. company, commodity or fund |
| Issuer | Organization issuing a particular product |
| Issuer product | Issuer-native product ID + underlying relation + instrument form + unit/backing/rights |
| Network | Canonical chain namespace |
| Deployment | Product + network + contract/mint + effective dates |
| Bridge representation | Deployment backed by assets locked/held elsewhere |
| Venue | Exchange, DEX or protocol |
| Spot market | Exact pair/pool/market on a venue |
| Perp contract | Venue/domain + builder/DEX + native market ID/name + contract metadata |
| Pool | Network + pool address + protocol + base/quote/reserve semantics |
| Execution | Successful matched trade/swap leg with native event identity |
| Provider alias | Provider + namespace + external ID mapped to canonical entity |

## 3. Registry requirements

- Assign stable internal IDs to underlyings, issuers and issuer products.
- Attach provider IDs to the correct entity with source/effective dates.
- Never join by symbol alone.
- EVM addresses may be normalized for lookup while retaining checksum display; preserve case-sensitive non-EVM mint identifiers.
- Contract migrations and symbol reuse require dated mappings.
- Record representation as independent issuance, bridge/wrapper or unknown.
- Record economic-supply group, origin relationship, unit conversion and supporting evidence.
- An issuer-supported network does not prove every product is deployed there.
- Keep legal/backing claims separate from trading observations.
- Pool identity is network + pool address.
- Centralized markets/perps use venue + native market ID, plus builder/domain where applicable.

## 4. Supply and value

For each product/time, count independently issued economic units once.

Illustrative bridge example: origin supply 100 includes 40 locked in a bridge; destination wrapped supply is 40. Unique economic supply is 100, not 140. An accessible breakdown may show 60 unlocked origin units and 40 destination units, with the 40 locked reserve separately identified.

Independent additional issuance can be counted only after unit, backing and overlap checks.

Issuer product value = unique verified economic supply × defensible same-unit product price, or a verified issuer-wide/provider value with understood coverage. Prefer reconciled issuer-wide values to reconstruction from incomplete chains.

Do not sum prices. Supply units can change through splits/rebasing; conversions must be dated. Do not multiply reference equity price by token supply without a verified token-to-underlying unit relationship.

Underlying tokenized value = sum of verified non-overlapping issuer-product values once per product. Whole-market total sums one chosen hierarchy level, never parent aggregates and constituents together.

## 5. Execution and volume

For onchain executions preserve network, transaction ID, event/log index or instruction path, pool/market ID, status, time, assets, amounts and USD conversion source. Multiple successful instructions in one transaction may be distinct executions.

For centralized markets use venue, market ID and native trade ID where available. Aggregate-only endpoints retain their provider scope/methodology and cannot independently prove overlap with another aggregate.

A multi-hop route can contain multiple real pool executions. Pool-level volume may count each leg, while product traded value needs one declared attribution method. Do not collapse every leg in a transaction or treat route-leg notional as investor capital flow.

For a chosen 24-hour UTC window:
- Include successful eligible executions once.
- Sum defensible USD notionals.
- Choose one consistent valuation side.
- Reconcile stablecoin depegs and retain confidence/coverage.
- Exclude mint/redeem, bridge movement, transfers, failed swaps and liquidity deposits/withdrawals unless a separate metric explicitly measures them.

If execution-level records are unavailable, a provider-reported volume may be shown with explicit provider scope. Do not claim reconstructed unique volume is validated merely because an aggregate field was returned.

## 6. Liquidity and market aggregates

- Do not sum identical pool reserves from multiple providers.
- Sum unique physical-pool liquidity only after confirming compatible available reserves and comparable timestamps.
- Pool liquidity is not automatically executable depth.
- Do not add perpetual open interest to tokenized circulating value.
- Do not add spot and perpetual volume under one unqualified tokenized-volume metric.
- Count underlyings, products, deployments, venues and pools separately.
- Versions counts issuer products/eligible versions, not network deployments.

## 7. Provider global totals

Maintain dated categories: ordinary crypto, tokenized RWA product, bridge/wrapper representation and unresolved.

For every product excluded from a provider global total, retain evidence that it is included, excluded or unknown. Missing market rank is not proof of exclusion.

Adjusted crypto cap = provider global USD cap − sum of tokenized circulating caps proven included, once each, at compatible times. Unknown membership prevents a complete adjusted claim.

A sum of covered eligible Crypto rows is a covered-universe total, not automatically equal to provider global. Never add provider Crypto and tokenized global totals before overlap is reconciled.

## 8. Network view and navigation

All Networks: one row per issuer product, actual verified network names and covered metrics.

Selected network: only products with verified deployments on that network; hide redundant Networks column. Network-specific volume/liquidity use deployment scope. Issuer-wide supply/value remain labelled issuer-wide. Partial venue/network coverage remains partial.

Preserve selected network context to the exact issuer product. Broad underlying navigation may discover several products without merging them. Builder perpetual navigation remains exact.

## 9. Correlation

Market-wide Crypto vs Tokenized RWA: percentage changes in comparable market-value series, not raw dollar levels. Individual asset comparisons: percentage changes in prices. A coin vs market benchmark uses coin price returns against benchmark market-value returns and must be labelled accordingly.

Use matching timestamps and the approved 30D aggregate window where displayed. Cadence, minimum paired observations and gap thresholds require documented technical settings and tests. No invented history, zero fill or unmatched dates. Reconstitution/classification changes cannot silently become economic returns. Missing, zero-base or constant series return unavailable.

## 10. Pagination, freshness and evidence

- Validate terminal page/cursor, duplicate IDs, cursor continuity and source-time compatibility.
- First page is never a complete universe.
- A failed page makes the snapshot partial.
- Preserve metric-specific refresh plans; polling more often than provider updates does not create freshness.
- Record provider freshness, quota, history entitlement and licensing separately.
- Keep raw fixtures, normalized observations, identity/version history and calculation version.
- Tag values as source-reported, reconstructed, partial, stale or unavailable.

## 11. Acceptance fixtures

- Bridge: origin 100, locked 40, destination 40 → unique supply 100.
- Issuers: NVDAx value 60 + NVDAon value 40 → NVIDIA tokenized value 100 only if non-overlapping.
- Three networks for one product → one All Networks row, three names, no triple count.
- One DEX execution reported by three sources → one; two true execution instructions → two.
- Same pool across providers → liquidity once; same address on different chains → separate pool identities.
- RWA infrastructure coin remains Crypto; tokenized stock is RWA; ambiguous classification unresolved.
- Provider total 1,000; proven-included RWA 100; excluded RWA 50 → adjusted Crypto 900, not 850.
- Pagination 250/250/227/0 deduplicated → complete for that endpoint snapshot only, not full issuer universe.
- Identical nonconstant aligned return series → correlation +1; raw dollar levels are not inputs.

These are developer fixtures, not production PASS results.
