import { cn } from "@/lib/cn";
import type { JobStatus } from "@/lib/types";

const STYLES: Record<JobStatus, string> = {
  queued: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  running: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
  done: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  failed: "bg-rose-500/10 text-rose-400 border-rose-500/20",
  canceled: "bg-slate-500/10 text-slate-400 border-slate-500/20",
};

export function StatusBadge({ status, className }: { status: JobStatus; className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-widest border",
        STYLES[status],
        className,
      )}
    >
      {status}
    </span>
  );
}
