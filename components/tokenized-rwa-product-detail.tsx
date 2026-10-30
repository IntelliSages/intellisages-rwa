"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import type { TokenizedProductCatalogueItem } from "@/lib/catalogue-types";

type ApiError = { code?: string; detail?: string };
export function TokenizedRwaProductDetail({ productId }: { productId: string }) {
  const [product, setProduct] = useState<TokenizedProductCatalogueItem | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();
    setLoading(true);
    setError(null);
    fetch(`/api/catalogue/tokenized-products/${encodeURIComponent(productId)}`, {
      signal: controller.signal,
      headers: { accept: "application/json" },
    })
      .then(async response => {
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) throw payload as ApiError;
        return payload as TokenizedProductCatalogueItem;
      })
      .then(setProduct)
      .catch(reason => {
        if (!controller.signal.aborted) {
          setError(typeof reason === "object" && reason !== null ? reason as ApiError : { detail: "The product could not be loaded." });
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [productId]);

  return <main style={{maxWidth:1120,margin:"0 auto",padding:"32px 24px 64px",color:"#182230"}}>
    <nav aria-label="Breadcrumb" style={{fontSize:13,color:"#64748b",marginBottom:24}}>
      <Link href="/" style={{color:"inherit"}}>Market Overview</Link> <span>/</span>{" "}
      <Link href="/tokenized-rwa-screener" style={{color:"inherit"}}>Tokenized RWA Screener</Link> <span>/</span> Product
    </nav>
    {loading ? <section aria-live="polite"><h1>Loading product identity…</h1><p>Resolving the exact canonical issuer-product record.</p></section>
      : error ? <section role="alert" style={{border:"1px solid #e2e8f0",borderRadius:12,padding:24}}>
        <h1>Product unavailable</h1>
        <p>{error.detail ?? (error.code === "API_NOT_CONFIGURED" ? "The backend API is not configured." : "No effective RWA product was found for this identifier.")}</p>
        <p style={{fontSize:12,color:"#64748b"}}>{error.code ?? "REQUEST_FAILED"}</p>
        <Link href="/tokenized-rwa-screener">Return to Tokenized RWA Screener</Link>
      </section>
      : product ? <div style={{display:"grid",gap:20}}>
        <header>
          <p style={{fontSize:11,fontWeight:700,letterSpacing:1.2,color:"#64748b"}}>CANONICAL ISSUER PRODUCT</p>
          <h1 style={{fontSize:32,margin:"8px 0"}}>{product.display_name}{product.symbol ? ` · ${product.symbol}` : ""}</h1>
          <p style={{color:"#64748b"}}>{product.underlying.display_name} · Issued by {product.issuer.legal_name}</p>
        </header>
        <section style={{display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(220px,1fr))",gap:12}}>
          {[
            ["Canonical product ID",product.id],
            ["Canonical key",product.canonical_key],
            ["Native product ID",product.native_product_id],
            ["Instrument form",product.instrument_form],
            ["Representation",product.representation_type.replaceAll("_"," ")],
            ["Unit description",product.unit_description],
          ].map(([label,value])=><article key={label} style={{border:"1px solid #e2e8f0",borderRadius:12,padding:16,minWidth:0}}>
            <small style={{display:"block",color:"#64748b",marginBottom:8}}>{label}</small><b style={{overflowWrap:"anywhere"}}>{value}</b>
          </article>)}
        </section>
        <section style={{border:"1px solid #e2e8f0",borderRadius:12,padding:20}}>
          <h2 style={{fontSize:18,marginTop:0}}>Underlying identity</h2>
          <p><b>{product.underlying.display_name}</b> · {product.underlying.asset_type.replaceAll("_"," ")}</p>
          <small style={{color:"#64748b"}}>Canonical underlying ID: {product.underlying.id}</small>
        </section>
        <section style={{border:"1px solid #e2e8f0",borderRadius:12,padding:20}}>
          <h2 style={{fontSize:18,marginTop:0}}>Classification provenance</h2>
          <p>RWA classification · effective from {product.classification.effective_from}{product.classification.effective_to ? ` to ${product.classification.effective_to}` : " · no recorded end date"}</p>
          <p>Source: {product.classification.source}</p>
          <p style={{overflowWrap:"anywhere"}}>Evidence: {product.classification.evidence_ref}</p>
          <p>Provider-global inclusion: {product.classification.provider_global_included === null ? "Unknown" : product.classification.provider_global_included ? "Included" : "Excluded"}</p>
        </section>
        <section style={{border:"1px solid #e2e8f0",borderRadius:12,padding:20}}>
          <h2 style={{fontSize:18,marginTop:0}}>Product deployments</h2>
          {product.deployments.length ? <ul style={{paddingLeft:20,display:"grid",gap:12}}>
            {product.deployments.map(deployment=><li key={deployment.id}>
              <b>{deployment.network.display_name}</b> · {deployment.is_verified ? "Verified in registry" : "Unverified"}
              <div style={{fontSize:12,color:"#64748b"}}>{deployment.network.namespace} · {deployment.network.family}</div>
              <code style={{fontSize:12,overflowWrap:"anywhere"}}>{deployment.native_identifier}</code>
            </li>)}
          </ul> : <p>No deployment records are registered for this product.</p>}
          <p style={{fontSize:12,color:"#64748b"}}>{product.unverified_deployment_count} unverified deployment record(s). Registry verification is not legal, backing or audit verification.</p>
        </section>
        <section style={{border:"1px solid #e2e8f0",borderRadius:12,padding:20}}>
          <h2 style={{fontSize:18,marginTop:0}}>Market observations</h2>
          <p>Price, tokenized value, volume, liquidity, performance and perpetual availability are unavailable until validated source observations and coverage are connected.</p>
        </section>
      </div> : null}
  </main>;
}
