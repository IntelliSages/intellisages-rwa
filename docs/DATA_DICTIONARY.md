# Shared Metric Dictionary — RWAs Intelligence

**Purpose:** central reference for metric meaning, units, formulas, required inputs and unavailable-value handling.  
**Source:** supplied Shared Metric Dictionary (218 rendered table/card fields across fifteen pages plus Correlation and headline families) and Home Screener Specification.  
**Important:** this concise engineering index does not override exact page-level feature IDs and source rows in the original metric register. Keep each page's validation boundary. Removed/deferred fields are not authorized by appearing in old references.

## 1. Metric contract

Every metric definition must include:

| Attribute | Required meaning |
|---|---|
| metric_id | Stable metric identifier; not display label |
| entity_type / entity_id | Exact canonical instrument or entity |
| scope | Underlying, issuer product, deployment, venue, contract, pool, account or aggregate |
| purpose | User question the metric answers |
| definition | Plain-language meaning |
| value / unit | Numeric value and canonical unit |
| window / interval | e.g. rolling 24h, UTC day, completed 1h, 30D |
| source | Provider, endpoint, native field and source namespace |
| calculation | Formula, denominator, valuation convention and method version |
| source_observed_at | Provider's observation timestamp |
| retrieved_at / calculated_at | System retrieval and calculation timestamps |
| availability | available, partial, stale, unavailable, not_applicable or error |
| reason | Machine-readable and user-readable reason |
| coverage | Eligible/observed count, venue/network scope, exclusions and missingness |
| provenance | Source record/fixture IDs and adapter/calculation versions |

Null means unavailable, not zero. Zero is a valid measured value. Percentages are stored as numeric percent or fraction according to a declared unit; never mix them.

## 2. Shared formulas and conventions

- Percentage change = 100 × (current / prior − 1); missing or zero prior → unavailable.
- Volume / Market Cap = 100 × volume / market cap; compatible USD scope and market cap > 0.
- Volume / Open Interest and Volume / TVL require compatible USD scope/window and nonzero denominator.
- Conventional one-sided USD OI = direct USD value once, OR verified base quantity × contract unit × mark price. Never multiply direct USD by mark again.
- Bid/ask spread % = 100 × (ask − bid) / mid, with same-time valid bid/ask and positive mid. This is not trade-size slippage.
- Funding hourly fraction = confirmed signed funding fraction / interval hours. Percent = 100 × fraction. Preserve native fraction/percent and interval.
- Pair long A / short B funding convention = fB − fA for the declared orientation. Do not reverse orientation to show a more attractive result.
- Funding income is funding-only gross scenario, not net profit.
- Correlation = Pearson correlation of aligned returns, not raw price/value levels.
- Supply quantity = raw units / 10^decimals, then apply effective share multiplier only where verified.
- APY applies to the loan/reserve asset, not collateral by default. Multiply by 100 only when native source unit is fractional.
- Liquidity, volume, TVL, market value, OI, exposure and PnL are distinct concepts.

## 3. Home metrics

| Metric | Meaning / method | Required guardrail |
|---|---|---|
| Crypto Market Value | Circulating value of eligible Crypto excluding tokenized RWA products; adjusted provider global cap only when inclusion evidence exists | Do not subtract whole RWA aggregate or infer inclusion from rank |
| Crypto Market Performance | 24h change in comparable adjusted Crypto market value | Do not pair adjusted current total with unadjusted provider change |
| Crypto 24H Volume | Provider-reported global USD volume unless tokenized exclusions and volume definitions reconcile | Keep provider-global scope explicit; no unrelated RWA subtraction |
| Crypto Tracked Assets | Distinct covered eligible provider IDs after verified exclusions | Not provider global active-crypto count; complete pagination required |
| Tokenized RWA Market Value | Covered tokenized products, aggregated once at underlying/product level | Not underlying company market cap; no duplicate issuer products/bridges |
| Tokenized Market Performance | Change in comparable covered tokenized total | Snapshot membership and coverage must match |
| Tokenized 24H Volume | Covered secondary spot activity | Avoid pool/provider overlap and exclude perps unless explicitly scoped |
| Tokenized Tracked Assets | Distinct eligible underlyings in screener | Not issuer product or deployment count |
| Crypto ↔ RWA Correlation | Pearson of aligned hourly percentage changes in aggregate market-value series; 30D display | Missing/constant/insufficient series unavailable |

