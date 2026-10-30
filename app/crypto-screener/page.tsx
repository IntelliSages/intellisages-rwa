import type { Metadata } from "next";
import { CryptoScreener } from "@/components/crypto-screener";

export const metadata: Metadata = {
  title: "Crypto Screener",
  description: "Explore the eligible crypto asset universe with transparent data coverage.",
};

export default function CryptoScreenerPage() {
  return <CryptoScreener />;
}
