export type ProductPage={slug:string;label:string;group:"Markets"|"Platforms"|"Intelligence";description:string;purpose:string;reserved?:boolean};
export const productPages:ProductPage[]=[
{slug:"crypto-screener",label:"Crypto Screener",group:"Markets",description:"Discover and compare eligible crypto assets.",purpose:"Verified eligible universe, complete pagination and explicit catalogue coverage."},
{slug:"tokenized-rwa-screener",label:"Tokenized RWA Screener",group:"Markets",description:"Explore tokenized assets and distinct issuer products.",purpose:"One row per canonical issuer product with verified deployments."},
{slug:"correlation",label:"Correlation",group:"Markets",description:"Compare aligned return series when sufficient history exists.",purpose:"Aligned observations, stable membership and approved return methodology."},
{slug:"hip-3",label:"HIP-3 Markets",group:"Markets",description:"Explore builder-deployed perpetual markets.",purpose:"Exact builder, domain and native market identity."},
{slug:"ondo",label:"Ondo",group:"Platforms",description:"Issuer-specific products, deployments and markets.",purpose:"Verified product-level deployments and permitted source observations."},
{slug:"bstocks",label:"bStocks",group:"Platforms",description:"Discover supported tokenized stock products and markets.",purpose:"Keep the page visible while blocked source paths remain unavailable."},
{slug:"xstocks",label:"xStocks",group:"Platforms",description:"Explore issuer products, deployments and activity.",purpose:"Do not imply full catalogue coverage from a first-page sample."},
{slug:"backpack",label:"Backpack",group:"Platforms",description:"Inspect securities catalogue and supported market context.",purpose:"Distinguish RFQ/catalogue records from listed markets."},
{slug:"robinhood",label:"Robinhood Tokenized Assets",group:"Platforms",description:"Explore issuer products and covered market observations.",purpose:"Reconcile issuer catalogue membership and token-volume semantics."},
{slug:"prestocks",label:"PreStocks",group:"Platforms",description:"Explore pre-IPO token products and approved research fields.",purpose:"Separate snapshot evidence from unproven historical valuation or index series."},
{slug:"paimon",label:"Paimon",group:"Platforms",description:"Inspect distinct issued products and validated snapshots.",purpose:"Deals, events and settlements remain deferred."},
{slug:"funding-rates",label:"Funding Rates",group:"Intelligence",description:"Compare supported perpetual funding observations.",purpose:"Preserve native units, sign conventions, payment intervals and timestamps."},
{slug:"defi",label:"DeFi",group:"Intelligence",description:"Explore supported pools and lending markets.",purpose:"Separate reserves, supplied/borrowed assets, collateral and available liquidity."},
{slug:"trader-intelligence",label:"Trader Intelligence",group:"Intelligence",description:"A future workspace for trader performance and exposure.",purpose:"Accounting, identity and authorization require joint specification.",reserved:true},
{slug:"event-feed",label:"Intelligence Event Feed",group:"Intelligence",description:"A sourced feed of market, onchain, trading and macro observations.",purpose:"Taxonomy, deduplication, scoring and alerts remain reserved.",reserved:true}
];
export const getPageBySlug=(slug:string)=>productPages.find(p=>p.slug===slug);
export const groups=[{label:"Overview",items:[{slug:"/",label:"Market Overview"}]},...(["Markets","Platforms","Intelligence"] as const).map(group=>({label:group,items:productPages.filter(p=>p.group===group).map(p=>({slug:"/"+p.slug,label:p.label}))}))];