Home tables:
- Crypto: Asset (id/symbol/name), Price (current_price), Market Cap (market_cap), 24H Volume (total_volume), 24H percentage price change.
- Tokenized: Underlying (RWA market ID/symbol/name), Value (tokenized_market_data.market_cap), 24H Volume, 24H tokenized price change.
- Trending lists rank the complete eligible universe by 24H volume, then display top ten. Stable ID is a deterministic tie-break. Sorting displayed rows does not redefine eligibility.

## 4. Crypto Screener metric families

Retained fields include exact asset identity, price, circulating market cap, FDV, 24H volume, Volume/MCap, 24H/7D/30D price returns and RWA correlation. Use provider canonical coin ID, not ticker joins. FDV is not market cap. Volume/MCap is turnover ratio, not liquidity or profit. Missing 7D/30D source fields stay unavailable; do not synthesize from an unvalidated history series.

Crypto eligibility is internal. Stablecoins remain eligible in the screener but are excluded from Trending Crypto per Home specification. RWA infrastructure coins remain eligible unless the instrument itself is a tokenized RWA.

## 5. Tokenized RWA screener and underlying metrics

Retained metric families:
- Underlying identity/name/symbol and asset class.
- Tokenized reference price.
- Tokenized value for covered issuer products.
- 24H covered secondary spot volume.
- Pool liquidity.
- 24H/7D/30D price changes.
- Versions (distinct issuer products, not deployments).
- Perpetual availability (verified venues/contracts).

Use provider RWA fields where their semantics are tested. A mean across issuer products is not approved. Tokenized value is not equity market cap. Liquidity is not volume/backing/order-book depth. New products may lack 7D/30D history. Perp availability is a relationship count with exact contract identity, not proof of trading access.

## 6. HIP-3 and issuer/perpetual metric families

HIP-3 retained fields include exact Market, Builder, Underlying, contract Price/mark, 24H perpetual volume, Volume Change, Open Interest, OI Change, OI utilization/cap context where verified, Funding Rate, funding changes/history and quote/book-related fields where retained. Keep native builder key and contract name; xyz, km and mkts namespaces are distinct. Native mark is not executable bid/ask or oracle. A rolling-day volume is not spot token turnover.

Issuer-specific perps on Ondo, bStocks, xStocks, Backpack and Robinhood require exact issuer/product-to-contract mapping. Similar tickers are not enough. Maintain separate spot product and derivative records. OI must be direct USD once or verified base × contract size × mark. Missing history makes changes unavailable. Empty/crossed/stale books are unavailable; removed standalone order-book UI is not restored.

## 7. Issuer page metric families and retained caveats

### Ondo
Retained concepts include tokenized value, tracked products, 24H spot volume, product price/unit/supply, network/deployment coverage, related perps and market context. Authenticated official catalogue payload was not obtained in retained evidence. Issuer product/rights and deployment mappings require validation. Do not infer listing from a similar perp ticker.

### bStocks
Retained concepts include product catalogue, tokenized value/volume, market price, network/product context and related markets. Binance tokenized-assets access was blocked in retained environment. Verify exact instrument and issuer relationship; do not confuse bStocks with Backed/xStocks.

### xStocks
Retained concepts include tokenized value, eligible issuer products, 24H volume and active networks. First 100 catalogue entries had hasNextPage=true; full catalogue was not verified. Temporary halt/session closure is not delisting. Network count derives from verified deployments, not hard-coded mock values.

### Backpack
Retained concepts include tokenized value, eligible listed securities, 24H volume and 24/7 asset availability. Distinguish RFQ security catalogue from listed order-book markets. Do not treat RFQ counts as listed pairs. Session/holiday schedules must be verified per instrument. Supply discrepancy and complete cross-venue coverage remain unresolved.

### Robinhood Tokenized Assets
Retained concepts include tokenized value, tracked issuer products, 24H tokenized volume, network/pool activity and directional flow. Issuer dailyTradingVolume is underlying equity trading, not token DEX turnover. Retained catalogue reconciliation was 194 issuer entries vs 192 provider matches; CRWD/BND and unrelated stoxfi entry require resolution. Directional flow is blocked until authenticated coverage and buy/sell/netting semantics are verified.

