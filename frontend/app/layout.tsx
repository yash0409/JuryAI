import type { Metadata } from "next";
import Link from "next/link";
import { Inter } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });

export const metadata: Metadata = {
  title: "VerdictIQ",
  description: "AI-powered legal document analysis",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={cn("font-sans", inter.variable)}>
      <body className="min-h-screen bg-[#0a0f1e] text-[#e2e8f0] antialiased">
        <div className="min-h-screen bg-[#0a0f1e] w-full">
          <header className="fixed inset-x-0 top-0 z-50 border-b border-white/10 bg-[#0a0f1e]/80 backdrop-blur-xl">
            <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 sm:px-6 lg:px-8">
              <Link href="/" className="flex items-center gap-3">
                <span className="text-2xl">⚖️</span>
                <span className="text-white text-lg font-semibold tracking-tight">
                  VerdictIQ
                </span>
              </Link>
              <nav className="flex items-center gap-8 text-sm font-medium text-[#94a3b8]">
                <Link href="/upload" className="transition hover:text-white">
                  Upload
                </Link>
                <Link href="/analysis" className="transition hover:text-white">
                  Analysis
                </Link>
              </nav>
            </div>
          </header>

          <main className="pt-24">{children}</main>
        </div>
      </body>
    </html>
  );
}
