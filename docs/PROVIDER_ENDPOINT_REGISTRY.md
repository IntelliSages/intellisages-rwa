# Provider Endpoint Registry

**Purpose:** guide adapter implementation and identify what remains to be tested.  
**Status:** retained evidence from supplied research, not fresh universal API certification on 2026-10-30.

A documentation page or base URL is not proof of endpoint access. A field sample, formula validation, complete universe/history coverage, permitted access and production reliability are separate.

## 1. Provider inventory

| Provider | Routes/families retained in supplied evidence | Retained evidence and boundary |
|---|---|---|
| CoinGecko | GET /api/v3/global; /coins/markets; /rwas/markets; /rwas/{underlying}?tokens=true | Global and sample coin/RWA fields tested. Complete adjusted Crypto membership and whole RWA universe not verified. |
| GeckoTerminal | /api/v2/networks/{network}/tokens/{contract}/pools; /pools/{pool}; /ohlcv | Exact pool/token subsets validated; full deployment/venue registry not verified. Paginate and deduplicate. |
| Ondo official | GET /v1/assets/all/metadata; /market at api.gm.ondo.finance | Authenticated payload not obtained in retained test; x-api-key required. Do not fabricate success. |
| Binance / bStocks | GET /sapi/v1/equity/market/tokenized-assets; candidate native spot/futures routes | Access/environment blocked in retained evidence. Authorized supported environment and exact tokenized pair mapping required. |
| xStocks official | GET /api/v2/public/assets | First 100 returned hasNext; later v2 access failed. Full catalogue not verified. |
| Backpack | /api/v1/markets, /assets/securities, /markPrices, /depth, /fundingRates | Exact NVDA perp mark validated; full coverage and other inputs partial. RFQ catalogue differs from listed book universe. |
| Robinhood | GET /rhj/assets | Dated 194 issuer records vs 192 matched; mapping subset tested. CRWD/BND missing and unrelated stoxfi entry need reconciliation. dailyTradingVolume is not token turnover. |
| Hyperliquid | POST https://api.hyperliquid.xyz/info | Exact xyz fields and 720 common-hour pilot retained; full builder/history/account scope not proven. |
| Kraken | /derivatives/api/v3/instruments, tickers, historical-funding-rates, orderbook | Exact samples and history subset tested; complete economic/current coverage partial. |
| Lighter RH/Core | api.rh.lighter.xyz and mainnet.zklighter.elliot.ai | RH market ID 15 direct USD OI validated; RH/Core are separate domains. Current 8h vs historical hourly funding units need normalization. |
| Solana RPC | getTokenSupply/getAccountInfo | MU exact conversion and eight PreStocks mint accounts tested. Historical multiplier/bridge backing/full mint coverage not proven. |
| PreStocks | GET https://prestocks.com/api/prestocks | Eight current products/mints and issuer valuation estimates snapshot validated; stable history/terms need validation. |
| Paimon | /api/v1/c/launchpad/projects?skip=0&limit=100 | Catalogue sample/Core Asset snapshot validated; legacy workflows, rights and complete pagination not validated. |
| Morpho | POST https://api.morpho.org/graphql | USDG loan/NVDA collateral subset normalized and validated; full pair registry/current coverage not proven. |
| Kamino | /v2/kamino-market; /kamino-market/{pubkey}/reserves/metrics | Reserve subsets tested; every collateral pair not proven. |
| Jupiter | GET /swap/v1/quote | Candidate $10K route quote; authorized access absent and complete execution estimates blocked. |
| Macro publishers | Candidate BLS, BEA, Federal Reserve | Purpose approved; no confirmed working API/calendar integration in supplied evidence. |
| Ondo/Enclave perps | Exact live base URL not preserved | Prior field samples only; reproducible endpoint not verified. Recover original route/entitlement. |

## 2. CoinGecko and onchain route families

CoinGecko base: https://api.coingecko.com/api/v3/

- /global: provider global aggregate.
- /coins/markets?vs_currency=usd&per_page=250&page={page}: complete page crawl candidate; or ids={verified IDs} for exact instruments.
- /rwas/markets: tokenized underlying catalogue.
- /rwas/{underlying}?tokens=true: underlying/product associations.
- /coins/{id}/market_chart: history; do not assume RWA history has identical coverage.

Retained issuer categories include ondo-tokenized-assets, bstocks-ecosystem, backpack-securities-ecosystem and robinhood-chain-stocks-ecosystem. These assist discovery but are not legal/deployment catalogues. xStocks exact category/ID mapping must come from its specific source fixtures.

GeckoTerminal base: https://api.geckoterminal.com/api/v2/

- /networks/{network}/tokens/{contract}
- token /pools?page={page}
- /networks/{network}/pools/{pool}
- pool /ohlcv/hour or /ohlcv/day with exact saved aggregate, limit, currency and token side.

