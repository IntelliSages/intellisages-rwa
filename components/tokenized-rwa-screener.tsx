"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  ArrowDown, ArrowUp, ArrowUpDown, ChevronDown, ChevronRight, Database,
  Filter, RefreshCw, Search, ShieldCheck, SlidersHorizontal,
} from "lucide-react";
import { AvailabilityPill, DataProvenance, MetricUnavailable } from "@/components/data-components";
import type { TokenizedProductCatalogueResponse, TokenizedProductCatalogueItem } from "@/lib/catalogue-types";
import styles from "./tokenized-rwa-screener.module.css";

const PAGE_SIZE = 25;
type ApiError = { code: string; message: string; unavailable: boolean };

function getError(payload: unknown, status: number): ApiError {
  const body = payload && typeof payload === "object" ? payload as Record<string, unknown> : {};
  const code = typeof body.code === "string" ? body.code : status === 503 ? "SERVICE_UNAVAILABLE" : "REQUEST_FAILED";
  const message = typeof body.detail === "string" ? body.detail : "The catalogue request failed. Retry or check the API service.";
  return { code, message, unavailable: status === 503 || status === 502 };
}

function DeploymentList({ product }: { product: TokenizedProductCatalogueItem }) {
  const verified = product.deployments.filter(deployment => deployment.is_verified);
  const pending = product.deployments.filter(deployment => !deployment.is_verified);
  return <div className={styles.deploymentDetail}>
    <div className={styles.detailIntro}><b>Canonical product record</b><span>{product.canonical_key}</span></div>
    <div className={styles.detailGrid}>
      <div><small>Issuer</small><b>{product.issuer.legal_name}</b><span>{product.issuer.id}</span></div>
      <div><small>Underlying</small><b>{product.underlying.display_name}</b><span>{product.underlying.asset_type} · {product.underlying.id}</span></div>
      <div><small>Native product ID</small><b>{product.native_product_id}</b><span>{product.instrument_form} · {product.unit_description}</span></div>
      <div><small>Representation</small><b>{product.representation_type.replaceAll("_", " ")}</b><span>Not a legal or backing verification</span></div>
    </div>
    <div className={styles.deploymentSection}>
      <div className={styles.deploymentTitle}><b>Verified product deployments</b><span>{verified.length} verified</span></div>
      {verified.length ? verified.map(deployment=><div className={styles.deploymentRow} key={deployment.id}>
        <span className={styles.networkMark}>{deployment.network.display_name.slice(0,1)}</span>
        <span><b>{deployment.network.display_name}</b><small>{deployment.network.namespace} · {deployment.network.family}</small></span>
        <code title={deployment.native_identifier}>{deployment.native_identifier}</code>
        <AvailabilityPill status="available" reason="Product-specific deployment is marked verified in the identity registry."/>
      </div>) : <p className={styles.detailMuted}>No product deployment is currently marked verified.</p>}
      {pending.length > 0 && <p className={styles.pendingDeployments}>{pending.length} additional deployment record(s) are unverified and excluded from network filters.</p>}
    </div>
    <DataProvenance
      source={product.classification.source}
      evidenceRef={product.classification.evidence_ref}
      effectiveFrom={product.classification.effective_from}
      effectiveTo={product.classification.effective_to}
      providerGlobalIncluded={product.classification.provider_global_included}
    />
  </div>;
}

