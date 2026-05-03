import { cn } from "@/lib/cn";

export function ProgressBar({ value, className }: { value: number; className?: string }) {
  const pct = Math.max(0, Math.min(100, value));
  return (
    <div
      className={cn(
        "w-full h-1.5 rounded-full bg-slate-900/80 border border-white/5 overflow-hidden",
        className,
      )}
    >
      <div
        className="h-full bg-gradient-to-r from-cyan-500 via-teal-500 to-emerald-500 transition-all duration-500 shadow-[0_0_12px_rgba(34,211,238,0.4)]"
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}
