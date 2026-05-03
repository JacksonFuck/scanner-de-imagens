import Link from "next/link";
import { Star } from "lucide-react";
import type { JobSummary } from "@/lib/types";
import { StatusBadge } from "./StatusBadge";
import { ProgressBar } from "./ProgressBar";
import { cn } from "@/lib/cn";

export function JobCard({ job }: { job: JobSummary }) {
  const created = new Date(job.created_at).toLocaleString();
  return (
    <Link
      href={`/jobs/${job.id}`}
      className={cn(
        "group block glass rounded-2xl p-4 transition-all hover:border-cyan-500/30 hover:-translate-y-0.5",
        (job.status === "running" || job.status === "queued") && "pulse-glow-active",
      )}
    >
      <div className="flex items-start gap-3">
        <div className="w-16 h-16 rounded-xl bg-slate-900/80 border border-white/5 overflow-hidden flex-shrink-0">
          {job.thumbnail ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={job.thumbnail} alt="" className="w-full h-full object-cover" />
          ) : null}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <h3 className="font-bold truncate text-sm text-slate-100 group-hover:text-cyan-400 transition-colors">
              {job.title || job.id}
            </h3>
            <Star
              className={cn(
                "h-4 w-4 flex-shrink-0",
                job.is_favorite ? "fill-amber-400 text-amber-400" : "text-slate-600",
              )}
            />
          </div>
          <div className="mt-1.5 flex items-center gap-2">
            <StatusBadge status={job.status} />
            <span className="text-[10px] font-mono text-slate-500">{created}</span>
          </div>
          {(job.status === "running" || job.status === "queued") && (
            <ProgressBar value={job.progress} className="mt-3" />
          )}
        </div>
      </div>
    </Link>
  );
}
