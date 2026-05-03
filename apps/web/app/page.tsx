"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import {
  ChevronDown,
  ChevronRight,
  ScanLine,
  Sparkles,
  Shield,
  Zap,
  ArrowRight,
} from "lucide-react";
import { DropZone } from "@/components/DropZone";
import { Spinner } from "@/components/Spinner";
import { EnablePush } from "@/components/EnablePush";
import { InstallPrompt } from "@/components/InstallPrompt";
import { createJob } from "@/lib/api";
import { cn } from "@/lib/cn";

const FORMAT_OPTIONS = ["md", "docx", "pdf", "all"] as const;

const FEATURES = [
  { icon: ScanLine, label: "OCR Pt-BR", desc: "Extração otimizada" },
  { icon: Sparkles, label: "Layout fiel", desc: "Imagens preservadas" },
  { icon: Zap, label: "Local-first", desc: "Sem upload externo" },
  { icon: Shield, label: "Privado", desc: "Seus arquivos, suas regras" },
];

export default function HomePage() {
  const router = useRouter();
  const [files, setFiles] = useState<File[]>([]);
  const [formats, setFormats] = useState<string[]>(["md"]);
  const [merge, setMerge] = useState(false);
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [device, setDevice] = useState("auto");
  const [lang, setLang] = useState("pt,en");
  const [ocrEngine, setOcrEngine] = useState("easyocr");
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
    <div className="space-y-16">
      {/* Hero */}
      <section className="text-center space-y-6 pt-4">
        <p className="text-[10px] font-black uppercase tracking-[0.3em] text-cyan-500/70">
          Foto → Markdown estruturado
        </p>
        <h1 className="text-5xl sm:text-6xl font-black tracking-tighter leading-[0.95]">
          Digitalize livros e artigos
          <br />
          <span className="gradient-text">com qualidade editorial.</span>
        </h1>
        <p className="max-w-xl mx-auto text-slate-400 text-base leading-relaxed">
          Envie fotografias de páginas e receba Markdown limpo, com imagens preservadas
          e exportação opcional para DOCX e PDF.
        </p>

        {/* Features strip */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-3xl mx-auto pt-4">
          {FEATURES.map((feat) => (
            <div
              key={feat.label}
              className="glass rounded-2xl p-4 flex flex-col items-center text-center gap-1.5 card-stagger"
            >
              <feat.icon className="w-4 h-4 text-cyan-400" />
              <p className="text-[11px] font-bold uppercase tracking-widest text-slate-300">
                {feat.label}
              </p>
              <p className="text-[10px] text-slate-500">{feat.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Upload card */}
      <section className="max-w-2xl mx-auto space-y-6">
        <div className="glass rounded-3xl p-6 sm:p-8 space-y-6">
          <DropZone files={files} onChange={setFiles} disabled={submitting} />

          <div className="space-y-4">
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-widest text-slate-400 mb-2">
                Formato de saída
              </label>
              <div className="flex flex-wrap gap-2">
                {FORMAT_OPTIONS.map((f) => (
                  <button
                    key={f}
                    type="button"
                    onClick={() => toggleFormat(f)}
                    className={cn(
                      "px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider border transition-all",
                      formats.includes(f)
                        ? "bg-gradient-to-br from-cyan-500 to-teal-500 text-slate-950 border-transparent shadow-lg shadow-cyan-500/20"
                        : "border-white/10 text-slate-300 hover:border-cyan-500/40 hover:text-cyan-400",
                    )}
                  >
                    {f}
                  </button>
                ))}
              </div>
            </div>

            <label className="flex items-center gap-2.5 text-sm text-slate-300 cursor-pointer select-none">
              <input
                type="checkbox"
                checked={merge}
                onChange={(e) => setMerge(e.target.checked)}
                className="w-4 h-4 rounded border-white/10 bg-slate-900 accent-cyan-500"
              />
              Mesclar páginas em único documento
            </label>

            <div>
              <button
                type="button"
                onClick={() => setAdvancedOpen((v) => !v)}
                className="flex items-center gap-1 text-xs font-bold uppercase tracking-widest text-slate-400 hover:text-cyan-400 transition-colors"
              >
                {advancedOpen ? (
                  <ChevronDown className="h-3.5 w-3.5" />
                ) : (
                  <ChevronRight className="h-3.5 w-3.5" />
                )}
                Avançado
              </button>
              {advancedOpen && (
                <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <label className="text-sm">
                    <span className="block text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-1">
                      OCR Engine
                    </span>
                    <input
                      value={ocrEngine}
                      onChange={(e) => setOcrEngine(e.target.value)}
                      placeholder="auto"
                      className="w-full rounded-lg border border-white/10 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-600 focus:border-cyan-500/40 focus:outline-none"
                    />
                  </label>
                  <label className="text-sm">
                    <span className="block text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-1">
                      Idioma
                    </span>
                    <input
                      value={lang}
                      onChange={(e) => setLang(e.target.value)}
                      placeholder="por"
                      className="w-full rounded-lg border border-white/10 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-600 focus:border-cyan-500/40 focus:outline-none"
                    />
                  </label>
                  <label className="text-sm">
                    <span className="block text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-1">
                      Device
                    </span>
                    <select
                      value={device}
                      onChange={(e) => setDevice(e.target.value)}
                      className="w-full rounded-lg border border-white/10 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 focus:border-cyan-500/40 focus:outline-none"
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
            className="w-full inline-flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-br from-cyan-500 to-teal-500 hover:from-cyan-400 hover:to-teal-400 disabled:opacity-40 disabled:cursor-not-allowed text-slate-950 px-6 py-3.5 text-sm font-black uppercase tracking-widest shadow-lg shadow-cyan-500/20 transition-all"
          >
            {submitting ? <Spinner /> : <ArrowRight className="w-4 h-4" />}
            {submitting ? "Enviando..." : "Iniciar conversão"}
          </button>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-3 text-xs text-slate-500">
          <EnablePush />
          <InstallPrompt />
        </div>
      </section>
    </div>
  );
}
