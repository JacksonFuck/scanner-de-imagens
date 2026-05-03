"use client";

import { useDropzone } from "react-dropzone";
import { Upload, X } from "lucide-react";
import { useCallback } from "react";
import { cn } from "@/lib/cn";

interface Props {
  files: File[];
  onChange: (files: File[]) => void;
  disabled?: boolean;
}

export function DropZone({ files, onChange, disabled }: Props) {
  const onDrop = useCallback(
    (accepted: File[]) => {
      onChange([...files, ...accepted]);
    },
    [files, onChange],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [], "application/pdf": [".pdf"] },
    disabled,
  });

  const remove = (idx: number) => {
    const next = files.slice();
    next.splice(idx, 1);
    onChange(next);
  };

  return (
    <div className="space-y-3">
      <div
        {...getRootProps()}
        className={cn(
          "relative border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all overflow-hidden group",
          isDragActive
            ? "border-cyan-400 bg-cyan-500/5 glow-box"
            : "border-white/10 hover:border-cyan-500/40 hover:bg-white/[0.02]",
          disabled && "opacity-50 pointer-events-none",
        )}
      >
        <input {...getInputProps()} />
        <div
          className={cn(
            "mx-auto mb-3 w-12 h-12 rounded-2xl flex items-center justify-center transition-all",
            isDragActive
              ? "bg-gradient-to-br from-cyan-500 to-teal-500 scale-110"
              : "bg-slate-900/80 border border-white/5 group-hover:border-cyan-500/30",
          )}
        >
          <Upload
            className={cn(
              "h-5 w-5 transition-colors",
              isDragActive ? "text-slate-950" : "text-cyan-400",
            )}
          />
        </div>
        <p className="text-sm font-semibold text-slate-200">
          {isDragActive ? "Solte aqui..." : "Arraste fotos ou PDFs"}
        </p>
        <p className="mt-1 text-xs text-slate-500">ou clique para selecionar</p>
      </div>

      {files.length > 0 && (
        <ul className="space-y-2">
          {files.map((f, i) => (
            <li
              key={`${f.name}-${i}`}
              className="flex items-center justify-between gap-2 rounded-xl border border-white/5 bg-slate-950/40 px-4 py-2.5 text-sm card-stagger"
            >
              <span className="truncate flex-1 text-slate-200">{f.name}</span>
              <span className="text-[10px] font-mono text-slate-500">
                {(f.size / 1024).toFixed(1)} KB
              </span>
              <button
                type="button"
                onClick={() => remove(i)}
                className="text-slate-500 hover:text-rose-400 transition-colors"
                aria-label="Remover"
              >
                <X className="h-4 w-4" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
