# Frontend Specification — RWAs Intelligence

**Source:** product vision, Home Screener Specification, supplied Final MVP Review HTML and shared metric dictionary.  
**Status:** requirements reference; visual polish and exact component geometry remain subject to implementation audit.

## 1. Frontend responsibilities

The frontend is a read and exploration surface. It renders canonical entity identity, backend-calculated metrics, source coverage and availability. It must not invent instrument relationships, calculate market-wide aggregates, substitute missing values or construct historical series.

## 2. Top-level page inventory

The approved product brief identifies sixteen main surfaces:

| Page | Primary interaction/content |
|---|---|
| Home | Headline cards, Trending Crypto, Trending Tokenized, sorting and CSV |
| Crypto Screener | Search/filter/sort eligible crypto assets |
| Tokenized RWA Screener | Underlying catalogue and distinct issuer-product discovery |
| Correlation | Aligned returns and correlation when history is available |
| HIP-3 | Builder-scoped perp discovery and exact contract detail |
| Ondo | Issuer-specific products, networks, markets |
| bStocks | Issuer/product and venue discovery |
| xStocks | Products, deployments, networks and activity |
| Backpack | Securities catalogue; RFQ/listed distinction |
| Robinhood Tokenized Assets | Issuer catalogue, token products and covered market observations |
| PreStocks | Pre-IPO token products and approved basket/index research |
| Paimon | Separate issued products and approved unavailable states |
| Funding Rates | Supported perp funding observations and comparisons |
| DeFi | Pools and lending markets |
| Trader Intelligence | PnL, win rate, trading activity, volume and exposure; accounting reserved |
| Event Feed | Market, onchain, trading, company/catalyst and macro observations |

The supplied HTML review package contains 20 page objects. Cross-Token Arbitrage and standalone Pre-IPO Markets are legacy/removed pages and are not approved top-level MVP scope. hip3-detail and asset-detail are detail templates/routes, not additional navigation pages.

## 3. Legacy tabs and scope conflicts in HTML

The current-baseline HTML still contains:
- Spot–Perp Carry tabs on Ondo, bStocks, xStocks, Backpack and Robinhood;
- Paimon Launchpad Deals and Events/Settlements;
- Cross-Token Arbitrage standalone page;
- standalone Pre-IPO Markets page;
- old basis/reference-gap/holder/off-hours fields.

These are not authorized by presence in baseline. Respect settled removals/deferments in the source metric/decision register. Do not restore Spot–Perp Carry, standalone Pre-IPO, arbitrage or removed columns. Paimon Deals and Events/Settlements remain unavailable/deferred rather than fabricated.

Funding Rates has its own Rates and Cross-Venue Spreads comparison context. Funding Pair Basis Difference is a retained distinct metric and must not be confused with removed issuer Basis/Carry.

## 4. Global interaction model

- Global navigation exposes approved MVP pages.
- Search resolves canonical entities and verified aliases; ambiguous tickers show distinct results.
- Filters operate on eligible records and preserve state when opening/backing from detail.
- All Networks displays one row per issuer product and verified networks.
- A selected network displays only issuer products with a verified deployment on that network.
- Issuer-wide values remain labelled issuer-wide when viewed from a network-specific page.
- Broad underlying pages discover issuer products; issuer product pages preserve issuer-specific context.
- Perpetual markets retain venue/domain/builder/native market identity.
- Metric tooltips explain meaning, unit, scope, source freshness and limitations.
- CSV exports current eligible results with raw values and identity/provenance metadata.
- Empty, loading, error, unavailable, partial and stale states are distinct.

## 5. Broad underlying and product detail

Broad underlying pages identify the economic reference, show distinct issuer products, expand products to reveal verified deployments and actual venues, separate spot products from perpetuals, and use canonical IDs for links/route state.

Issuer product pages preserve issuer, product ID, unit, backing/rights disclosure where evidenced, deployments and markets. Issuer-specific supply/value stays separate from underlying aggregate. Show actual supported networks, not issuer-wide marketing support. Preserve selected network when navigating from a filtered screener.

## 6. Spot and perpetual presentation

- Broad underlying Spot discovery uses a compact asset-symbol overview with expandable venues.
- Broad Perpetual discovery initially shows at most five entries, with View all and Collapse.
- First-five selection occurs after eligible filtering and verified-volume ordering.
- Perpetual detail and Markets preserve venue/domain/builder/native contract identity.
- HIP-3 markets open in exact builder context.
- Spot price, mark price, oracle price, index price, bid/ask and last trade are distinct fields; label them.

## 7. Metric and data states

- **Available/current:** show value, unit and observation time.
- **Stale:** show source observation time and stale state, or hide per metric policy.
- **Partial:** show only if metric permits; label subset and coverage.
- **Unavailable:** null plus reason; no zero substitute.
- **Not applicable:** metric does not apply to this instrument.
- **Loading:** explicit pending state.
- **Error:** classified cause; preserve retry/error context.
- **Illustrative:** prototype/example only; never production.

A zero is displayed as zero, not a dash. A dash without an accessible explanation is insufficient.

## 8. Charts and time controls

A chart control is interactive only when a corresponding backend series exists. Show window, interval, unit, source and history coverage. Do not draw through missing intervals as if continuous. Do not convert a current value into a historical curve. Correlation uses aligned returns, not raw indexed price/market-value lines as inputs. Distinguish unfinished current interval from finalized observations.

**Important Home discrepancy:** HTML baseline shows +0.61 Crypto ↔ RWA correlation with 24H window. Approved Home specification says market-wide history unavailable and specifies returns-based 30D. The numeric HTML figure is illustrative and must not ship as live.

## 9. Sorting, filtering and export

Sorting uses raw numeric values and compatible units; nulls last; stable canonical ID as tie-break; disable all-null sorts. Sorting visible rows does not redefine top-ten eligibility.

CSV includes readable headings, canonical IDs, raw numbers, unit, window, source/observed time, status, coverage and calculation version where relevant. Do not export internal approval controls or credentials. Prototype export is not proof of production schema.

## 10. Accessibility and responsive behaviour

- Keyboard-accessible navigation, filters, drawers, modals and controls.
- Visible focus state and semantic table headers.
- Tooltips available on focus, not hover only.
- Responsive tables preserve instrument identity and units.
- Charts have text summaries or accessible data alternatives.
- Loading/error/unavailable states are announced appropriately.

## 11. Frontend acceptance tests

- Open underlying → product → deployment/venue → back → reopen; confirm exact identity.
- Select network and verify product count and deployment membership.
- Test All Networks deduplication.
- Test builder-specific perp navigation.
- Test five-entry/View all/Collapse after filters.
- Sort 100 above 9; null last.
- Test zero, null, partial, stale and error states separately.
- Verify CSV matches eligible rows and includes metadata.
- Confirm missing history does not render a fabricated chart.
- Verify removed pages/tabs/columns are absent from approved MVP navigation.
