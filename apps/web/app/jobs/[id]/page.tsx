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
        if (ev.progress !== undefined) setLiveProgress(ev.progress);
        if (ev.message) setLiveMessage(ev.message);
        if (ev.status && ev.status !== job.status) {
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
      <div className="flex items-center gap-2 text-sm text-zinc-500">
        <Spinner /> Carregando...
      </div>
    );
  }
  if (error) return <div className="text-red-600 text-sm">Erro: {error}</div>;
  if (!job) return <div className="text-sm text-zinc-500">Job não encontrado.</div>;

  const progress = liveProgress ?? job.progress;
  const isActive = job.status === "running" || job.status === "queued";

  return (
    <div className="space-y-6">
      <button
        onClick={() => router.push("/jobs")}
        className="inline-flex items-center gap-1 text-sm text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100"
      >
        <ArrowLeft className="h-4 w-4" /> Voltar
      </button>

      <div className="flex items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold">{job.title || job.id}</h1>
          <div className="mt-2 flex items-center gap-2">
            <StatusBadge status={job.status} />
            <span className="text-xs text-zinc-500">
              Criado: {new Date(job.created_at).toLocaleString()}
            </span>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleFavorite}
            className={cn(
              "p-2 rounded border border-zinc-300 dark:border-zinc-700",
              job.is_favorite && "bg-amber-50 dark:bg-amber-900/20 border-amber-400",
            )}
            aria-label="Favoritar"
          >
            <Star className={cn("h-4 w-4", job.is_favorite && "fill-amber-400 text-amber-400")} />
          </button>
          <button
            onClick={handleDelete}
            className="p-2 rounded border border-zinc-300 dark:border-zinc-700 hover:border-red-400 hover:text-red-500"
            aria-label="Deletar"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>

      {isActive && (
        <div className="rounded-lg border border-zinc-200 dark:border-zinc-800 p-4 space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span>Progresso</span>
            <span className="text-zinc-500">{Math.round(progress)}%</span>
          </div>
          <ProgressBar value={progress} />
          {liveMessage && <p className="text-xs text-zinc-500">{liveMessage}</p>}
        </div>
      )}

      {job.error && (
        <div className="rounded-lg border border-red-300 dark:border-red-800 bg-red-50 dark:bg-red-900/20 p-3 text-sm text-red-700 dark:text-red-300">
          {job.error}
        </div>
      )}

      <div>
        <h2 className="text-sm font-medium mb-2">Arquivos</h2>
        {job.files.length === 0 ? (
          <p className="text-sm text-zinc-500">Nenhum arquivo ainda.</p>
        ) : (
          <ul className="divide-y divide-zinc-200 dark:divide-zinc-800 rounded-lg border border-zinc-200 dark:border-zinc-800">
            {job.files.map((f) => (
              <li key={f.filename} className="flex items-center justify-between gap-3 px-3 py-2 text-sm">
                <div className="min-w-0">
                  <div className="truncate">{f.filename}</div>
                  <div className="text-xs text-zinc-500">
                    {f.kind} · {(f.size_bytes / 1024).toFixed(1)} KB
                  </div>
                </div>
                <a
                  href={fileUrl(job.id, f.filename)}
                  download
                  className="inline-flex items-center gap-1 text-blue-600 hover:underline"
                >
                  <Download className="h-4 w-4" /> Baixar
                </a>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