export function TokenizedRwaScreener() {
  const [search, setSearch] = useState("");
  const [issuerId, setIssuerId] = useState("all");
  const [networkId, setNetworkId] = useState("all");
  const [sort, setSort] = useState("underlying");
  const [direction, setDirection] = useState("asc");
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [offset, setOffset] = useState(0);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [data, setData] = useState<TokenizedProductCatalogueResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    const params = new URLSearchParams({
      limit: String(PAGE_SIZE),
      offset: String(offset),
      sort,
      direction,
    });
    if (search.trim()) params.set("q", search.trim());
    if (issuerId !== "all") params.set("issuer_id", issuerId);
    if (networkId !== "all") params.set("network_id", networkId);

    setLoading(true);
    setError(null);
    setData(null);
    fetch(`/api/catalogue/tokenized-products?${params.toString()}`, {
      signal: controller.signal,
      headers: { accept: "application/json" },
    })
      .then(async response => {
        const payload: unknown = await response.json().catch(() => null);
        if (!response.ok) throw getError(payload, response.status);
        return payload as TokenizedProductCatalogueResponse;
      })
      .then(payload => {
        if (!payload || typeof payload !== "object" || !Array.isArray((payload as TokenizedProductCatalogueResponse).items)
          || typeof (payload as TokenizedProductCatalogueResponse).total !== "number"
          || !(payload as TokenizedProductCatalogueResponse).facets) {
          throw { code: "INVALID_CATALOGUE_RESPONSE", message: "The catalogue API returned an unexpected response shape.", unavailable: false };
        }
        setData(payload);
        setExpandedId(null);
      })
      .catch(reason => {
        if (controller.signal.aborted) return;
        setError(typeof reason === "object" && reason !== null && "code" in reason
          ? reason as ApiError
          : { code: "REQUEST_FAILED", message: "The catalogue could not be loaded. Check the connection and retry.", unavailable: true });
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [search, issuerId, networkId, sort, direction, offset, retry]);

  const activeFilters = useMemo(
    () => Number(issuerId !== "all") + Number(networkId !== "all"),
    [issuerId, networkId],
  );

  function resetFilters() {
    setSearch("");
    setIssuerId("all");
    setNetworkId("all");
    setSort("underlying");
    setDirection("asc");
    setOffset(0);
    setExpandedId(null);
  }

  function updateFilter(update: () => void) {
    update();
    setOffset(0);
  }

  return <div className={styles.page}>
    <div className={styles.breadcrumb}><Link href="/">Market Overview</Link><span>/</span><b>Tokenized RWA Screener</b></div>
    <section className={styles.header}>
      <div><p className={styles.eyebrow}>TOKENIZED ASSET DISCOVERY</p><h1>Tokenized RWA Screener</h1><p className={styles.subtitle}>Discover the underlying asset, distinguish issuer products and inspect verified product-level network deployments.</p></div>
      <span className={styles.readiness}><i/> Registry-backed · market data pending</span>
    </section>

    <section className={styles.coverageNotice}>
      <span className={styles.noticeIcon}><ShieldCheck size={18}/></span>
      <div><b>Identity and market-data coverage are separate</b><p>The catalogue returns currently classified registry records. It does not represent a provider-complete market universe. Price, value, volume, liquidity and performance remain unavailable until validated observations are connected.</p></div>
      <AvailabilityPill status="partial" reason="Registry coverage is known only for registered identities; provider universe completeness is unknown."/>
    </section>

    <section className={styles.metrics}>
      <article><span>Registered RWA products</span><strong>{data ? data.total.toLocaleString() : "—"}</strong><small>{data ? "Matching registry records" : "Awaiting catalogue response"}</small></article>
      <article><span>Products on this page</span><strong>{data ? data.items.length.toLocaleString() : "—"}</strong><small>Current result page · max {PAGE_SIZE}</small></article>
      <article><span>Verified network facets</span><strong>{data ? data.facets.networks.length.toLocaleString() : "—"}</strong><small>Networks with verified product deployments</small></article>
      <article><span>Market observations</span><strong className={styles.pendingValue}>Not connected</strong><small>Not inferred from identity records</small></article>
    </section>

    <section className={styles.workspace}>
      <div className={styles.toolbar}>
        <div className={styles.search}><Search size={16}/><input aria-label="Search tokenized products" placeholder="Search underlying, issuer, product or symbol…" value={search} onChange={event=>{setSearch(event.target.value);setOffset(0);}}/>{search&&<button type="button" aria-label="Clear search" onClick={()=>{setSearch("");setOffset(0);}}>×</button>}</div>
        <button type="button" className={styles.filterButton} onClick={()=>setFiltersOpen(value=>!value)} aria-expanded={filtersOpen}><SlidersHorizontal size={14}/> Filters {activeFilters>0&&<span>{activeFilters}</span>}<ChevronDown size={13}/></button>
        <label className={styles.sort}>Sort by<select aria-label="Sort tokenized products" value={sort} onChange={event=>{setSort(event.target.value);setOffset(0);}}><option value="underlying">Underlying</option><option value="issuer">Issuer</option><option value="product">Product</option></select></label>
        <button type="button" className={styles.direction} onClick={()=>{setDirection(value=>value==="asc"?"desc":"asc");setOffset(0);}} aria-label={`Sort direction ${direction}`}>{direction==="asc"?<ArrowUp size={14}/>:<ArrowDown size={14}/>}<span>{direction==="asc"?"A to Z":"Z to A"}</span></button>
      </div>

      {filtersOpen&&<div className={styles.filters}>
        <label>Issuer<select value={issuerId} onChange={event=>updateFilter(()=>setIssuerId(event.target.value))}><option value="all">All issuers</option>{(data?.facets.issuers??[]).map(issuer=><option value={issuer.id} key={issuer.id}>{issuer.label}</option>)}</select></label>
        <label>Network<select value={networkId} onChange={event=>updateFilter(()=>setNetworkId(event.target.value))}><option value="all">All verified networks</option>{(data?.facets.networks??[]).map(network=><option value={network.id} key={network.id}>{network.label}</option>)}</select></label>
        <button type="button" onClick={resetFilters}>Reset filters</button>
        <span><Filter size={13}/> Network filters use verified product deployments, not issuer-wide network support.</span>
      </div>}

      <div className={styles.tableMeta}><div><b>Issuer product catalogue</b><span>One row per distinct issuer product · All Networks does not multiply products</span></div><span>{loading?"Loading…":data? `${data.total.toLocaleString()} registry matches`:"Catalogue unavailable"}</span></div>

      {error ? <div className={styles.statePanel} role="alert">
        <span className={styles.stateIcon}><Database size={22}/></span>
        <b>{error.code==="API_NOT_CONFIGURED"?"Frontend is running; API connection is not configured":error.unavailable?"Catalogue service unavailable":"Catalogue request failed"}</b>
        <p>{error.message}</p>
        <span className={styles.errorCode}>{error.code}</span>
        <button type="button" onClick={()=>setRetry(value=>value+1)}><RefreshCw size={14}/> Retry</button>
      </div> : loading && !data ? <div className={styles.statePanel} aria-live="polite"><span className={styles.spinner}/><b>Loading registered issuer products</b><p>Retrieving canonical identities and product-level deployment mappings.</p></div> : data?.items.length ? <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead><tr><th className={styles.identityHead}>Underlying / issuer product</th><th>Asset class</th><th>Verified networks</th><th>Tokenized price</th><th>Tokenized value</th><th>24H volume</th><th>Liquidity</th><th>24H</th><th>7D</th><th>30D</th><th>Versions</th><th>Perp availability</th></tr></thead>
          <tbody>{data.items.map(product=><FragmentRow
            key={product.id}
            product={product}
            expanded={expandedId===product.id}
            onToggle={()=>setExpandedId(current=>current===product.id?null:product.id)}
          />)}</tbody>
        </table>
      </div> : <div className={styles.statePanel}>
        <span className={styles.stateIcon}><Database size={22}/></span>
        <b>{search||activeFilters?"No registered products match these filters":"No RWA-classified products are registered yet"}</b>
        <p>{search||activeFilters?"No records in the current registry match this search and filter combination. This does not establish that no such products exist in the market.":"The API is reachable, but there are currently no issuer products with an effective RWA classification in the registry. This is not a zero-market claim."}</p>
        {(search||activeFilters>0)&&<button type="button" onClick={resetFilters}>Clear search and filters</button>}
      </div>}

      <div className={styles.tableFooter}>
        <span>Registry results only · Provider coverage unknown</span>
        <div><button type="button" disabled={!data||offset===0||loading} onClick={()=>setOffset(value=>Math.max(0,value-PAGE_SIZE))}>Previous</button><span>{data? `${data.total===0?0:offset+1}–${Math.min(offset+(data.items.length),data.total)} of ${data.total}`:"—"}</span><button type="button" disabled={!data||!data.has_more||loading} onClick={()=>setOffset(value=>value+PAGE_SIZE)}>Next</button></div>
      </div>
    </section>

    <section className={styles.integrityNote}><div><ShieldCheck size={15}/><span><b>Identity rules</b> · Issuer products remain distinct even when they reference the same underlying. A product appears once across all verified network deployments.</span></div><span>As of {data?.as_of??"—"}</span></section>
    {data&&<p className={styles.coverageFootnote}>{data.coverage.note}</p>}
  </div>;
}

function FragmentRow({product,expanded,onToggle}:{product:TokenizedProductCatalogueItem;expanded:boolean;onToggle:()=>void}) {
  const verified = product.deployments.filter(deployment=>deployment.is_verified);
  return <>
    <tr className={styles.productRow}>
      <td className={styles.identityCell}><button type="button" className={styles.expand} aria-expanded={expanded} aria-label={`${expanded?"Collapse":"Expand"} ${product.display_name} details`} onClick={onToggle}>{expanded?<ChevronDown size={15}/>:<ChevronRight size={15}/>}</button><span><b>{product.underlying.display_name}</b><small>{product.display_name}{product.symbol? ` · ${product.symbol}`:""} · {product.issuer.legal_name}</small><code>{product.id}</code></span></td>
      <td><span className={styles.assetClass}>RWA</span></td>
      <td><div className={styles.networkChips}>{verified.length?verified.map(deployment=><span key={deployment.id}>{deployment.network.display_name}</span>):<small>No verified deployment</small>}</div>{product.unverified_deployment_count>0&&<small className={styles.pendingCount}>{product.unverified_deployment_count} pending</small>}</td>
      <td><MetricUnavailable label="Tokenized price" reason="No validated tokenized price observation is connected to this product." /></td>
      <td><MetricUnavailable label="Tokenized value" reason="Supply, unit conversion and non-overlapping economic-supply methodology are not yet connected." /></td>
      <td><MetricUnavailable label="24 hour volume" reason="No validated venue-scoped trading volume observation is connected." /></td>
      <td><MetricUnavailable label="Liquidity" reason="No comparable pool or venue liquidity observation is connected." /></td>
      <td><MetricUnavailable label="24 hour change" reason="No completed, timestamp-aligned price history is connected." /></td>
      <td><MetricUnavailable label="7 day change" reason="No completed, timestamp-aligned price history is connected." /></td>
      <td><MetricUnavailable label="30 day change" reason="No completed, timestamp-aligned price history is connected." /></td>
      <td><MetricUnavailable label="Versions" reason="This is a product count, not a deployment count; complete version reconciliation is pending." /></td>
      <td><AvailabilityPill status="unavailable" reason="Perpetual market catalogue and exact product-market mappings are not connected." /></td>
    </tr>
    {expanded&&<tr className={styles.expandedRow}><td colSpan={12}><DeploymentList product={product}/></td></tr>}
  </>;
}
