import { NextRequest, NextResponse } from "next/server";

const allowedParams = ["q", "issuer_id", "network_id", "sort", "direction", "limit", "offset", "as_of"] as const;

export async function GET(request: NextRequest) {
  const base = process.env.RWA_API_BASE_URL?.replace(/\/+$/, "");
  if (!base) {
    return NextResponse.json(
      { code: "API_NOT_CONFIGURED", detail: "Set RWA_API_BASE_URL to the RWAs Intelligence API base URL." },
      { status: 503 },
    );
  }

  const upstream = new URL(`${base}/api/v1/catalogue/tokenized-products`);
  for (const key of allowedParams) {
    const value = request.nextUrl.searchParams.get(key);
    if (value) upstream.searchParams.set(key, value);
  }

  try {
    const response = await fetch(upstream, { cache: "no-store", headers: { accept: "application/json" } });
    const body = await response.json().catch(() => ({ code: "INVALID_UPSTREAM_RESPONSE" }));
    return NextResponse.json(body, { status: response.status, headers: { "Cache-Control": "no-store" } });
  } catch {
    return NextResponse.json(
      { code: "UPSTREAM_UNAVAILABLE", detail: "The catalogue service could not be reached. Retry when the API is available." },
      { status: 502 },
    );
  }
}
