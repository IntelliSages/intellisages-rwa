import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AvailabilityPill, DataProvenance, MetricUnavailable } from "@/components/data-components";

describe("shared data disclosure components", () => {
  it("distinguishes available zero from unavailable", () => {
    render(<>
      <AvailabilityPill status="available" reason="A measured value." />
      <MetricUnavailable label="Tokenized value" reason="No observation is connected." />
    </>);
    expect(screen.getByText("Available")).toBeInTheDocument();
    expect(screen.getByLabelText("Tokenized value: unavailable. No observation is connected.")).toBeInTheDocument();
  });

  it("exposes partial and stale reasons accessibly", () => {
    render(<>
      <AvailabilityPill status="partial" reason="Only two verified networks are covered." />
      <AvailabilityPill status="stale" observedAt="2026-10-29T10:00:00Z" />
    </>);
    expect(screen.getByLabelText(/Partial: Only two verified networks/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Stale: Observed 2026-10-29/)).toBeInTheDocument();
  });

  it("shows classification source, evidence and unknown global inclusion", () => {
    render(<DataProvenance
      source="Issuer classification register"
      evidenceRef="evidence:classification:42"
      effectiveFrom="2026-01-01"
      effectiveTo={null}
      providerGlobalIncluded={null}
    />);
    expect(screen.getByText("Issuer classification register")).toBeInTheDocument();
    expect(screen.getByText("evidence:classification:42")).toBeInTheDocument();
    expect(screen.getByText("Unknown")).toBeInTheDocument();
  });
});
