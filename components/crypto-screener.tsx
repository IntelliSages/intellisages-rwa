"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import {
  ArrowDownUp, ArrowRight, ChevronDown, CircleHelp, Download,
  Filter, RefreshCw, Search, ShieldCheck, SlidersHorizontal,
} from "lucide-react";
import styles from "./crypto-screener.module.css";

type SortDirection = "desc" | "asc";

const columns = [
  { label: "Asset", hint: "Canonical asset identity" },
  { label: "Price", hint: "Latest eligible spot price" },
  { label: "Market cap", hint: "Eligible circulating market cap" },
  { label: "24h volume", hint: "Validated spot volume" },
  { label: "24h change", hint: "Price return over 24 hours" },
  { label: "Networks", hint: "Verified deployments" },
];

export function CryptoScreener() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("all");
  const [network, setNetwork] = useState("all");
  const [sort, setSort] = useState("market_cap");
  const [direction, setDirection] = useState<SortDirection>("desc");
  const [filtersOpen, setFiltersOpen] = useState(false);

  const activeFilters = useMemo(
    () => [category !== "all", network !== "all"].filter(Boolean).length,
    [category, network],
  );

  function resetFilters() {
    setQuery("");
    setCategory("all");
    setNetwork("all");
    setSort("market_cap");
    setDirection("desc");
  }

  return (
    <div className={styles.page}>
      <div className={styles.breadcrumb}><Link href="/">Market Overview</Link><span>/</span><b>Crypto Screener</b></div>
      <section className={styles.heading}>
        <div>
          <p className={styles.eyebrow}>MARKETS / DIGITAL ASSETS</p>
          <h1>Crypto Screener</h1>
          <p className={styles.subtitle}>Discover eligible crypto assets, compare market activity and inspect verified market coverage.</p>
        </div>
        <div className={styles.headingActions}>
          <span className={styles.readiness}><i /> Data connection pending</span>
          <button className={styles.export} type="button" disabled title="Export becomes available when validated screener records are connected"><Download size={15}/> Export CSV</button>
        </div>
      </section>

      <section className={styles.coverage} aria-label="Data availability notice">
        <span className={styles.coverageIcon}><ShieldCheck size={19}/></span>
        <div><b>Live universe is not connected</b><p>Filters and table structure are ready. Asset rows, counts and rankings will appear only after the backend supplies a paginated, classified universe with verified market observations.</p></div>
        <span className={styles.coverageTag}>NO SAMPLE DATA</span>
      </section>

      <section className={styles.summaryGrid} aria-label="Screener summary">
        <article className={styles.summaryCard}><span>Eligible assets</span><strong>—</strong><small>Awaiting complete universe</small></article>
        <article className={styles.summaryCard}><span>Assets with price</span><strong>—</strong><small>Validated spot observations</small></article>
        <article className={styles.summaryCard}><span>Market-cap coverage</span><strong>—</strong><small>Coverage denominator pending</small></article>
        <article className={styles.summaryCard}><span>Last catalogue sync</span><strong className={styles.pending}>Not available</strong><small>No successful sync recorded</small></article>
      </section>

      <section className={styles.workspace}>
        <div className={styles.toolbar}>
          <div className={styles.searchBox}><Search size={17}/><input aria-label="Search crypto assets" placeholder="Search name, symbol or canonical ID…" value={query} onChange={event => setQuery(event.target.value)}/>{query && <button type="button" onClick={() => setQuery("")} aria-label="Clear search">×</button>}</div>
          <button className={styles.filterToggle} type="button" onClick={() => setFiltersOpen(value => !value)} aria-expanded={filtersOpen}><SlidersHorizontal size={15}/> Filters {activeFilters > 0 && <span>{activeFilters}</span>}<ChevronDown size={14}/></button>
          <label className={styles.sortControl}><span>Sort by</span><select aria-label="Sort assets by" value={sort} onChange={event => setSort(event.target.value)}><option value="market_cap">Market cap</option><option value="volume">24h volume</option><option value="price_change">24h change</option><option value="name">Name</option></select></label>
          <button className={styles.direction} type="button" onClick={() => setDirection(value => value === "desc" ? "asc" : "desc")} aria-label={`Sort direction: ${direction}`}><ArrowDownUp size={15}/>{direction === "desc" ? "High to low" : "Low to high"}</button>
        </div>

        {filtersOpen && <div className={styles.filters}>
          <label>Asset category<select value={category} onChange={event => setCategory(event.target.value)}><option value="all">All eligible categories</option><option value="layer-1">Layer 1</option><option value="layer-2">Layer 2</option><option value="defi">DeFi</option><option value="infrastructure">Infrastructure</option></select></label>
          <label>Network<select value={network} onChange={event => setNetwork(event.target.value)}><option value="all">All networks</option><option value="ethereum">Ethereum</option><option value="solana">Solana</option><option value="arbitrum">Arbitrum</option><option value="base">Base</option></select></label>
          <button type="button" className={styles.reset} onClick={resetFilters}>Reset filters</button>
          <span className={styles.filterNote}><CircleHelp size={13}/> Filter options are presentation controls until the eligible asset catalogue is connected.</span>
        </div>}

        <div className={styles.tableMeta}><div><b>Asset universe</b><span>Canonical identities · eligible crypto only</span></div><span className={styles.resultCount}>No records loaded</span></div>
        <div className={styles.tableWrap}>
          <table className={styles.table}>
            <thead><tr>{columns.map(column => <th key={column.label}><span>{column.label}</span><span className={styles.hint} title={column.hint}><CircleHelp size={12}/></span></th>)}</tr></thead>
            <tbody><tr><td colSpan={columns.length}>
              <div className={styles.empty}>
                <span className={styles.emptyIcon}><Filter size={21}/></span>
                <b>{query || activeFilters ? "No matching records yet" : "Waiting for validated market data"}</b>
                <p>{query || activeFilters ? "The screener has no connected records to evaluate these filters. Reset the controls or return when the catalogue is available." : "The table will populate when the API returns canonical asset IDs, eligible classification, market observations and coverage metadata. No illustrative assets are shown."}</p>
                {(query || activeFilters) && <button type="button" onClick={resetFilters}>Clear search and filters</button>}
                <span className={styles.unavailable}><i/> Catalogue unavailable · API integration pending</span>
              </div>
            </td></tr></tbody>
          </table>
        </div>
        <div className={styles.tableFooter}><span>Rows per page <b>25</b></span><span>— of — assets</span><div><button disabled type="button" aria-label="Previous page">‹</button><button disabled type="button" aria-label="Next page">›</button></div></div>
      </section>

      <section className={styles.footerNote}><div><RefreshCw size={14}/><span><b>Data integrity</b> · The screener will distinguish zero values from missing values, keep unavailable metrics null, and disclose partial or stale coverage.</span></div><Link href="/tokenized-rwa-screener">Explore tokenized products <ArrowRight size={14}/></Link></section>
    </div>
  );
}
