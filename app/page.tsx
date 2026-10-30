import Link from "next/link";
import { ArrowRight, ArrowUpDown, Database, Download, Globe2, Layers3, ShieldCheck } from "lucide-react";
import { productPages } from "@/lib/navigation";

function Metric({label,detail}:{label:string;detail:string}) {
  return <article className="metric-card"><div className="metric-top"><span className="metric-symbol"><Database size={16}/></span><span className="status status-off">Unavailable</span></div><p>{label}</p><strong>—</strong><small>{detail}</small><div className="metric-reason">Withheld until source coverage and calculation are validated.</div></article>;
}

function TrendingPanel({title,description}:{title:string;description:string}) {
  return <article className="panel">
    <div className="section-title"><div><p className="eyebrow">MARKET DISCOVERY</p><h2>{title}</h2><p className="subtitle">{description}</p></div><span className="count">NOT CONNECTED</span></div>
    <div className="tableWrap" style={{overflowX:"auto"}}>
      <table style={{width:"100%",borderCollapse:"collapse",minWidth:440}}>
        <thead><tr>{["Asset / product","Price","Market cap / value","24h volume","24h change"].map(label=><th key={label} style={{textAlign:"left",padding:"11px 8px",fontSize:9,color:"#8994a5",fontWeight:600,borderBottom:"1px solid #edf0f4"}}>{label}</th>)}</tr></thead>
        <tbody><tr><td colSpan={5}><div className="empty-state"><Database size={20}/><b>No validated records available</b><p>Trending rankings require a complete eligible catalogue and comparable, timestamped observations. No sample rows are shown.</p></div></td></tr></tbody>
      </table>
    </div>
    <div className="panel-foot"><span>Sort <ArrowUpDown size={12} style={{display:"inline",verticalAlign:"middle"}}/> · Export <Download size={12} style={{display:"inline",verticalAlign:"middle"}}/></span><span className="status status-off">Unavailable until data is connected</span></div>
  </article>;
}

export default function HomePage(){return <div className="stack">
<section className="welcome"><div><p className="eyebrow">GLOBAL INTELLIGENCE</p><h1>Market Overview</h1><p className="subtitle">A clearer view of digital asset markets, tokenized products and the venues connecting them.</p></div><span className="validation-pill"><i/> Validation in progress</span></section>
<section className="notice"><span className="notice-icon"><ShieldCheck size={18}/></span><div><b>Evidence-first market intelligence</b><p>Live market totals are withheld until identity, source coverage, calculation, observation freshness and data rights are verified.</p></div><small>NO MOCK MARKET DATA</small></section>
<section><div className="section-title"><div><p className="eyebrow">MARKET SNAPSHOT</p><h2>Global market indicators</h2></div><span>4 metrics · readiness gated</span></div><div className="metrics"><Metric label="Crypto market cap" detail="Adjusted eligible-universe total"/><Metric label="Tokenized RWA value" detail="Deduplicated economic supply"/><Metric label="24h market volume" detail="Cross-venue overlap-adjusted"/><Metric label="Market-wide correlation" detail="Aligned 30D return series"/></div></section>
<section className="columns"><TrendingPanel title="Trending Crypto" description="Eligible crypto assets ranked on verified market observations."/><TrendingPanel title="Trending Tokenized Assets" description="Distinct issuer products with verified deployments and market coverage."/></section>
<section className="columns"><article className="panel"><div className="section-title"><div><p className="eyebrow">PLATFORM READINESS</p><h2>Coverage before conclusions</h2></div><Globe2 size={18}/></div><div className="empty-state"><Layers3 size={23}/><b>Provider coverage is being established</b><p>Catalogue completeness, provider permissions and observation freshness will appear here when verified.</p></div><div className="panel-foot"><span>Provider status</span><span className="status status-partial">Partial validation</span></div></article>
<article className="panel"><div className="section-title"><div><p className="eyebrow">DISCOVERY</p><h2>Explore the intelligence stack</h2></div></div><p className="panel-copy">Move from an underlying asset to its issuer product, verified deployment and exact market.</p>{[["Tokenized RWA Screener","Products, issuers and networks","/tokenized-rwa-screener"],["Crypto Screener","Eligible crypto asset universe","/crypto-screener"],["HIP-3 Markets","Builder-scoped perpetual markets","/hip-3"]].map(x=><Link className="explore-row" href={x[2]} key={x[2]}><span><b>{x[0]}</b><small>{x[1]}</small></span><ArrowRight size={16}/></Link>)}</article></section>
<section className="panel directory"><div className="section-title"><div><p className="eyebrow">MVP WORKSPACE</p><h2>Sixteen approved product surfaces</h2><p className="subtitle">All pages remain in navigation while their individual metrics pass readiness gates.</p></div><span className="count">16 PAGES</span></div><div className="directory-grid">{productPages.map((p,i)=><Link href={"/"+p.slug} className="directory-row" key={p.slug}><small>{String(i+1).padStart(2,"0")}</small><b>{p.label}</b><span>{p.reserved?"Reserved":"Readiness gated"}</span><ArrowRight size={14}/></Link>)}</div></section></div>}
