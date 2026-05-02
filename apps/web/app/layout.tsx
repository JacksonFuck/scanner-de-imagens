import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import { Toaster } from "sonner";
import { ServiceWorkerRegistrar } from "@/components/ServiceWorkerRegistrar";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Scanner de Imagens",
  description: "Converte fotos de páginas em Markdown/DOCX/PDF",
  manifest: "/manifest.json",
  applicationName: "Scanner de Imagens",
  appleWebApp: {
    capable: true,
    title: "Scanner",
    statusBarStyle: "default",
  },
};

export const viewport: Viewport = {
  themeColor: "#0f172a",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body className={inter.className}>
        <ServiceWorkerRegistrar />
        <header className="border-b border-zinc-200 dark:border-zinc-800">
          <nav className="max-w-5xl mx-auto px-4 py-3 flex items-center gap-4 text-sm">
            <Link href="/" className="font-semibold">
              Scanner
            </Link>
            <Link href="/" className="text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100">
              Novo
            </Link>
            <Link href="/jobs" className="text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100">
              Jobs
            </Link>
            <Link href="/health" className="text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 ml-auto">
              Health
            </Link>
          </nav>
        </header>
        <main className="max-w-5xl mx-auto px-4 py-6">{children}</main>
        <Toaster richColors position="bottom-right" />
      </body>
    </html>
  );
}
