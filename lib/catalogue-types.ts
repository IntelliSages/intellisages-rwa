export type Availability = "available" | "partial" | "stale" | "unavailable" | "not_applicable" | "error";

export interface CatalogueFacet { id: string; label: string }
export interface TokenizedProductCatalogueItem {
  id: string;
  canonical_key: string;
  native_product_id: string;
  display_name: string;
  symbol: string | null;
  instrument_form: string;
  unit_description: string;
  representation_type: "independent_issuance" | "bridge" | "wrapper" | "unknown";
  issuer: { id: string; legal_name: string };
  underlying: { id: string; display_name: string; asset_type: string };
  classification: {
    classification: "rwa";
    effective_from: string;
    effective_to: string | null;
    source: string;
    evidence_ref: string;
    provider_global_included: boolean | null;
  };
  deployments: Array<{
    id: string;
    network: { id: string; namespace: string; display_name: string; family: string };
    native_identifier: string;
    representation_type: "independent_issuance" | "bridge" | "wrapper" | "unknown";
    is_verified: boolean;
  }>;
  unverified_deployment_count: number;
}
export interface TokenizedProductCatalogueResponse {
  as_of: string;
  items: TokenizedProductCatalogueItem[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
  facets: { issuers: CatalogueFacet[]; networks: CatalogueFacet[] };
  coverage: { status: "unknown"; scope: string; note: string };
}
