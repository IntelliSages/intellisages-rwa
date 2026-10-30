# RWAs Intelligence — Product and Engineering Rules

**Status:** Binding project rules derived from the supplied product vision and supporting specifications, including the product-owner approved MVP Implementation Blueprint.  
**Audience:** product, frontend, backend, data engineering, research and QA.

These rules take precedence over mock values, convenience assumptions and unverified provider behaviour. A change requires explicit product-owner approval and a recorded decision.

## 1. MVP scope and delivery governance

1. The 16 pages listed in PRD.md and MVP_IMPLEMENTATION_BLUEPRINT.md remain in the MVP.
2. A page may launch with an explicitly unavailable/restricted metric; it must not silently disappear because a data source is incomplete.
3. MVP_IMPLEMENTATION_BLUEPRINT.md governs page-level launch qualifications, work-package sequence, inherited QA defects and release gates.
4. Do not expand into speculative intelligence before the data foundation is sound.
5. No execution, order placement, custody, wallet signing or guaranteed profitability is part of MVP.
6. Changes to approved scope, methodology, provider tiers or release gates require product-owner approval and a decision-log entry.
7. Documentation completeness, application readiness and data readiness are independent statuses.

## 2. Product truth and evidence

1. Every displayed metric has a user purpose, entity scope, unit, window, source, calculation, timestamp semantics and coverage description.
2. Distinguish source-reported, reconstructed, partial, stale, illustrative and unavailable values.
3. A successful sample response proves only that request, fields and sample scope at that time. It does not prove entitlement, complete pagination, universe coverage, history, licensing or production reliability.
4. Never use mock values as production defaults or fallbacks.
5. Never invent historical observations, interpolate absent history, forward-fill missing values for correlation, or silently substitute a different metric.
6. Missing values are null with a reason. Known zero is numeric zero. Stale is a freshness state, not a different numeric value.
7. Keep provider observation time separate from retrieval time and calculation time.
8. A partial crawl cannot publish a complete-universe total. Preserve page/cursor failures and covered/uncovered membership.
9. Approval, source identification, field validation, formula validation, history validation, full coverage and production readiness are independent statuses.
10. Test statuses are PASS (executed and passed), FAIL (executed and failed), BLOCKED (demonstrated dependency) and NOT TESTED (no execution evidence).

## 3. Canonical identity

1. Never identify an instrument by ticker or display name alone.
2. Keep separate canonical entities for underlying, issuer, issuer product, network, deployment, venue, market/contract, pool and execution.
3. Different issuer products referencing one underlying remain distinct (e.g. NVDAx and NVDAon).
4. A product deployed on multiple networks is one issuer product with multiple deployments, not multiple issuer products.
5. A bridge/wrapper representation is not additional economic supply unless independent issuance is proven.
6. Keep spot products and perpetual contracts separate, even when they reference the same underlying.
7. A HIP-3 contract is identified in its exact builder/perp-DEX context. Do not treat it as interchangeable with a spot token or another builder's similarly named contract.
8. Keep issuer legal/backing/rights claims separate from onchain market observations. A pool listing does not establish ownership, redemption or shareholder rights.
9. Provider IDs are aliases attached to canonical entities with provider, namespace, effective dates and evidence. Do not use ticker joins.
10. Verify deployment per product; issuer-wide network support is not enough.
11. Unknown asset/market IDs return not found, never a default row.

## 4. Classification

1. Maintain a versioned identity/classification registry with effective dates and evidence.
2. Tokenized real-world asset products belong in their appropriate RWA product universe.
3. Ordinary crypto infrastructure tokens associated with RWA projects remain in Crypto unless the instrument itself is a tokenized RWA product.
4. Do not classify by name substring, symbol, marketing category or provider category alone.
5. Keep unresolved classifications explicit; do not silently force them into either universe.
6. Provider global totals require separate inclusion evidence for every tokenized product potentially included in the provider total.

## 5. Aggregation and metric integrity

