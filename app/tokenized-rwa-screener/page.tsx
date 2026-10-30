import type { Metadata } from "next";
import { TokenizedRwaScreener } from "@/components/tokenized-rwa-screener";

export const metadata: Metadata = {
  title: "Tokenized RWA Screener",
  description: "Discover tokenized products, issuers and verified network deployments.",
};

export default function TokenizedRwaScreenerPage() {
  return <TokenizedRwaScreener />;
}
