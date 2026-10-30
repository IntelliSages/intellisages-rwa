import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { TokenizedRwaScreener } from "@/components/tokenized-rwa-screener";
import type { TokenizedProductCatalogueResponse } from "@/lib/catalogue-types";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

function catalogue(): TokenizedProductCatalogueResponse {
  return {
    as_of: "2026-10-30",
    items: [{
      id: "product-a",
      canonical_key: "product:issuer-a:nvdax",
      native_product_id: "NVDAx",
      display_name: "NVDAx",
      symbol: "NVDAx",
      instrument_form: "tokenized_equity",
      unit_description: "one token",
      representation_type: "wrapper",
      issuer: { id: "issuer-a", legal_name: "Issuer A" },
      underlying: { id: "underlying-nvidia", display_name: "NVIDIA", asset_type: "equity" },
      classification: {
        classification: "rwa",
        effective_from: "2026-01-01",
        effective_to: null,
        source: "Issuer register",
        evidence_ref: "evidence:issuer:nvdax",
        provider_global_included: null,
      },
      deployments: [{
        id: "deployment-ethereum",
        network: { id: "network-eth", namespace: "eip155:1", display_name: "Ethereum", family: "evm" },
        native_identifier: "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        representation_type: "wrapper",
        is_verified: true,
      }],
      unverified_deployment_count: 1,
    }],
    total: 1,
    limit: 25,
    offset: 0,
    has_more: false,
    facets: {
      issuers: [{ id: "issuer-a", label: "Issuer A" }],
      networks: [{ id: "network-eth", label: "Ethereum" }],
    },
    coverage: {
      status: "unknown",
      scope: "canonical identity registry",
      note: "Registered records only; provider universe coverage is unknown.",
    },
  };
}

describe("Tokenized RWA screener", () => {
  it("renders canonical product identity once and discloses missing market metrics", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => catalogue(),
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<TokenizedRwaScreener />);

    expect(await screen.findByText("NVIDIA")).toBeInTheDocument();
    const productLink = screen.getByRole("link", { name: "NVDAx" });
    expect(productLink).toHaveAttribute("href", "/tokenized-rwa-screener/product-a");
    expect(screen.getByText(/Issuer A/)).toBeInTheDocument();
    expect(screen.getByText("Ethereum")).toBeInTheDocument();
    expect(screen.getByText("1 pending")).toBeInTheDocument();
    expect(screen.getByLabelText(/Tokenized price: unavailable/)).toBeInTheDocument();
    expect(screen.getByText(/Provider coverage unknown/)).toBeInTheDocument();
  });

  it("expands product details and reveals classification evidence", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: async () => catalogue(),
    }));

    render(<TokenizedRwaScreener />);
    await screen.findByText("NVIDIA");
    fireEvent.click(screen.getByRole("button", { name: "Expand NVDAx details" }));

    expect(screen.getByText("Canonical product record")).toBeInTheDocument();
    fireEvent.click(screen.getByText(/Classification evidence/));
    expect(screen.getByText("Issuer register")).toBeInTheDocument();
    expect(screen.getByText("evidence:issuer:nvdax")).toBeInTheDocument();
    expect(screen.getByText("Unknown")).toBeInTheDocument();
  });

  it("uses the selected verified network as an API filter", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => catalogue(),
    });
    vi.stubGlobal("fetch", fetchMock);

    render(<TokenizedRwaScreener />);
    await screen.findByText("NVIDIA");
    fireEvent.click(screen.getByRole("button", { name: /Filters/ }));
    fireEvent.change(screen.getByLabelText("Network"), { target: { value: "network-eth" } });

    await waitFor(() => {
      expect(fetchMock).toHaveBeenLastCalledWith(
        expect.stringContaining("network_id=network-eth"),
        expect.objectContaining({ headers: { accept: "application/json" } }),
      );
    });
  });

  it("shows an explicit configuration state when the API proxy is not configured", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: false,
      status: 503,
      json: async () => ({
        code: "API_NOT_CONFIGURED",
        detail: "Set RWA_API_BASE_URL to the RWAs Intelligence API base URL.",
      }),
    }));

    render(<TokenizedRwaScreener />);
    expect(await screen.findByText("Frontend is running; API connection is not configured")).toBeInTheDocument();
    expect(screen.getByText(/RWA_API_BASE_URL/)).toBeInTheDocument();
  });
});
