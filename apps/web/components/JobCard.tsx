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
      className="block rounded-lg border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 p-4 hover:border-blue-400 transition"
    >
      <div className="flex items-start gap-3">
        <div className="w-16 h-16 rounded bg-zinc-100 dark:bg-zinc-800 overflow-hidden flex-shrink-0">
          {job.thumbnail ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={job.thumbnail} alt="" className="w-full h-full object-cover" />
          ) : null}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2">
            <h3 className="font-medium truncate text-sm">{job.title || job.id}</h3>
            <Star
              className={cn(
                "h-4 w-4 flex-shrink-0",
                job.is_favorite ? "fill-amber-400 text-amber-400" : "text-zinc-400",
              )}
            />
          </div>
          <div className="mt-1 flex items-center gap-2">
            <StatusBadge status={job.status} />
            <span className="text-xs text-zinc-500">{created}</span>
          </div>
          {(job.status === "running" || job.status === "queued") && (
            <ProgressBar value={job.progress} className="mt-2" />
          )}
        </div>
      </div>
    </Link>
  );
}
