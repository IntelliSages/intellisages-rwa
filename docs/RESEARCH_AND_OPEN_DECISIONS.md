# Research Findings and Open Product Decisions

**Research date:** 2026-10-30  
**Sources:** supplied product specifications and external primary/standards sources listed below.  
**Purpose:** translate market structure and technical research into product implications. This is product research, not legal, investment or regulatory advice.

## 1. Product positioning

RWAs Intelligence should be an **instrument-aware RWA market intelligence platform**, not a generic crypto screener with an RWA category or a tokenized-asset directory.

Its differentiator is the ability to connect the economic underlying, issuer and legal/economic product, onchain deployment and representation, actual spot venue/pool, related perpetual contract and builder, and the observations/histories/coverage/methodology behind each claim.

## 2. Market structure research and implications

### Tokenized securities are not homogeneous

The SEC staff's 28 January 2026 statement describes tokenized securities as securities represented in crypto-asset form where ownership records are maintained in whole or in part through crypto networks. It distinguishes issuer-sponsored tokenization from third-party unaffiliated tokenization and notes that structures and holder rights can vary. The statement is a staff view, not a Commission rule or legal force.

**Implication:** capture tokenization model, issuer relationship, legal instrument/claim type, custody/recordkeeping arrangement, holder-rights evidence, redemption mechanics and jurisdiction/disclosure references where available. Do not infer share ownership, voting, dividend or redemption rights from ticker, marketing description or a token/market listing.

### Technical token standards are not legal status

ERC-3643 specifies interfaces for permissioned token transfers, identity registries, trusted claim issuers and compliance rules. It is useful technical metadata, but does not by itself prove that an offering is legally compliant, properly registered or that token holders own the underlying security.

**Implication:** record a token standard as technical-standard metadata with contract/source evidence. Keep it separate from legal classification, issuer status, rights, regulatory approvals and investor eligibility. Avoid a single “compliant” badge based only on ERC-3643.

### Multi-network tokenization creates representation/interoperability risk

BIS Annual Economic Report 2026 discusses fragmentation across public and permissioned networks, non-seamless interoperability, ad hoc bridges and operational risks.

**Implication:** network count is not issuer-product count; deployment count is not independent supply. Store bridge origin, lock/mint or burn/mint relationship, backing evidence, conversion ratio and effective dates. Unknown bridge relation means no complete consolidated supply claim. Expose network-level breakdown and issuer-wide total separately.

### Perpetual markets need venue and builder identity

Hyperliquid HIP-3 documentation describes builder-deployed perp DEXs with deployer responsibilities for market/oracle definitions and operations. Builder-deployed DEXs have independent margining, order books and deployer settings. Native APIs expose builder/perp-DEX context.

**Implication:** a perp contract key must include protocol, perp DEX/builder, native market identifier and relevant domain. Similar symbols across xyz, km, mkts, RH Lighter and Core Lighter are not interchangeable. Preserve oracle, mark, index, last, bid/ask and funding as separate fields.

## 3. Provider fit

- **CoinGecko:** broad crypto/RWA discovery, provider-reported aggregates, tokenized market reference fields and history where available. Its public API overview describes coin/token, RWA, exchange/derivative, onchain and historical data families. This does not prove our entitlement, endpoint semantics, cache, history depth, completeness, redistribution rights or quota.
- **GeckoTerminal:** onchain token/pool discovery, reserves, rolling volume and OHLCV. A pool listing is not proof of issuer backing or legal rights.
- **Issuer-native catalogues:** product identifiers, deployment addresses, session status and metadata. Reconcile against other sources; do not assume complete legal or trading universes.
- **Native derivatives venues:** exact perp market metadata, mark/oracle/quote, OI, funding, book and history. Preserve native IDs and units.
- **Macro publishers:** BLS, BEA and Federal Reserve are candidates from supplied research. No complete macro feed/calendar integration was validated.

## 4. Product strategy conclusions

These are product-analysis conclusions, not claims about competitor feature sets.

1. **Identity resolution is the core moat.** A generic list of tokenized tickers is easy to reproduce; correct relationships among underlying, issuer, product, deployment, pool and derivative market are harder.
2. **Coverage transparency can differentiate.** Research and institutional users need to know what is missing, how much is covered and why a total is partial.
3. **Cross-market analytics require provenance.** A funding spread, correlation or activity change is useful only when instruments, windows, units and timestamps are comparable.
4. **Issuer pages should be product-first.** Do not collapse distinct products or infer rights from a company ticker.
5. **Evidence-first, not prediction-first.** Signals should follow validated histories, event definitions and model evaluation.
6. **Modular adapters are preferable.** Provider access and schemas change; provider-specific adapters should not dictate canonical entities or frontend contracts.
7. **Read-only MVP is a sensible boundary.** Trading, custody, investor eligibility and transaction execution introduce distinct risks and controls.

