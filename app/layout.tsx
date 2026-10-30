import type { Metadata } from "next";
import type { ReactNode } from "react";
import { AppShell } from "@/components/app-shell";
import "./globals.css";
export const metadata: Metadata = { title:{default:"RWAs Intelligence | IntelliSages",template:"%s | RWAs Intelligence"},description:"Market discovery and research intelligence for tokenized real-world assets, crypto markets and onchain venues." };
export default function RootLayout({children}:{children:ReactNode}) { return <html lang="en"><body><AppShell>{children}</AppShell></body></html>; }