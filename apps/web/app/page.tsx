"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { ChevronDown, ChevronRight } from "lucide-react";
import { DropZone } from "@/components/DropZone";
import { Spinner } from "@/components/Spinner";
import { EnablePush } from "@/components/EnablePush";
import { InstallPrompt } from "@/components/InstallPrompt";
import { createJob } from "@/lib/api";
import { cn } from "@/lib/cn";

const FORMAT_OPTIONS = ["md", "docx", "pdf", "all"] as const;

export default function HomePage() {
  const router = useRouter();
  const [files, setFiles] = useState<File[]>([]);
  const [formats, setFormats] = useState<string[]>(["md"]);
  const [merge, setMerge] = useState(false);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [device, setDevice] = useState("cpu");
  const [lang, setLang] = useState("por");
  const [ocrEngine, setOcrEngine] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const toggleFormat = (f: string) => {
    setFormats((prev) => (prev.includes(f) ? prev.filter((x) => x !== f) : [...prev, f]));
  };

  const onSubmit = async () => {
    if (files.length === 0) {
      toast.error("Selecione ao menos uma imagem.");
      return;
    }
    setSubmitting(true);
    try {
      const job = await createJob({
        files,
        formats,
        merge,
        device: device || undefined,
        lang: lang || undefined,
        ocr_engine: ocrEngine || undefined,
      });
      toast.success("Job criado");
      router.push(`/jobs/${job.id}`);
    } catch (e) {
      toast.error(`Falha ao criar job: ${(e as Error).message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Novo scan</h1>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          Envie fotos de páginas e receba Markdown estruturado.
        </p>
      </div>

      <DropZone files={files} onChange={setFiles} disabled={submitting} />

      <div className="rounded-lg border border-zinc-200 dark:border-zinc-800 p-4 space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Formatos</label>
          <div className="flex flex-wrap gap-2">
            {FORMAT_OPTIONS.map((f) => (
              <button
                key={f}
                type="button"
                onClick={() => toggleFormat(f)}
                className={cn(
                  "px-3 py-1 rounded-full text-sm border transition",
                  formats.includes(f)
                    ? "bg-blue-500 text-white border-blue-500"
                    : "border-zinc-300 dark:border-zinc-700 hover:border-blue-400",
                )}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={merge}
            onChange={(e) => setMerge(e.target.checked)}
            className="rounded"
          />
          Mesclar em único documento
        </label>

        <div>
          <button
            type="button"
            onClick={() => setAdvancedOpen((v) => !v)}
            className="flex items-center gap-1 text-sm text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100"
          >
            {advancedOpen ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            Avançado
          </button>
          {advancedOpen && (
            <div className="mt-3 grid grid-cols-1 sm:grid-cols-3 gap-3">
              <label className="text-sm">
                <span className="block text-xs text-zinc-500 mb-1">OCR Engine</span>
                <input
                  value={ocrEngine}
                  onChange={(e) => setOcrEngine(e.target.value)}
                  placeholder="auto"
                  className="w-full rounded border border-zinc-300 dark:border-zinc-700 bg-transparent px-2 py-1 text-sm"
                />
              </label>
              <label className="text-sm">
                <span className="block text-xs text-zinc-500 mb-1">Idioma</span>
                <input
                  value={lang}
                  onChange={(e) => setLang(e.target.value)}
                  placeholder="por"
                  className="w-full rounded border border-zinc-300 dark:border-zinc-700 bg-transparent px-2 py-1 text-sm"
                />
              </label>
              <label className="text-sm">
                <span className="block text-xs text-zinc-500 mb-1">Device</span>
                <select
                  value={device}
                  onChange={(e) => setDevice(e.target.value)}
                  className="w-full rounded border border-zinc-300 dark:border-zinc-700 bg-transparent px-2 py-1 text-sm"
                >
                  <option value="cpu">cpu</option>
                  <option value="cuda">cuda</option>
                  <option value="mps">mps</option>
                </select>
              </label>
            </div>
          )}
        </div>
      </div>

      <button
        type="button"
        onClick={onSubmit}
        disabled={submitting || files.length === 0}
        className="inline-flex items-center gap-2 rounded-md bg-blue-500 hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-2 text-sm font-medium"
      >
        {submitting && <Spinner />}
        Iniciar
      </button>

      <div className="pt-6 mt-6 border-t border-zinc-200 dark:border-zinc-800 flex flex-wrap items-center gap-3 text-xs text-zinc-500">
        <span className="font-medium text-zinc-600 dark:text-zinc-400">Configurações</span>
        <EnablePush />
        <InstallPrompt />
      </div>
    </div>
  );
}