## 5. Additional data-model recommendations

When evidence exists, add:
- tokenization_model: issuer_sponsored, third_party, custodial_receipt, synthetic_or_derivative, unknown;
- claim_type: direct_security, security_entitlement, fund_unit, debt_claim, commodity_claim, contractual_claim, synthetic_exposure, unknown;
- issuer relationship and controlling/operating entity;
- custodian/trustee/administrator;
- holder rights: voting, dividends/distributions, redemption, transfer restrictions, corporate-action handling;
- legal/jurisdiction/disclosure references and last-reviewed date;
- eligibility/transfer restrictions and whether onchain, offchain or both.

These are evidence-backed metadata fields, not a legal conclusion engine. Unknown is first-class.

Market-quality metadata should include source/observation timestamp, venue/pool/contract, market status/session calendar, quote currency/conversion source, executable quote size/depth where available, volume methodology and coverage notes.

Corporate-action/unit history should include split/reverse split, dividend/distribution, redemption/maturity, rebasing/multiplier change, token/contract migration, effective timestamp and source evidence. These can change unit conversion and historical comparability and must not silently become market return.

## 6. Open product decisions

### Priority 0 — before core implementation
1. Confirm canonical product taxonomy and allowed instrument/claim types.
2. Confirm minimum product disclosure fields and who reviews issuer-rights claims.
3. Agree how to label issuer-sponsored vs third-party tokenization when evidence is incomplete.
4. Agree coverage language for market totals: complete provider total, adjusted provider total, covered-universe sum or partial sample.
5. Approve metric-level availability thresholds and which partial values may be shown.
6. Confirm CSV/export scope and provider redistribution permissions.

### Priority 1 — before relevant modules
7. Define Trader Intelligence account/wallet scope, PnL, fees, funding, cashflows, exposure and win rate.
8. Define Event Feed taxonomy, source hierarchy, event deduplication and entity relevance.
9. Define macro release coverage, revision policy, event time and consensus source if needed.
10. Approve PreStocks index constituents, rebalance, weights, missing-data and base-value methodology.
11. Confirm issuer-page disclosure/legal metadata and update cadence.
12. Define venue market-quality measures (spread, depth, slippage) and executable-size assumptions.

### Priority 2 — after MVP
13. Define cross-platform adoption and liquidity migration analytics.
14. Define capital-flow methodology that separates token transfers, exchange flows, mint/redeem and true investor capital.
15. Validate scoring, alerts or predictive research models with out-of-sample tests and documented limitations.

## 7. Research references

- SEC staff, [Statement on Tokenized Securities](https://www.sec.gov/newsroom/speeches-statements/corp-fin-statement-tokenized-securities-012826-statement-tokenized-securities), 28 Jan 2026. Distinguishes issuer-sponsored and third-party tokenized securities and explains variation in ownership-record models and rights. Staff statement, not a Commission rule.
- Ethereum standards, [ERC-3643: T-REX](https://eips.ethereum.org/EIPS/eip-3643). Technical interfaces for permissioned security tokens, identity registries and compliance.
- ERC3643 Association, [How ERC-3643 works](https://www.erc3643.org/the-standard). Technical standard is not regulatory approval.
- BIS, [Annual Economic Report 2026](https://www.bis.org/publ/arpdf/ar2026e.pdf). Interoperability fragmentation and bridge-related operational risks.
- BIS FSI, [Financial stability implications of tokenisation — Executive Summary](https://www.bis.org/publications/fsi-summary-financial-stability-implications-tokenisation-executive-summary), 28 Aug 2025.
- OECD, [Tokenisation of assets and DLT in financial markets](https://www.oecd.org/en/publications/tokenisation-of-assets-and-distributed-ledger-technologies-in-financial-markets_40e7f217-en.html), 9 Jan 2025.
- Hyperliquid, [HIP-3: Builder-deployed perpetuals](https://hyperliquid.gitbook.io/hyperliquid-docs/hyperliquid-improvement-proposals-hips/hip-3-builder-deployed-perpetuals).
- Hyperliquid, [Perpetuals API](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint/perpetuals).
- CoinGecko, [API product overview](https://www.coingecko.com/en/api).

## 8. Research limitations

This research does not provide jurisdiction-by-jurisdiction legal classification, issuer diligence, security valuation, source subscription verification or a complete competitor feature benchmark. Those require targeted research and, for legal/rights claims, qualified counsel and authoritative issuer documentation. The product should describe observed evidence and avoid implying legal conclusions.
