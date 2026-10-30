import type { Metadata } from "next";
import { TokenizedRwaProductDetail } from "@/components/tokenized-rwa-product-detail";

export const metadata: Metadata = {
  title: "Tokenized Product Detail",
  description: "Canonical issuer-product identity, classification provenance and verified deployments.",
};

export default async function TokenizedRwaProductPage({
  params,
}: {
  params: Promise<{ productId: string }>;
}) {
  const { productId } = await params;
  return <TokenizedRwaProductDetail productId={productId} />;
}
