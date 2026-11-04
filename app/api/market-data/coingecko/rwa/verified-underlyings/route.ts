import { NextResponse } from "next/server";

export async function GET() {
  const base = process.env.RWA_API_BASE_URL?.replace(/\/+$/, "");
  if (!base) {
    return NextResponse.json(
      { code: "API_NOT_CONFIGURED", detail: "Set RWA_API_BASE_URL to the RWAs Intelligence API base URL." },
      { status: 503, headers: { "Cache-Control": "no-store" } },
    );
  }
  try {
    const response = await fetch(
      `${base}/api/v1/market-data/coingecko/rwa/verified-underlyings`,
      { cache: "no-store", headers: { accept: "application/json" } },
    );
    const payload = await response.json().catch(() => ({
      code: "INVALID_UPSTREAM_RESPONSE",
      detail: "The market-data API returned invalid JSON.",
    }));
    return NextResponse.json(payload, {
      status: response.status,
      headers: { "Cache-Control": "no-store" },
    });
  } catch {
    return NextResponse.json(
      { code: "UPSTREAM_UNAVAILABLE", detail: "The CoinGecko market-data service could not be reached." },
      { status: 502, headers: { "Cache-Control": "no-store" } },
    );
  }
}
