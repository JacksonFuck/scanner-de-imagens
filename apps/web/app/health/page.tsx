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
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold">Health</h1>
      {loading && (
        <div className="flex items-center gap-2 text-sm text-zinc-500">
          <Spinner /> Verificando...
        </div>
      )}
      {error && <div className="text-sm text-red-600">Erro: {error}</div>}
      {data !== null && (
        <pre className="rounded-lg border border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-900 p-4 text-xs overflow-auto">
          {JSON.stringify(data, null, 2)}
        </pre>
      )}
    </div>
  );
}
