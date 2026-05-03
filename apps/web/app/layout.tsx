import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono, Lora } from "next/font/google";
import Link from "next/link";
import { ScanLine } from "lucide-react";
import { Toaster } from "sonner";
import { ServiceWorkerRegistrar } from "@/components/ServiceWorkerRegistrar";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });
const lora = Lora({
  variable: "--font-lora",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Scanner de Imagens — Fotos em Markdown estruturado",
  description:
    "Converta fotografias de livros e artigos em Markdown e DOCX preservando imagens e layout.",
  manifest: "/manifest.json",
  applicationName: "Scanner de Imagens",
  appleWebApp: {
    capable: true,
    title: "Scanner",
    statusBarStyle: "default",
  },
};

export const viewport: Viewport = {
  themeColor: "#020617",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} ${lora.variable} antialiased bg-mesh min-h-screen`}
      >
        <ServiceWorkerRegistrar />
        <header className="sticky top-0 z-40 glass-dark">
          <nav className="max-w-6xl mx-auto px-6 py-4 flex items-center gap-6 text-sm">
            <Link href="/" className="flex items-center gap-2.5 group">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-cyan-500 to-teal-500 flex items-center justify-center shadow-lg shadow-cyan-500/20 group-hover:shadow-cyan-500/40 transition-shadow">
                <ScanLine className="w-4 h-4 text-white" />
              </div>
              <span className="text-base font-black tracking-tighter">
                Scanner <span className="gradient-text">de Imagens</span>
              </span>
            </Link>
            <div className="ml-auto flex items-center gap-1">
              <Link
                href="/"
                className="px-3 py-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-white/5 transition-colors"
              >
                Novo
              </Link>
              <Link
                href="/jobs"
                className="px-3 py-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-white/5 transition-colors"
              >
                Jobs
              </Link>
              <Link
                href="/health"
                className="px-3 py-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-white/5 transition-colors"
              >
                Health
              </Link>
            </div>
          </nav>
        </header>
        <main className="max-w-6xl mx-auto px-6 py-10 relative z-10">{children}</main>
        <Toaster richColors position="bottom-right" theme="dark" />
      </body>
    </html>
  );
}
