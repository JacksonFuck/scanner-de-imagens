import Link from "next/link";
import { Download, FileText, Star } from "lucide-react";
import type { JobSummary } from "@/lib/types";
import { jobZipUrl } from "@/lib/api";
import { StatusBadge } from "./StatusBadge";
import { cn } from "@/lib/cn";

export function JobCard({ job }: { job: JobSummary }) {
  const created = new Date(job.created_at).toLocaleString();
  const isActive = job.status === "running" || job.status === "queued";
  const isDone = job.status === "done";
  return (
    <div
      className={cn(
        "group relative glass rounded-2xl p-4 transition-all hover:border-cyan-500/30 hover:-translate-y-0.5",
        isActive && "pulse-glow-active",
      )}
    >
      <Link
        href={`/jobs/${job.id}`}
        className="absolute inset-0 z-0 rounded-2xl"
        aria-label={`Abrir ${job.title || job.id}`}
      />
      <div className="relative z-10 flex items-start gap-3 pointer-events-none">
        <div className="w-16 h-16 rounded-xl bg-slate-900/80 border border-white/5 flex items-center justify-center flex-shrink-0">
          <FileText className="h-7 w-7 text-slate-600 group-hover:text-cyan-500/70 transition-colors" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <h3 className="font-bold truncate text-sm text-slate-100 group-hover:text-cyan-400 transition-colors">
              {job.title || job.id}
            </h3>
            <div className="flex items-center gap-1.5 pointer-events-auto">
              {isDone && (
                <a
                  href={jobZipUrl(job.id)}
                  download
                  onClick={(e) => e.stopPropagation()}
                  className="inline-flex items-center gap-1 rounded-lg border border-cyan-500/30 bg-cyan-500/10 px-2 py-1 text-[10px] font-bold uppercase tracking-widest text-cyan-300 hover:bg-cyan-500/20 hover:text-cyan-100 transition"
                  aria-label="Baixar resultados (.zip)"
                  title="Baixar todos os arquivos gerados (ZIP)"
                >
                  <Download className="h-3 w-3" /> Baixar
                </a>
              )}
              <Star
                className={cn(
                  "h-4 w-4 flex-shrink-0",
                  job.is_favorite ? "fill-amber-400 text-amber-400" : "text-slate-600",
                )}
              />
            </div>
          </div>
          <div className="mt-1.5 flex items-center gap-2 flex-wrap">
            <StatusBadge status={job.status} />
            <span className="text-[10px] font-mono text-slate-500">
              {job.input_count} foto{job.input_count !== 1 ? "s" : ""} · {job.formats}
            </span>
          </div>
          <p className="mt-1 text-[10px] font-mono text-slate-600">{created}</p>
        </div>
      </div>
    </div>
  );
}
