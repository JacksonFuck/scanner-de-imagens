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
          "border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition",
          isDragActive
            ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
            : "border-zinc-300 dark:border-zinc-700 hover:border-blue-400",
          disabled && "opacity-50 pointer-events-none",
        )}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-8 w-8 text-zinc-400" />
        <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">
          {isDragActive ? "Solte aqui..." : "Arraste fotos ou PDFs, ou clique para selecionar"}
        </p>
      </div>

      {files.length > 0 && (
        <ul className="space-y-2">
          {files.map((f, i) => (
            <li
              key={`${f.name}-${i}`}
              className="flex items-center justify-between gap-2 rounded border border-zinc-200 dark:border-zinc-800 px-3 py-2 text-sm"
            >
              <span className="truncate flex-1">{f.name}</span>
              <span className="text-xs text-zinc-500">{(f.size / 1024).toFixed(1)} KB</span>
              <button
                type="button"
                onClick={() => remove(i)}
                className="text-zinc-400 hover:text-red-500"
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
