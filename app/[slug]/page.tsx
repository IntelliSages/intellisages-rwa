import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getPageBySlug, productPages } from "@/lib/navigation";
import { ProductWorkspace } from "@/components/product-workspace";

type Props = { params: Promise<{ slug: string }> };

export function generateStaticParams() {
  return productPages.map(page => ({ slug: page.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  return { title: getPageBySlug(slug)?.label ?? "Not found" };
}

export default async function ProductPage({ params }: Props) {
  const { slug } = await params;
  const page = getPageBySlug(slug);
  if (!page) notFound();
  return <ProductWorkspace page={page} />;
}
