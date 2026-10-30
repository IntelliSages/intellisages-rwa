# Proposed Backend API Contracts

**Status:** logical internal contracts for engineering. These are not deployed routes, generated OpenAPI or tested schemas. Transport, route naming and framework remain subject to repository audit.

## 1. Contract principles

- Read services return canonical entities and precomputed metric results.
- Provider-native payloads do not leak directly into the UI.
- A value is nullable and accompanied by status, reason, scope, unit, window, timestamps and coverage.
- IDs are stable internal IDs; symbols are display/search aliases only.
- Sorting/filtering happens over the complete eligible set for the declared scope.
- No response claims full coverage if any required page or mapping is unresolved.
- Every response carries schema version and calculation version where derived metrics are returned.

## 2. Shared response envelope

Illustrative TypeScript-style shape:

    type Availability =
      | "available" | "partial" | "stale"
      | "unavailable" | "not_applicable" | "error";

    interface MetricValue<T = number> {
      metricId: string;
      entity: { type: string; id: string };
      value: T | null;
      unit: string;
      window?: { start: string; end: string; label: string };
      scope: {
        level: "market" | "underlying" | "issuer_product"
          | "deployment" | "venue" | "contract" | "pool" | "account";
        id?: string;
        description: string;
      };
      availability: Availability;
      reasonCode?: string;
      reason?: string;
      sourceObservedAt?: string;
      retrievedAt?: string;
      calculatedAt?: string;
      calculationVersion?: string;
      provenance: Array<{
        provider: string; sourceRecordId?: string;
        endpoint?: string; adapterVersion?: string;
      }>;
      coverage: {
        status: "complete" | "partial" | "unknown";
        eligibleCount?: number;
        observedCount?: number;
        excludedCount?: number;
        unresolvedCount?: number;
        networks?: string[];
        venues?: string[];
        notes?: string[];
      };
    }

A metric may have a numeric zero with availability=available. An absent value must be null with an explicit reason.

## 3. Logical read services

### Overview
GET /api/v1/overview

Returns Home headline MetricValue objects, cryptoTrending and tokenizedTrending arrays, plus catalogue coverage. Each row contains canonical ID, display identity, raw sortable values, availability and navigation target. The top-ten lists are derived after complete eligible universe collection.

### Screener
GET /api/v1/screeners/{screenId}

Query parameters may include search, assetClass, issuerId, networkId, venueId, instrumentType, sort, direction, cursor and limit.

Response:
- screener ID and applied filters;
- column definitions with metric IDs/units;
- rows with canonical identity and metric values;
- total eligible count vs returned count;
- coverage snapshot;
- next cursor and deterministic sort definition.

Network filtering is deployment-based. All Networks groups one row per issuer product.

### Entity detail
GET /api/v1/entities/{entityType}/{entityId}

Returns canonical entity metadata, relationships, disclosure references, metrics, history availability and related markets. Entity type is explicit. Do not resolve route by ticker.

### Related markets
GET /api/v1/entities/{entityType}/{entityId}/markets

Optional filters: instrumentType, networkId, venueId, builderId, marketStatus. Returns exact spot/perp market identities, venue/domain/builder, native market ID, product relation and metric coverage.

### History
GET /api/v1/history/{entityType}/{entityId}/{metricId}

Parameters: interval, start, end, timezone (UTC internally), optional calculationVersion.

Response includes ordered completed observations, unit, source coverage, missing intervals, finalized flags, method version and explicit unavailable reason when series is absent/insufficient. The API must not fabricate points.

### Correlation
GET /api/v1/correlation

Parameters: left entity/benchmark, right entity/benchmark, window, interval, method. Market-wide benchmark series are market-value returns; individual assets use price returns. Response includes coefficient or null, sample count, aligned timestamps, dropped/missing pairs, coverage and method version.

### Funding comparison
GET /api/v1/funding/comparisons

Inputs: exact market IDs, orientation, window and optional scenario parameters. Return native rate, normalized rate, payment interval, observed/finalized state and funding-only estimate separately from cost scenarios. If fee/quote/impact inputs are absent, cost and net recovery are null.

### DeFi
GET /api/v1/defi/markets

Filters: network, protocol, pool/market, loan asset, collateral asset. Response distinguishes pool reserves/TVL, supplied/borrowed loan asset, APY, available market liquidity and collateral eligibility.

### Trader Intelligence (reserved)
GET /api/v1/traders and account-specific endpoints are not implementation-ready until identity, authorization, accounting, data retention and PnL definitions are jointly approved.

### Event Feed (reserved)
GET /api/v1/events is a future logical read service. Event taxonomy, source policy, deduplication and scoring are not yet specified. Do not invent a detector or ranking contract.

### CSV export
POST /api/v1/exports or equivalent may create a scoped export job. Export must include canonical IDs, raw values, units, window, timestamps, coverage and calculation version. Check provider redistribution/export rights. Never include credentials or internal approval data.

## 4. Canonical instrument response

A market response should expose:
- marketId (internal stable ID);
- marketType (spot, perpetual, lending, pool);
- underlyingId and optional issuerProductId;
- issuerId where applicable;
- venueId and venue display name;
- networkId/deploymentId for onchain markets;
- builderId/perpDexId/domain for builder-specific perps;
- nativeMarketId and nativeSymbol;
- base/quote asset IDs and unit metadata;
- contract size, multiplier, settlement/collateral asset where relevant;
- source coverage and availability.

## 5. Error model

Use stable codes such as:
- AUTH_REQUIRED / ACCESS_DENIED
- RATE_LIMITED
- PROVIDER_UNAVAILABLE
- INCOMPLETE_PAGINATION
- IDENTITY_UNRESOLVED
- UNSUPPORTED_INSTRUMENT
- INVALID_UNIT
- OVERLAP_UNRESOLVED
- HISTORY_UNAVAILABLE
- INSUFFICIENT_HISTORY
- STALE_OBSERVATION
- CALCULATION_FAILED

Error responses must not reveal secrets. Retain last-success state separately; retryable provider failures do not erase historical observations or turn values into zero.

## 6. Contract test requirements

- Validate schemas and nullability.
- Verify canonical IDs and navigation targets.
- Verify unit/window/scope metadata.
- Verify zero vs null.
- Verify partial coverage and incomplete pagination.
- Verify deterministic sort and cursor behaviour.
- Verify exact builder/domain scoping.
- Verify no source credentials in payload/export.
- Verify unavailable history does not return synthetic points.

## 7. Implemented tokenized-product catalogue read route

**Implementation status:** available in the repository on the Tokenized RWA Screener increment; it is not a provider-ingestion or market-metric API.

`GET /api/v1/catalogue/tokenized-products`

Query: `q`, `issuer_id`, `network_id`, `sort=underlying|issuer|product`, `direction=asc|desc`, `limit=1..100`, `offset`, optional `as_of=YYYY-MM-DD`.

The response returns:
- distinct issuer-product records joined to their issuer and underlying;
- only currently effective `rwa` product classifications;
- classification source, evidence reference and effective period;
- all recorded product deployments, with an explicit verification flag;
- issuer and verified-network facets;
- pagination metadata and an explicit `coverage.status=unknown` disclosure.

The `total` field is the count of matching registry records, not a provider-complete market universe. A network filter matches only verified product-specific deployments. No price, value, volume, liquidity, supply, performance or perpetual-availability observations are returned. Those fields remain unavailable in the UI until a validated observation/read service is implemented.

The Next.js route `/api/catalogue/tokenized-products` proxies to the backend using server-only `RWA_API_BASE_URL`; it does not expose the upstream API base URL to browser JavaScript.
