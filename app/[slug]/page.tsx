import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getPageBySlug, productPages } from "@/lib/navigation";
import { ProductWorkspace } from "@/components/product-workspace";
import { TokenizedRwaScreener } from "@/components/tokenized-rwa-screener";

type Props = { params: Promise<{ slug: string }> };

const TOKENIZED_RWA_SLUG = "tokenized-rwa-screener";

export function generateStaticParams() {
  return productPages.map(page => ({ slug: page.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const page = getPageBySlug(slug);

  if (!page) return { title: "Not found" };

  if (slug === TOKENIZED_RWA_SLUG) {
    return {
      title: "Tokenized RWA Screener",
      description: "Discover tokenized products, issuers and verified network deployments.",
    };
  }

  return { title: page.label };
}

export default async function ProductPage({ params }: Props) {
  const { slug } = await params;
  const page = getPageBySlug(slug);
  if (!page) notFound();

  // Render this data-backed page explicitly through the shared slug route.
  // This avoids the static /tokenized-rwa-screener route colliding with
  // /[slug] on deployments where the generic workspace is served instead.
  if (slug === TOKENIZED_RWA_SLUG) {
    return <TokenizedRwaScreener />;
  }

  return <ProductWorkspace page={page} />;
}
