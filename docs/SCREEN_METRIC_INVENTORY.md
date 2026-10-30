# Screen and Metric Inventory — Source Register Index

**Source:** supplied Shared Metric Dictionary, which reports 218 rendered table/card fields across fifteen pages, plus Correlation and headline families. This index preserves the source labels grouped by page. It is not a new approval of each metric: consult DATA_DICTIONARY.md and the original metric decision/evidence register for formulas and readiness. Labels marked removed/deferred below must not reappear as active MVP features.

## Home
- Crypto: Asset, Price, Market Cap, 24H Volume, 24H
- Tokenized: Underlying, Value, 24H Volume, 24H

## Crypto Screener
- Asset, Price, Market Cap, FDV, 24H Volume, Volume / MCap, 24H, 7D, 30D, RWA Correlation

## Tokenized RWA Screener
- Underlying, Asset Class, Tokenized Price, Tokenized Value, 24H Volume, Liquidity, 24H, 7D, 30D, Versions, Perp Availability

## HIP-3
- Market, Builder, Underlying, Price, 24H Volume, Volume Change, Open Interest, OI Change, Volume/OI, OI Cap, OI Utilisation, Funding Rate, Spread, Active Traders, Qualified Trader Flow

Qualified Trader Flow remains unavailable/unapproved as a calculation in the retained evidence; do not invent trader qualification or flow.

## Ondo
- Stocks: Asset, Underlying, Tokenized Value, Supply, Holder Addresses, 7D Holder Growth, 24H Trading Volume, Secondary Liquidity, Networks
- Perps: Market, Underlying, Price, 24H Volume, Volume Change, Open Interest, OI Change, Volume/OI, Funding Rate, Basis, Spread

Holder Addresses and 7D Holder Growth are deferred/blocked. Perps Basis is user-approved removed. Do not restore them.

## bStocks
- Spot: Asset, Type, Underlying, Price, Tokenized Value, 24H Volume, Volume Change, Off-Hours Volume %, Spot Spread, Networks
- Perps: Market, Underlying, Price, 24H Volume, Volume Change, Open Interest, OI Change, Volume/OI, Funding Rate, Basis, Spread

Perps Basis is user-approved removed. Exact Binance/bStocks access and instrument mapping remain blocked in retained evidence.

## xStocks
- Spot: Asset, Underlying, Type, Price, Tokenized Value, Supply, 24H Volume, Liquidity, Networks, Best Venue Gap
- Perps: Market, Underlying, Price, 24H Volume, Open Interest, OI Change, Volume/OI, Funding Rate, Basis, Spread

Best Venue Gap is deferred; Perps Basis is removed. Do not restore either as active columns or an arbitrage preview.

## Backpack
- Spot: Asset, Underlying, Price, Tokenized Value, Onchain Supply, 24H Volume, Liquidity, Off-Hours Volume %, Off-Hours Move, Conversion Status, Networks
- Perps: Market, Underlying, Price, 24H Volume, Open Interest, Volume/OI, Funding Rate, Spread

Off-Hours Move is deferred. Keep RFQ securities distinct from listed tokenized pairs and order books.

## Robinhood Tokenized Assets
- Spot: Asset, Underlying, Type, Price, Tokenized Value, Supply, 24H DEX Volume, Turnover, Net Directional Flow, Liquidity, Off-Hours Volume %, Networks
- Perps: Market, Underlying, Price, 24H Volume, Open Interest, OI Change, Volume/OI, Funding Rate, Basis, Spread

Perps Basis is removed. Net Directional Flow remains blocked until source access and buy/sell/netting semantics are validated. Issuer dailyTradingVolume is not token DEX turnover.

## PreStocks
- Asset, Token Price, Issuer Implied Valuation, Relative Strength, 24H Volume

Pre-IPO Index, Market Breadth, Rotation Leader and 30D Index Change are documented headline families. The equal-weight daily-rebalanced basket proposal remains unvalidated for complete constituents/history.

## Paimon
- Asset, Price, 24H DEX Volume, Pool Liquidity

No headline metric cards are approved. Launchpad Deals and Events/Settlements remain unavailable/deferred.

## Funding Rates
- Rates: Underlying, Venue, Market, Funding Rate, Funding Interval, Normalized Funding, 24H Avg, 7D Avg, Persistence, OI, 24H Volume
- Pairs: Underlying, Long Venue, Short Venue, Funding Spread, Basis Difference, OI long/short, Volume long/short, Trading Costs, Time to Recover Costs, Estimated Funding Income

Funding Pair Basis Difference remains a distinct retained feature (N0008) and is not the removed issuer Perps Basis/Spot–Perp Carry feature. Cost/recovery fields remain unavailable unless assumptions, quotes, fee tier and execution legs are known.

## DeFi
- LP: Asset, Platform, Protocol, Pair, TVL, 24H Volume, Volume/TVL, 24H Fees, Reported Base APY, Pool Type, 24H Swaps
- Lending: Asset, Loan Asset, Platform, Protocol, Supply APY, Borrow APY, Supplied, Borrowed, Utilisation, Available to Borrow, Collateral Enabled

No DeFi headline cards are approved. APY belongs to loan/reserve asset, not collateral by default. Available to Borrow is market liquidity, not personal borrowing allowance.

## Trader Intelligence
- Trader, Venue, RWA PnL, Total PnL, Trades, Win Rate, Profit Factor, Max Drawdown, Exposure, Last Active, Status

Approved product purpose includes PnL, win rate, trading activity, volume and exposure. Detailed accounting, ledger completeness, numeric formulas, scoring/qualification and cohort status remain reserved for joint specification. A wallet/account is not automatically a human or institution.

## Event Feed
- Asset/company label, Event title/kind, Venue/platform context, Summary/statement, Event date, Source/category badge, Illustrative-event label, Macro developments

No numeric event headline metrics are approved. Event detection, ranking, urgency/impact scoring, causal claims and alerts remain reserved.

## Headline families recorded in source dictionary
- Home: Crypto Market Value, Crypto Market Performance, Crypto 24H Volume, Crypto Tracked Assets, Tokenized RWA Market Value, Tokenized Market Performance, Tokenized 24H Volume, Tokenized Tracked Assets, Crypto ↔ RWA Correlation.
- Crypto: Market Cap, BTC Dominance, Assets Tracked, RWA Correlation Median.
- Correlation: market-wide and individual-asset comparison method.
- HIP-3, Ondo, bStocks, xStocks, Backpack, Robinhood, PreStocks, Paimon, Funding, DeFi, Traders and Events: consult DATA_DICTIONARY.md for page-specific approved headline families and no-headline decisions.

## Inventory reconciliation notes

1. The source dictionary describes 218 rendered table/card fields across fifteen pages, plus Correlation and headline families. Its exported text also includes legacy/deferred/removed fields for QA reconciliation.
2. The list above preserves the named inventory, including legacy fields, and marks known removals/deferred states where explicitly recorded.
3. Do not infer implementation readiness from presence in this inventory.
4. Before coding any field, reconcile its exact feature ID and original decision-register entry. Similar labels do not authorize shared formula, source, unit or scope.