1. Apply approved Option B rules: unique economic supply across networks; different issuers remain distinct; each execution counted once; Crypto and tokenized RWA classifications mutually exclusive.
2. Never add the same bridged economic supply twice.
3. Never add a provider aggregate to constituents already included in that aggregate.
4. Never sum prices.
5. Never multiply reference equity price by token supply unless token-to-underlying unit relationship and effective multiplier are verified.
6. Do not sum market value, supply or liquidity across networks mechanically.
7. Do not combine spot and perpetual volume under an unqualified spot/tokenized volume metric.
8. Do not add perpetual open interest to circulating token value.
9. Do not double-count the same pool reported by multiple providers.
10. One transaction hash can contain multiple genuine execution legs. Deduplicate at the chain/venue execution key, not transaction hash alone.
11. Liquidity/reserves are not executable order-book depth, investor capital, issuer backing or borrowing allowance.
12. Use one declared valuation side for a trade's USD notional; do not count both token sides as two trades.

## 6. Historical and statistical integrity

1. Percentage change is 100 × (current / prior − 1) on comparable values; absent or zero prior values make the result unavailable.
2. Market-wide Crypto ↔ RWA correlation uses aligned percentage changes in comparable aggregate market-value series.
3. Individual asset correlation uses aligned percentage price changes.
4. Do not correlate raw dollar levels, mix price returns with market-value returns without naming the distinction, or substitute BTC versus one stock for a market-wide comparison.
5. Do not forward-fill missing pairs. Constant series, insufficient overlap, missing history or incompatible coverage return unavailable.
6. Reconstitution/classification changes must not silently appear as market returns.
7. Use completed intervals for historical bars/funding; do not treat unfinished intervals as finalized.
8. Store calculation/method version, paired sample count, alignment and missing-pair coverage.

## 7. API and UI contract rules

1. Backend responses include canonical IDs, scope, unit, observation time, availability, reason, coverage and calculation version where relevant.
2. Frontend components must not infer missing values, create totals, guess product identities or synthesize chart series.
3. Sort raw numeric values in compatible units; nulls last; stable canonical ID as deterministic tie-break.
4. Top-five/top-ten display limits are applied after complete eligibility and filtering, not to the first provider page.
5. Network selectors filter verified deployments. All Networks shows one row per issuer product and verified network names.
6. A selected network uses deployment-scoped trading observations where supported; issuer-wide supply/value remains explicitly issuer-wide.
7. Preserve navigation context (origin, filters, selected network, builder, tab and exact entity) through detail/back/reopen.
8. CSV exports include canonical IDs, raw numeric values, units, window, timestamps and coverage/status; never export secrets or internal approval controls.
9. Tooltips explain metric meaning and coverage in user language, not internal approval workflows.
10. Distinguish empty results, no eligible data, provider errors, blocked access and interrupted pagination.

## 8. Security, licensing and operations

1. Provider secrets stay in server-side secret management; never embed them in browser bundles, HTML, docs, CSV or client-visible errors.
2. Use only authorized API access and documented entitlements. A blocked environment does not prove a provider has no data; do not bypass restrictions.
3. Validate provider rate limits, cache behaviour, retention, redistribution and export rights before promising cadence or access.
4. Keep raw fixtures access-controlled and redact credentials/personal data.
5. Retry within an actual provider budget, use bounded backoff, checkpoint pagination and make ingestion idempotent.
6. Classify auth, rate-limit, provider outage, incomplete pagination, unsupported instrument, invalid unit, unresolved overlap and unavailable history separately.
7. Essential ingestion must run in a reliable worker/runtime, not depend on frontend traffic or short-lived web requests.
8. Verify backup/restore, monitoring, rollback and incident ownership before controlled launch.

## 9. Scope boundaries

- No execution service, trade placement, custody, wallet signing or portfolio execution is implied by the MVP.
- Do not restore removed Spot–Perp Carry/arbitrage subsystem, standalone Pre-IPO page, removed order-book/Sources controls or deferred columns.
- Pre-IPO information remains inside relevant platform pages.
- Paimon Launchpad Deals and Events/Settlements remain unavailable/deferred as specified.
- Trader Intelligence deeper PnL accounting, scoring, qualification and cohort logic require joint product-owner/developer specification.
- Event Feed detection, ranking, urgency/impact scoring and alerting require joint specification and validation.
- Macro integration is an approved purpose, not an already validated provider integration.

## 10. Change control

Every proposed change states: user problem, affected screens/entities/metrics, data evidence, formula, coverage impact, double-counting risk, migration/backfill implications, acceptance tests and owner approval. Record rejected/deferred decisions as well as accepted ones.
