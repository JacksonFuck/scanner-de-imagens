import { cn } from "@/lib/cn";

export function ProgressBar({ value, className }: { value: number; className?: string }) {
  const pct = Math.max(0, Math.min(100, value));
  return (
    <div className={cn("w-full h-2 rounded-full bg-zinc-200 dark:bg-zinc-800 overflow-hidden", className)}>
      <div
        className="h-full bg-blue-500 transition-all duration-300"
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}
