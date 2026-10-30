# Validation Matrix — RWAs Intelligence

**Purpose:** prevent approval, source availability, formula correctness, coverage and production readiness from being conflated.  
**Status:** transcribed from retained supplied evidence; no new provider-wide certification or production test run is claimed here.

## 1. Status dimensions

Each metric/adapter must be tracked independently across:

1. Product approval (approved, proposed, deferred, removed).
2. Provider/source identified.
3. Exact endpoint and native field validated.
4. Unit and identity mapping validated.
5. Formula validated against real source fields.
6. Historical series validated.
7. Full eligible coverage validated.
8. Access entitlement and licence/export rights validated.
9. Production implementation and monitoring validated.

Suggested readiness labels:
- VALIDATED — only for the exact retained scope/fixture stated.
- PARTIALLY VALIDATED — useful evidence exists but material scope/semantics remain open.
- BLOCKED — access or required inputs currently prevent validation in retained evidence.
- NOT VALIDATED — not tested or insufficient evidence.
- RESERVED — requires joint specification before implementation.
- DEFERRED/REMOVED — not current MVP implementation scope.

Never promote a sample or one successful call into whole-product readiness.

## 2. Provider readiness snapshot

| Source | Retained status | Required next validation |
|---|---|---|
| CoinGecko global/coins/RWA | Sample fields and requests tested; full adjusted Crypto/RWA universe not verified | Current entitlement, pagination, global inclusion, coverage, licence, cache and history |
| GeckoTerminal | Exact token/pool subsets validated | Complete deployment/venue coverage, pool overlap, reserve units and execution dedup |
| Ondo official | Authenticated payload not obtained | Authorized x-api-key access, complete catalogue and market field validation |
| Binance/bStocks | Access/environment blocked | Authorized supported environment, exact pairs and tokenized catalogue mapping |
| xStocks official | First page 100 with hasNext; later request forbidden | Recover permitted endpoint/access, full pagination and product/deployment mapping |
| Backpack | Exact NVDA perp mark validated; other data partial | Catalogue vs RFQ/listed scope, complete coverage, history, units and product relation |
| Robinhood | Issuer catalogue snapshot validated; 194 vs 192 provider match | Resolve missing CRWD/BND, unrelated stoxfi, token volume and network coverage |
| Hyperliquid | Exact xyz fields and 720 common-hour pilot retained | All builder scopes, funding units, history and account ledger boundaries |
| Kraken | Samples and 719 hourly quotes retained | Full current contract coverage, funding conversion, fees, units and book timestamps |
| Lighter RH/Core | RH NVDA ID15 direct USD OI validated | Separate domains, funding units/history, exact coverage and current metadata |
| Solana RPC | MU supply conversion and eight PreStocks mint accounts tested | Historical multipliers, bridge backing and full mint coverage |
| PreStocks | Eight product/mint snapshot and valuation fields validated | Terms, historical consistency, complete pool/execution coverage and index history |
| Paimon | Core Asset sample validated | Complete pagination, API stability/terms, rights and deferred workflow boundaries |
| Morpho | USDG loan / NVDA collateral subset normalized | Full market pair registry, current coverage and exact field semantics |
| Kamino | Reserve subsets tested | Complete collateral/pair mappings and unit semantics |
| Jupiter | Authorized access absent; execution quote scope blocked | Credential/access approval, route quote units/fees and permitted use |
| Macro publishers | Candidate BLS/BEA/Federal Reserve only | Select actual feeds, validate release calendar, timestamps, revision policy and licence |
| Ondo/Enclave perps | Reproducible base URL absent | Recover exact route/entitlement and retest |

## 3. Known metric and product blockers

### Home
- Crypto-only adjusted global cap/volume not validated.
- Complete Crypto eligible pagination not proven.
- Complete tokenized RWA market pagination/aggregation not proven.
- Tokenized value economic-supply consolidation partial.
- Volume overlap/dedup incomplete.
- Aggregate market-value history unavailable; market-wide correlation must remain unavailable.
- Illustrative prototype +2.1% is not measured.

### Crypto / Tokenized RWA
- Full universe and classification mapping incomplete.
- Provider global inclusion membership unresolved.
- Some history fields requested/tested but not a complete history guarantee.
- Tokenized product/deployment counts differ and must not be conflated.
- Cross-venue liquidity and volume aggregation partial.

### Issuers
- Ondo authenticated catalogue access absent in retained evidence.
- bStocks/Binance access blocked in retained environment.
- xStocks pagination incomplete.
- Backpack RFQ/listed distinction and supply discrepancy remain.
- Robinhood issuer/provider mismatch and token-volume source distinction remain.
- PreStocks index membership/history/multiplier coverage partial.
- Paimon deal/settlement flows deferred.

### Derivatives and Funding
- Exact contract identity must be venue/domain/builder scoped.
- Some open-interest formulas validated only for specific IDs.
- Native funding intervals/signs differ by venue.
- Funding cost requires execution assumptions and four legs.
- Current rates do not prove historical funding series or net profitability.

### DeFi
- Exact reserve/pair coverage is partial.
- Loan asset vs collateral must remain explicit.
- Available market liquidity is not personal borrow allowance.
- Pool reserves are not issuer backing or executable depth.
- LP earnings cannot be inferred from current fee × historical volume.

### Trader Intelligence / Event Feed
- Accounting and scoring remain reserved.
- Event source integration/detector/ranking/alerts remain reserved.
- Macro publisher integrations are not validated.

## 4. Required QA fixtures

### Identity
- Same ticker across issuers.
- One underlying with multiple issuer products.
- One issuer product across multiple networks.
- Contract migration and case-sensitive mint.
- Spot product and similarly named perp.
- HIP-3 builder/domain collision.

### Supply/value
- Bridge origin 100, locked 40, wrapped destination 40 → unique supply 100.
- Independent issuance only counted with proof.
- Product units and multipliers change effective date.
- Never add underlying parent and product constituents twice.

### Volume/execution
- One execution repeated by provider/router counted once.
- Two real event/instruction legs in one transaction remain distinct.
- Failed swap, transfer, bridge and liquidity add/remove excluded.
- One trade's two token sides do not double notional.
- Stablecoin depeg valuation handled.

### Market metrics
- Direct USD OI is not multiplied again.
- Base OI uses verified contract size × mark.
- Empty/crossed/stale order book unavailable.
- Null differs from zero.
- Spread is not slippage.
- Spot and perp volume remain separate.

### History/statistics
- Missing/zero prior returns unavailable.
- Unfinished interval excluded.
- Misaligned timestamps excluded, not forward-filled.
- Identical nonconstant returns correlate +1; inverse returns −1.
- Constant or insufficient pairs unavailable.
- Universe membership change does not become market return.

### Pagination/operations
- Duplicate IDs across pages removed.
- Terminal page verified.
- Interrupted page yields partial status.
- Retry is idempotent.
- Rate limit/auth/provider outage classified separately.
- Last successful observation remains stale, not live.

## 5. Release gate

No metric enters production as a complete market claim until identity, exact source, units, formula, coverage, access/licence and required history are proven. For partial metrics, product owner must approve the partial display semantics. A release can ship with unavailable metrics if the UI explains the limitation; it cannot ship by fabricating values.

## 6. Evidence recording template

For every test, record: test ID, date/time UTC, code commit, provider/route, fixture or sanitized response ID, instrument IDs, expected result, actual result, status, coverage, error, reviewer and follow-up issue.
