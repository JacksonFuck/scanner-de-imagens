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
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Jobs</h1>
      </div>

      <div className="flex gap-1 border-b border-zinc-200 dark:border-zinc-800">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => {
              setTab(t.key);
              setPage(1);
            }}
            className={cn(
              "px-3 py-2 text-sm border-b-2 -mb-px transition",
              tab === t.key
                ? "border-blue-500 text-blue-600"
                : "border-transparent text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100",
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      {loading && (
        <div className="flex items-center gap-2 text-sm text-zinc-500">
          <Spinner /> Carregando...
        </div>
      )}
      {error && <div className="text-sm text-red-600">Erro: {error}</div>}

      {data && data.items.length === 0 && !loading && (
        <p className="text-sm text-zinc-500">Nenhum job encontrado.</p>
      )}

      {data && data.items.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {data.items.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      )}

      {data && data.total > PAGE_SIZE && (
        <div className="flex items-center justify-center gap-2 pt-4">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
            className="p-2 rounded border border-zinc-300 dark:border-zinc-700 disabled:opacity-50"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <span className="text-sm">
            {page} / {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
            className="p-2 rounded border border-zinc-300 dark:border-zinc-700 disabled:opacity-50"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      )}
    </div>
  );
}