### PreStocks
Retained concepts include Pre-IPO Index, 24H Trading Volume, Market Breadth, Rotation Leader and 30D Index Change. Index proposal in retained dictionary: daily-rebalanced equal-weight basket, hourly eligible price returns, base level 100. This is not a validated production index. Complete basket/history/multiplier coverage is not proven. Market breadth must report valid denominator; missing constituents are not flat. Rotation compares same-scope 24H volume share against the mean share across seven completed UTC daily snapshots; no leader if baseline absent or all changes nonpositive.

### Paimon
No headline metric cards in approved core view. Do not add market cap, FDV, implied company valuation or all-time activity. Four products remain separate. Launchpad Deals and Events/Settlements remain unavailable/deferred. Do not infer private-company share value from token price without legal/unit denominator evidence.

## 8. Funding Rates metrics

Retained fields include compared underlyings, venue pairs, funding rates, normalized hourly rates, pair funding differential, funding history and scenario income/cost/recovery fields where approved. Keep fixed longA/shortB orientation and exact market identity. Normalize native payment interval. Historical averages use completed intervals only. Funding-only gross income is not net profit. Cost needs entry and exit execution assumptions for both legs, account fee tier, quotes, impact and scenario inputs; otherwise cost/recovery unavailable. Spot–Perp Carry and issuer Perps Basis are not restored. Funding Pair Basis Difference remains a separate retained feature as recorded in source decision register.

## 9. DeFi metrics

No headline cards are approved. Retained table families include protocol/pool/market identity, TVL or pool reserves, volume, fees, fee/TVL and volume/TVL ratios, supply APY, borrow APY, loan asset, collateral asset, supplied/borrowed amounts, available liquidity, collateral-enabled status and reserve metrics.

Guardrails:
- TVL is exact pool/market reserves, not issuer backing.
- Supply/Borrow APY applies to loan/reserve asset.
- Available liquidity is not user-specific borrowing allowance.
- Collateral enabled requires actual protocol/pair/risk configuration.
- Base APY excludes incentives unless explicitly included.
- Current fee rate × historical volume is not validated LP earnings.
- Concentrated LP returns depend on range participation and historical liquidity.

## 10. Trader Intelligence metrics

Approved purpose: PnL, win rate, trading activity, volume and exposure. No numeric headline cards, smart-money score, qualification or ranking are approved by the supplied metric dictionary. A trader row is a verified wallet/account in declared venue coverage, not necessarily a person/institution.

Before implementation jointly define realized/unrealized PnL, fees/funding, deposits/withdrawals, account boundaries, trade grouping, time window, volume, exposure and win rate. Fills alone are not a complete ledger. Exposure is outstanding position value, not capital or profit.

## 11. Event Feed fields

No numeric headline metrics. Approved event purposes include:
- Market developments: factual observed price/volume/liquidity/funding changes with comparable history.
- Onchain/trading developments: execution/activity/position observations with verified identity and coverage.
- Company announcements/catalysts: source-backed issuer/corporate/regulatory facts and relevant date.
- Macro developments: publisher-backed releases/indicators with period, release timestamp and actual value.

No validated universal event API, autonomous event detector, ranking, urgency/impact score, causal price claim, surprise logic or alerts are established. Retrieval time is not event time.

## 12. Metric availability vocabulary

| State | Meaning | UI treatment |
|---|---|---|
| available | Valid value in declared scope | Show value, unit and timestamp/coverage |
| partial | Valid subset, incomplete coverage | Show only if metric permits; label subset and coverage |
| stale | Last known observation outside freshness target | Show age/source time and stale label or hide per metric policy |
| unavailable | Required input/history/coverage missing | Null + reason; no zero substitute |
| not_applicable | Metric does not apply to entity | Explain not applicable |
| error | Provider/system failure with classified cause | Preserve error state; retry where allowed |
| illustrative | Prototype/example only | Never expose as production value |

## 13. Reconciliation rule

The source dictionary records 218 rendered table/card fields across fifteen pages plus Correlation and headline families. This index groups related metrics and preserves important formula/readiness boundaries. Before implementation, reconcile every actual feature ID and row from the source metric register against this document; similar labels do not authorize reuse of a different metric's units, scope or validation status.
