"use client";

import { useEffect, useState } from "react";
import { getHealth } from "@/lib/api";
import { Spinner } from "@/components/Spinner";

export default function HealthPage() {
  const [data, setData] = useState<unknown>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getHealth()
      .then(setData)
      .catch((e) => setError((e as Error).message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="space-y-1">
        <p className="text-[10px] font-black uppercase tracking-[0.3em] text-cyan-500/70">
          Diagnóstico
        </p>
        <h1 className="text-3xl font-black tracking-tighter">Health</h1>
      </div>
      {loading && (
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Spinner /> Verificando...
        </div>
      )}
      {error && (
        <div className="rounded-2xl border border-rose-500/20 bg-rose-500/10 text-rose-400 text-sm p-4">
          Erro: {error}
        </div>
      )}
      {data !== null && (
        <pre className="glass rounded-2xl p-5 text-xs font-mono text-slate-300 overflow-auto custom-scrollbar">
          {JSON.stringify(data, null, 2)}
        </pre>
      )}
    </div>
  );
}
