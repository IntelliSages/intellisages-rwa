# Frontend Specification — RWAs Intelligence

**Source:** product vision, Home Screener Specification, supplied Final MVP Review HTML and shared metric dictionary.  
**Status:** requirements reference; visual polish and exact component geometry remain subject to implementation audit.

## 1. Frontend responsibilities

The frontend is a read and exploration surface. It renders canonical entity identity, backend-calculated metrics, source coverage and availability. It must not invent instrument relationships, calculate market-wide aggregates, substitute missing values or construct historical series.

## 2. Global interaction model

- Global navigation exposes the approved MVP pages.
- Search resolves canonical entities and verified aliases; ambiguous tickers show distinct results.
- Filters operate on eligible records and preserve filter state when opening/backing from detail.
- All Networks displays one row per issuer product and verified networks.
- A selected network displays only issuer products with a verified deployment on that network.
- Issuer-wide values remain labelled issuer-wide when viewed from a network-specific page.
- Broad underlying pages discover issuer products; issuer product pages preserve issuer-specific context.
- Perpetual markets retain venue/domain/builder/native market identity.
- Metric tooltips explain meaning, unit, scope, source freshness and limitations.
- CSV exports current eligible results with raw values and identity/provenance metadata.
- Empty, loading, error, unavailable, partial and stale states are distinct.

## 3. Page inventory and intent

| Page | Required interaction/content | Critical guardrail |
|---|---|---|
| Home | Headline cards, Trending Crypto, Trending Tokenized, sorting and CSV | Headline coverage is not inferred from ten visible rows |
| Crypto Screener | Search/filter/sort eligible crypto instruments and open exact asset | Exclude verified tokenized RWA products; retain ordinary RWA-infrastructure coins |
| Tokenized RWA Screener | Filter underlying catalogue; open broad underlying detail | Underlying row is not one issuer token |
| Correlation | Select instruments/window and view aligned returns/correlation when available | No synthetic series; unavailable if history insufficient |
| HIP-3 | Builder-scoped perp discovery and exact contract detail | Builder DEX and native contract are part of identity |
| Ondo | Issuer catalogue/product/network/market exploration | Authenticated catalogue access not validated in supplied evidence |
| bStocks | Issuer/product and venue discovery | Exact tokenized pair must be verified; Binance access was blocked in retained environment |
| xStocks | Product, deployments, networks, value/activity | First page had hasNext; full catalogue not validated |
| Backpack | Securities, RFQ vs listed instruments and supported trading context | RFQ universe is not the listed order-book universe |
| Robinhood Tokenized Assets | Issuer catalogue, token product and network/pool observations | Issuer equity dailyTradingVolume is not token DEX turnover |
| PreStocks | Pre-IPO token products, index/breadth/rotation fields where approved | Basket methodology and full history remain partial |
| Paimon | Separate issued tokens and approved unavailable states | No invented valuation, deals or settlement data |
| Funding Rates | Compare eligible perpetual funding rates/pairs | Native intervals/signs must normalize; no uncosted net-profit claim |
| DeFi | Pools, lending markets, TVL/reserves, APY and borrow liquidity | Loan asset, collateral and user borrowing allowance are distinct |
| Trader Intelligence | PnL, win rate, activity, volume and exposure | Accounting and permissions require joint specification |
| Event Feed | Market, onchain, trading, company/catalyst and macro events | No invented detector, urgency score, causal claim or alerts |

## 4. Broad underlying and product detail

Broad underlying pages:
- Identify the economic reference.
- Show distinct issuer products.
- Expand a product to reveal verified deployments and actual venues.
- Separate spot token products from related perpetual contracts.
- Use canonical IDs for links and route state.

Issuer product pages:
- Preserve issuer, product ID, unit, backing/rights disclosure where evidenced, deployments and markets.
- Keep issuer-specific supply/value separate from underlying aggregate.
- Show actual supported networks, not issuer-wide marketing support.
- Preserve selected network when navigating from a filtered screener.

## 5. Spot and perpetual presentation

- Broad underlying Spot discovery uses a compact asset-symbol overview with expandable venues.
- Broad Perpetual discovery initially shows at most five entries, with View all and Collapse.
- First-five selection occurs after eligible universe filtering and verified-volume ordering.
- Perpetual detail and Markets preserve venue/domain/builder/native contract identity.
- HIP-3 markets open in exact builder context.
- Spot price, mark price, oracle price, index price, bid/ask and last trade are different fields; label them.

## 6. Metric and data states

Every value should support these states:
- Available/current.
- Available but stale (show source observation time).
- Partial (show scope and coverage; use only where the metric permits partial display).
- Unavailable (null and reason).
- Not applicable (metric does not apply to this instrument).
- Loading.
- Error (classified cause; do not collapse to unavailable if retry/error context matters).
- Illustrative (prototype/research fixture only; never production).

Do not use a dash without an accessible explanation. A zero is displayed as zero, not a dash.

## 7. Charts and time controls

- A chart control is interactive only when a corresponding backend series exists.
- Show selected time window, interval, unit, source, and history coverage.
- Do not draw a line through missing intervals as if continuous.
- Do not convert a current value into a historical curve.
- Correlation uses aligned returns, not raw indexed price/market-value lines as the input.
- Historical charts must distinguish incomplete current interval from finalized observations.

## 8. Sorting, filtering and export

Sorting:
- Use raw numeric values and compatible units.
- Null values last.
- Stable canonical ID as deterministic tie-break.
- Disable all-null sorts.
- Sorting current rows does not redefine a top-ten eligibility rule.

CSV:
- Include readable column names, canonical IDs, raw numbers, unit, window, source/observed time, status, coverage and calculation version where relevant.
- Export eligible view semantics; do not export internal approval controls or credentials.
- Prototype export is not proof of production schema.

## 9. Accessibility and responsive behaviour

- Keyboard-accessible navigation, filters, drawers, modals and controls.
- Visible focus state and semantic table headers.
- Tooltips available on keyboard/focus, not hover only.
- Responsive tables should preserve instrument identity and units.
- Charts require text summaries or accessible data alternatives.
- Loading/error/unavailable states must be announced appropriately.

## 10. Frontend acceptance tests

- Open underlying → product → deployment/venue → back → reopen and confirm exact identity.
- Select network and verify product row count and deployment membership.
- Test All Networks deduplication.
- Test builder-specific perp navigation.
- Test first-five/View all/Collapse after filters.
- Sort values 100 and 9 correctly; null last.
- Test zero, null, partial, stale and error states separately.
- Verify CSV values and metadata match the displayed eligible result set.
- Confirm missing history does not render a fabricated chart.