Provider chain namespaces (e.g. eth, solana, bsc, robinhood) are not necessarily the same as user-facing chain labels. Preserve both.

## 3. Native market and derivative routes

### Hyperliquid
POST https://api.hyperliquid.xyz/info. Retained request types include metaAndAssetCtxs, fundingHistory and l2Book; builder/dex parameters must match exact fixtures. User-specific recentTrades/userFillsByTime/userFunding/userNonFundingLedgerUpdates/clearinghouseState/portfolio samples do not establish a complete accounting ledger.

### Kraken
GET futures.kraken.com/derivatives/api/v3/instruments, tickers, historical-funding-rates?symbol={symbol}, orderbook?symbol={symbol}. Retained 719 hourly quotes with more=false cover one requested interval, not unlimited history.

### Backpack
Base https://api.backpack.exchange/api/v1/. Preserve markets/assets/securities, exact ticker/markPrices/depth/fundingRates/stockSessions/stockHolidays fixtures. Separate RFQ and listed markets; preserve native units and time/offset termination.

### Lighter
RH: https://api.rh.lighter.xyz/api/v1/ and wss://api.rh.lighter.xyz/stream?readonly=true.  
Core: https://mainnet.zklighter.elliot.ai/api/v1/.  
These are different domains. Native market IDs are domain-scoped. Retained RH market_stats/all stream returned direct USD OI for NVDA ID15; Core ID110 is not the same contract.

### Binance
GET https://api.binance.com/sapi/v1/equity/market/tokenized-assets requires X-MBX-APIKEY. Retained environment was blocked. Candidate ticker/bookTicker, klines and futures funding/depth routes require exact eligible instrument/access tests. Environment restrictions do not prove global data absence.

## 4. Pagination and completeness

Follow all eligible pages. Record expected universe, filtered eligible count, pages/cursors, terminal condition, exclusions, duplicate IDs and unresolved members. Supplied research recorded:
- Ondo first 250 then rate limit.
- xStocks first 100 with hasNextPage=true.
- Paimon additional pages.
- Kraken more=false only for a requested endpoint/window.

If a page fails, retain partial coverage. Do not use a first-page count as a complete catalogue. Preserve raw responses and idempotent retry checkpoints.

## 5. Retained refresh plans — targets, not SLAs

- Crypto global aggregate: 10 minutes.
- Tokenized RWA value materialization: 5 minutes.
- Eligible tokenized price/volume inputs: 60 seconds where documented.
- Leading 1,000 crypto quotes: 60 seconds; long-tail hourly.
- Registry/classification: daily.
- Issuer price/multiplier snapshots: hourly; eligibility/volume snapshots: daily where recovered.
- Current funding: 30–60 seconds where previously specified.
- Contract metadata: daily.
- Funding history: initial backfill then hourly incremental completed-history collection.
- Correlation: preserve five-minute market snapshots and aggregate to aligned hourly observations.

These are recovered engineering plans. Confirm provider cache, entitlement, actual freshness, quota and export rights before implementation promises. Do not replace provider-specific schedules with a generic polling interval.

## 6. Adapter evidence required before production

For every adapter retain provider, exact route/method/query/body, auth requirement, entity/domain/network key, native unit, source/retrieval time, pagination termination, errors, native field map, sample fixture, coverage and licence/export status.

No secret may appear in docs, browser payloads or CSV. Do not bypass provider restrictions. A single failure is not proof that the provider has no data; preserve error scope and retry only within permitted budgets.


## 7. CoinGecko RWA discovery adapter — pilot implementation

The current pilot adapter uses:
- \`GET https://api.coingecko.com/api/v3/rwas/list\` for the provider-tracked RWA underlying list.
- \`GET /rwas/{id}?tokens=true&tokenized_market_data=true\` for per-underlying token records, issuer details and platform contract/mint mappings.
- \`GET /rwas/issuers/list\` as an optional issuer-list cross-check.

The official CoinGecko RWA API guide states that a Demo API key is required and that the free Demo plan supports the list/detail discovery workflow. Ticker liquidity and historical market-chart endpoints are not used by this registry importer; those require paid access according to the guide. See https://www.coingecko.com/learn/tokenized-rwa-data-api-guide (updated 26 Oct 2026).

The adapter stores raw provider responses locally with SHA-256 hashes, per-record checkpointing, retry handling and retrieval timestamps. It stages only; it does not approve canonical records. Provider issuer labels are not legal-identity proof. Platform-to-CAIP-2 mappings are explicit and unknown platform slugs remain unresolved. Token contract/mint entries are staged as unverified deployments.

Coverage is reported against CoinGecko's tracked RWA list at retrieval time. It must not be described as complete global tokenized-asset coverage.
