import { NextRequest, NextResponse } from "next/server";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ productId: string }> },
) {
  const base = process.env.RWA_API_BASE_URL?.replace(/\/+$/, "");
  if (!base) {
    return NextResponse.json(
      { code: "API_NOT_CONFIGURED", detail: "Set RWA_API_BASE_URL to the RWAs Intelligence API base URL." },
      { status: 503 },
    );
  }

  const { productId } = await params;
  const upstreamUrl = new URL(
    `${base}/api/v1/catalogue/tokenized-products/${encodeURIComponent(productId)}`,
  );
  const asOf = request.nextUrl.searchParams.get("as_of");
  if (asOf) upstreamUrl.searchParams.set("as_of", asOf);

  try {
    const upstream = await fetch(upstreamUrl, {
      headers: { accept: "application/json" },
      cache: "no-store",
      signal: AbortSignal.timeout(10_000),
    });
    const payload = await upstream.json().catch(() => ({
      code: "INVALID_UPSTREAM_RESPONSE",
      detail: "The catalogue API returned an invalid response.",
    }));
    return NextResponse.json(payload, {
      status: upstream.status,
      headers: { "Cache-Control": "no-store" },
    });
  } catch {
    return NextResponse.json(
      { code: "UPSTREAM_UNAVAILABLE", detail: "The catalogue API could not be reached." },
      { status: 502 },
    );
  }
}
