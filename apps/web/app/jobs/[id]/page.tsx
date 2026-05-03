"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Star, Trash2, Download, ArrowLeft } from "lucide-react";
import { toast } from "sonner";
import { StatusBadge } from "@/components/StatusBadge";
import { ProgressBar } from "@/components/ProgressBar";
import { Spinner } from "@/components/Spinner";
import { deleteJob, fileUrl, getJob, patchJob } from "@/lib/api";
import { connectJobWs } from "@/lib/ws";
import type { JobDetail, ProgressEvent } from "@/lib/types";
import { cn } from "@/lib/cn";

export default function JobDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const jobId = params?.id;

  const [job, setJob] = useState<JobDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [liveProgress, setLiveProgress] = useState<number | null>(null);
  const [liveMessage, setLiveMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;
    let cancelled = false;
    setLoading(true);
    getJob(jobId)
      .then((d) => {
        if (!cancelled) setJob(d);
      })
      .catch((e) => {
        if (!cancelled) setError((e as Error).message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [jobId]);

  useEffect(() => {
    if (!jobId || !job) return;
    if (job.status !== "running" && job.status !== "queued") return;

    const conn = connectJobWs(jobId, {
      onEvent: (ev: ProgressEvent) => {
        // Backend sends {type, current, total, ...} — derive a percentage.
        if (ev.type === "progress" && ev.current && ev.total) {
          setLiveProgress(Math.round((ev.current / ev.total) * 100));
          if (ev.current_file) setLiveMessage(`Processando ${ev.current_file}`);
        }
        // Terminal events: refetch the job to reflect new status/files.
        if (ev.type === "done" || ev.type === "error" || ev.type === "cancelled") {
          if (ev.message) setLiveMessage(ev.message);
          if (ev.type === "done") setLiveProgress(100);
          getJob(jobId).then(setJob).catch(() => {});
        }
      },
    });
    return () => conn.close();
  }, [jobId, job]);

  const handleFavorite = async () => {
    if (!job) return;
    try {
      const updated = await patchJob(job.id, { is_favorite: !job.is_favorite });
      setJob(updated);
    } catch (e) {
      toast.error(`Falha: ${(e as Error).message}`);
    }
  };

  // Backend serializes is_favorite as 0|1 — coerce for boolean styling.
  const fav = !!(job && job.is_favorite);

  const handleDelete = async () => {
    if (!job) return;
    if (!confirm("Deletar este job? Os arquivos serão removidos.")) return;
    try {
      await deleteJob(job.id);
      toast.success("Job removido");
      router.push("/jobs");
    } catch (e) {
      toast.error(`Falha: ${(e as Error).message}`);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-sm text-slate-500">
        <Spinner /> Carregando...
      </div>
    );
  }
  if (error)
    return (
      <div className="rounded-2xl border border-rose-500/20 bg-rose-500/10 text-rose-400 text-sm p-4">
        Erro: {error}
      </div>
    );
  if (!job) return <div className="text-sm text-slate-500">Job não encontrado.</div>;

  // Progress is only available via WebSocket while active; backend job model
  // doesn't persist a progress field. Default to 0 until first WS event.
  const progress = liveProgress ?? 0;
  const isActive = job.status === "running" || job.status === "queued";

  return (
    <div className="space-y-6">
      <button
        onClick={() => router.push("/jobs")}
        className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-widest text-slate-400 hover:text-cyan-400 transition-colors"
      >
        <ArrowLeft className="h-3.5 w-3.5" /> Voltar
      </button>

      <div className="glass rounded-3xl p-6 flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h1 className="text-2xl font-black tracking-tighter truncate">
            {job.title || job.id}
          </h1>
          <div className="mt-2 flex items-center gap-2 flex-wrap">
            <StatusBadge status={job.status} />
            <span className="text-[10px] font-mono text-slate-500">
              Criado · {new Date(job.created_at).toLocaleString()}
            </span>
          </div>
        </div>
        <div className="flex gap-2 flex-shrink-0">
          <button
            onClick={handleFavorite}
            className={cn(
              "p-2 rounded-xl border transition-all",
              fav
                ? "border-amber-400/40 bg-amber-500/10 text-amber-400"
                : "border-white/10 bg-slate-900/60 text-slate-400 hover:border-amber-400/40 hover:text-amber-400",
            )}
            aria-label="Favoritar"
          >
            <Star className={cn("h-4 w-4", fav && "fill-amber-400")} />
          </button>
          <button
            onClick={handleDelete}
            className="p-2 rounded-xl border border-white/10 bg-slate-900/60 text-slate-400 hover:border-rose-500/40 hover:text-rose-400 transition-all"
            aria-label="Deletar"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      {isActive && (
        <div className="glass rounded-2xl p-5 space-y-3 pulse-glow-active">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold uppercase tracking-widest text-slate-300">
              Progresso
            </span>
            <span className="text-xs font-mono text-cyan-400">{Math.round(progress)}%</span>
          </div>
          <ProgressBar value={progress} />
          {liveMessage && <p className="text-xs text-slate-500">{liveMessage}</p>}
        </div>
      )}

      {job.error_msg && (
        <div className="rounded-2xl border border-rose-500/20 bg-rose-500/10 p-4 text-sm text-rose-400">
          {job.error_msg}
        </div>
      )}

      <div>
        <h2 className="text-[11px] font-bold uppercase tracking-widest text-slate-400 mb-3">
          Arquivos
        </h2>
        {job.files.length === 0 ? (
          <p className="text-sm text-slate-500">Nenhum arquivo ainda.</p>
        ) : (
          <ul className="glass rounded-2xl divide-y divide-white/5 overflow-hidden">
            {job.files.map((f) => (
              <li
                key={f.filename}
                className="flex items-center justify-between gap-3 px-4 py-3 text-sm hover:bg-white/[0.02] transition-colors"
              >
                <div className="min-w-0">
                  <div className="truncate text-slate-200">{f.filename}</div>
                  <div className="text-[10px] font-mono text-slate-500 mt-0.5">
                    {f.role} · {(f.size_bytes / 1024).toFixed(1)} KB
                  </div>
                </div>
                <a
                  href={fileUrl(job.id, f.filename)}
                  download
                  className="inline-flex items-center gap-1.5 rounded-xl border border-white/10 bg-slate-900/60 px-3 py-1.5 text-[11px] font-bold uppercase tracking-widest text-cyan-400 hover:border-cyan-500/40 transition-colors"
                >
                  <Download className="h-3.5 w-3.5" /> Baixar
                </a>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
