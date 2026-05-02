import { cn } from "@/lib/cn";
import type { JobStatus } from "@/lib/types";

const STYLES: Record<JobStatus, string> = {
  queued: "bg-zinc-200 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300",
  running: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  done: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300",
  failed: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  canceled: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
};

export function StatusBadge({ status, className }: { status: JobStatus; className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium",
        STYLES[status],
        className,
      )}
    >
      {status}
    </span>
  );
}
