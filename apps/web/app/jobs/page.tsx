"use client";

import { useEffect, useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { JobCard } from "@/components/JobCard";
import { Spinner } from "@/components/Spinner";
import { listJobs } from "@/lib/api";
import { cn } from "@/lib/cn";
import type { JobListResponse, JobStatus } from "@/lib/types";

type Tab = "all" | "active" | "done" | "favorite";

const PAGE_SIZE = 20;

export default function JobsListPage() {
  const [tab, setTab] = useState<Tab>("all");
  const [page, setPage] = useState(1);
  const [data, setData] = useState<JobListResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    const filters: Parameters<typeof listJobs>[0] = { page, limit: PAGE_SIZE };
    if (tab === "favorite") filters.favorite = true;
    if (tab === "active") filters.status = "running" as JobStatus;
    if (tab === "done") filters.status = "done" as JobStatus;

    listJobs(filters)
      .then((d) => {
        if (!cancelled) setData(d);
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
  }, [tab, page]);

  const totalPages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;

  const TABS: { key: Tab; label: string }[] = [
    { key: "all", label: "Todos" },
    { key: "active", label: "Ativos" },
    { key: "done", label: "Concluídos" },
    { key: "favorite", label: "Favoritos" },
  ];

  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <p className="text-[10px] font-black uppercase tracking-[0.3em] text-cyan-500/70">
          Histórico
        </p>
        <h1 className="text-3xl font-black tracking-tighter">Jobs</h1>
      </div>

      <div className="flex flex-wrap gap-1 p-1 rounded-2xl glass w-fit">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => {
              setTab(t.key);
              setPage(1);
            }}
            className={cn(
              "px-4 py-1.5 text-[11px] font-bold uppercase tracking-widest rounded-xl transition-all",
              tab === t.key
                ? "bg-gradient-to-br from-cyan-500 to-teal-500 text-slate-950 shadow-lg shadow-cyan-500/20"
                : "text-slate-400 hover:text-slate-100 hover:bg-white/5",
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Spinner /> Carregando...
        </div>
      )}
      {error && (
        <div className="rounded-2xl border border-rose-500/20 bg-rose-500/10 text-rose-400 text-sm p-4">
          Erro: {error}
        </div>
      )}

      {data && data.items.length === 0 && !loading && (
        <div className="glass rounded-2xl p-8 text-center text-sm text-slate-500">
          Nenhum job encontrado.
        </div>
      )}

      {data && data.items.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {data.items.map((job) => (
            <div key={job.id} className="card-stagger">
              <JobCard job={job} />
            </div>
          ))}
        </div>
      )}

      {data && data.total > PAGE_SIZE && (
        <div className="flex items-center justify-center gap-3 pt-4">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
            className="p-2 rounded-xl border border-white/10 bg-slate-900/60 text-slate-300 hover:border-cyan-500/40 hover:text-cyan-400 transition disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <span className="text-xs font-mono text-slate-400">
            {page} / {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
            className="p-2 rounded-xl border border-white/10 bg-slate-900/60 text-slate-300 hover:border-cyan-500/40 hover:text-cyan-400 transition disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  );
}
