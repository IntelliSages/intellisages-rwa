# RWAs Intelligence — System Architecture

**Status:** proposed target architecture. This document does not claim the stack or services are already present in the repository. Phase 0 must audit the actual codebase before selecting or replacing technologies.

## 1. Architecture goals

- Preserve economic and instrument identity across issuers, chains, providers and venues.
- Separate source acquisition from normalization, domain calculations and presentation.
- Make every derived value reproducible from raw observations, effective-dated mappings and method versions.
- Support partial coverage without producing misleading aggregates.
- Serve responsive read models without synchronous fan-out to every provider.
- Keep MVP read-only; no trading execution or custody subsystem.

## 2. Logical components

1. **Web application:** screen navigation, search, filters, charts, tables, detail views and CSV initiation. It renders backend state; it does not calculate market aggregates.
2. **API/read layer:** typed endpoints for overview, screeners, asset details, markets, history, funding comparisons, DeFi, traders and events.
3. **Domain registry:** canonical entities, aliases, classification, deployments, issuer relationships, venue/market identity and effective dates.
4. **Provider adapters:** isolated clients for CoinGecko, GeckoTerminal, issuer APIs, exchange/perp APIs, chain RPC and macro publishers.
5. **Ingestion orchestration:** scheduled jobs, cursor checkpoints, rate budgets, retries, idempotency and job-state tracking.
6. **Raw evidence store:** request metadata and permitted raw payloads with secrets removed.
7. **Normalized observation store:** typed, timestamped source observations with units and scope.
8. **Calculation/materialization layer:** versioned transformations, deduplication, aggregates, rankings and history series.
9. **Coverage/validation service:** source status, page completion, eligible universe, mapping completeness and metric readiness.
10. **Operations/observability:** logs, metrics, traces, freshness alerts, dead-letter/quarantine and runbooks.

## 3. Conceptual data model

### Core identity tables/entities
- Underlying: economic reference (company, commodity, fund, private asset, etc.).
- Issuer: legal/operating entity issuing a product.
- IssuerProduct: distinct tokenized product, legal/economic terms, unit mapping and underlying relation.
- Network: canonical chain namespace and display metadata.
- Deployment: product + network + contract/mint + effective interval + representation type.
- EconomicSupplyGroup: proven economic equivalence across bridged/wrapped representations.
- Venue: exchange/protocol/provider venue identity.
- Market: exact spot pair, perp contract or other market; native market ID and domain.
- Pool: network + pool address + protocol + base/quote/reserve semantics.
- ProviderAlias: provider + namespace + external ID + canonical entity + evidence + effective dates.

### Observation and governance entities
- RawSourceRecord: provider, request key, response reference, source/retrieval time, status, adapter version.
- MarketObservation: entity, metric, raw value, normalized value, unit, window, scope, observed time.
- HistoryObservation: exact entity/metric/time/unit and finalized status.
- Execution: venue/network, trade/event key, market/pool, legs, status, time and USD valuation evidence.
- CoverageSnapshot: eligible set/count, covered set/count, exclusions, unknowns, page/cursor termination and source time.
- MetricDefinition: purpose, formula, unit, scope, window, method version and required inputs.
- MetricResult: nullable value, status, reason, coverage, provenance and calculation version.
- ValidationEvidence: test/source/formula/coverage/history/licensing result and evidence reference.
- IngestionJob: schedule, checkpoint, last success/error, provider budget and adapter version.
- NavigationContext: originating page, tab, filters, network, builder and canonical entity.

Use database constraints and foreign keys to enforce canonical relations. External IDs are not primary domain IDs. Use effective-dated records rather than overwriting history when symbols, addresses, units or classifications change.

## 4. Data flow

1. Scheduler triggers provider-specific collection according to a metric plan.
2. Adapter validates access, builds request, respects rate budget and records request metadata.
3. Raw response is persisted with secrets redacted.
4. Adapter parses provider-native fields; malformed records are quarantined.
5. Normalizer converts decimals, units, timestamps and provider namespaces without losing native values.
6. Identity resolver maps observations to canonical entities; unresolved records remain unresolved.
7. Coverage evaluator checks pagination termination, expected membership and mapping status.
8. Deduplication and domain rules create compatible input sets.
9. Versioned calculations materialize metric results/history.
10. Read API serves results with status, reason, scope, coverage and provenance.
11. UI displays the value only in the exact scope supported.

## 5. Storage and consistency

Recommended conceptual separation:
- Relational store for identity, configuration, normalized observations, metric results, jobs and coverage.
- Object/blob store for larger raw responses and reproducible fixtures.
- Cache for hot read models and rate-limited provider results.

Choose concrete database, queue, cache and object-store technology after repository audit, traffic assumptions, hosting budget and operational capability review. Do not introduce Kafka/streaming infrastructure merely because the domain is data-heavy; MVP can use scheduled, checkpointed ingestion if volume and latency allow.

Use UTC internally. Preserve provider-native timestamp and interval. Use decimal/numeric types for quantities, prices, rates and notional values; avoid binary float for financial normalization. Store raw native value/unit alongside normalized value/unit.

## 6. Provider adapter contract

Every adapter exposes:
- provider identity and adapter version;
- exact request method/route/parameters (secrets excluded);
- required entitlement/auth configuration;
- instrument/domain/network namespace;
- source observation time and retrieval time;
- native field map and unit semantics;
- pagination cursor and terminal condition;
- retryability/error classification;
- raw evidence reference;
- declared coverage and completeness.

Provider-specific schemas must not leak into the frontend. Do not hide semantic differences behind a generic field called price/volume/funding without unit and scope.

## 7. Metric calculation contract

A calculation consumes explicit canonical entities, normalized observations, a window, coverage snapshot, method version and configuration. It returns:
- nullable raw numeric value;
- unit and display precision;
- status and reason;
- entity/scope/window;
- source observation range;
- calculation time/version;
- sample count and coverage metadata.

No calculation should convert absent inputs into zero. A partial aggregate may be shown only when product-approved and labelled partial; otherwise unavailable.

## 8. API/read architecture

Read APIs should serve materialized views rather than call every provider at page render time. Search and filter operations should be deterministic and use canonical IDs. Detail endpoints should return the selected entity and scoped related markets, not infer relationships by symbol.

Proposed schemas are in docs/API_CONTRACTS.md. Route names are illustrative and require implementation agreement.

## 9. Security and permissions

- Provider API keys are server-side secrets.
- Separate public market data from user-specific Trader Intelligence data.
- Apply authorization at account/wallet scope; never expose another user's positions/fills.
- Use least-privilege service credentials, secret rotation and audit logs.
- Redact tokens, keys, signed requests and personal data from logs/fixtures.
- Confirm provider terms allow storage, derived data, redistribution and CSV export.

## 10. Observability

Track per provider/adapter:
- request count, latency, error rate and rate-limit responses;
- last successful source observation and retrieval;
- page/cursor completion and records ingested;
- unresolved identity mappings;
- stale/partial/unavailable metric counts;
- calculation failures and version changes;
- job lag, retries and quarantine size.

User-facing freshness must be derived from the source observation and approved metric policy, not from page render time.

## 11. Architecture decisions still open

- Actual frontend/backend framework and hosting from repository audit.
- Relational database and migration tool.
- Queue/scheduler choice and job concurrency.
- Raw payload retention and object storage.
- Authentication/authorization model for account-linked features.
- Search implementation and index refresh.
- Cache invalidation and materialization strategy.
- Provider licensing, data retention and export permissions.
