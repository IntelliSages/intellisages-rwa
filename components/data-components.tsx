import styles from "./data-components.module.css";
import type { Availability } from "@/lib/catalogue-types";

const labels: Record<Availability, string> = {
  available: "Available",
  partial: "Partial",
  stale: "Stale",
  unavailable: "Unavailable",
  not_applicable: "Not applicable",
  error: "Error",
};

export function AvailabilityPill({ status, reason, observedAt }: {
  status: Availability;
  reason?: string;
  observedAt?: string | null;
}) {
  const description = [reason, observedAt ? `Observed ${observedAt}` : null].filter(Boolean).join(" · ");
  return <span
    className={`${styles.pill} ${styles[status]}`}
    title={description || labels[status]}
    aria-label={`${labels[status]}${description ? `: ${description}` : ""}`}
  ><i />{labels[status]}</span>;
}

export function MetricUnavailable({ label, reason }: { label: string; reason: string }) {
  return <span className={styles.metricUnavailable} title={reason} aria-label={`${label}: unavailable. ${reason}`}>
    <span>—</span><small>Not connected</small>
  </span>;
}

export function DataProvenance({ source, evidenceRef, effectiveFrom, effectiveTo, providerGlobalIncluded }: {
  source: string;
  evidenceRef: string;
  effectiveFrom: string;
  effectiveTo: string | null;
  providerGlobalIncluded: boolean | null;
}) {
  const external = /^https?:\/\//i.test(evidenceRef);
  return <details className={styles.provenance}>
    <summary>Classification evidence <span>View provenance</span></summary>
    <dl>
      <div><dt>Classification source</dt><dd>{source}</dd></div>
      <div><dt>Evidence reference</dt><dd>{external ? <a href={evidenceRef} target="_blank" rel="noreferrer">{evidenceRef}</a> : evidenceRef}</dd></div>
      <div><dt>Effective period</dt><dd>{effectiveFrom} → {effectiveTo ?? "Open-ended"}</dd></div>
      <div><dt>Provider-global inclusion</dt><dd>{providerGlobalIncluded === null ? "Unknown" : providerGlobalIncluded ? "Included" : "Excluded"}</dd></div>
    </dl>
  </details>;
}
