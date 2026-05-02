"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Bell, BellOff } from "lucide-react";

type PermissionState = "default" | "granted" | "denied" | "unsupported";

function urlBase64ToUint8Array(base64String: string): Uint8Array<ArrayBuffer> {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const rawData = atob(base64);
  const buffer = new ArrayBuffer(rawData.length);
  const output = new Uint8Array(buffer);
  for (let i = 0; i < rawData.length; ++i) output[i] = rawData.charCodeAt(i);
  return output;
}

export function EnablePush() {
  const [permission, setPermission] = useState<PermissionState>("default");
  const [subscribed, setSubscribed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (!("Notification" in window) || !("serviceWorker" in navigator) || !("PushManager" in window)) {
      setPermission("unsupported");
      return;
    }
    setPermission(Notification.permission as PermissionState);

    navigator.serviceWorker.ready
      .then((reg) => reg.pushManager.getSubscription())
      .then((sub) => setSubscribed(!!sub))
      .catch(() => {
        /* ignore */
      });
  }, []);

  const enable = async () => {
    setError(null);
    setLoading(true);
    try {
      const result = await Notification.requestPermission();
      setPermission(result as PermissionState);
      if (result !== "granted") {
        throw new Error("Permissão negada");
      }

      const registration = await navigator.serviceWorker.ready;

      const keyRes = await fetch("/api/push/vapid-public-key");
      if (!keyRes.ok) throw new Error(`vapid key HTTP ${keyRes.status}`);
      const { public_key: publicKey } = (await keyRes.json()) as { public_key: string };
      if (!publicKey) throw new Error("VAPID public key ausente");

      const sub = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(publicKey),
      });

      const json = sub.toJSON() as {
        endpoint?: string;
        keys?: { p256dh?: string; auth?: string };
      };
      const subRes = await fetch("/api/push/subscribe", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          endpoint: json.endpoint,
          keys: { p256dh: json.keys?.p256dh, auth: json.keys?.auth },
        }),
      });
      if (!subRes.ok) throw new Error(`subscribe HTTP ${subRes.status}`);

      setSubscribed(true);
      toast.success("Notificações ativadas");
    } catch (err) {
      const msg = (err as Error).message;
      setError(msg);
      toast.error(`Falha ao ativar: ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  const disable = async () => {
    setError(null);
    setLoading(true);
    try {
      const registration = await navigator.serviceWorker.ready;
      const sub = await registration.pushManager.getSubscription();
      if (sub) {
        await fetch("/api/push/unsubscribe", {
          method: "DELETE",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ endpoint: sub.endpoint }),
        }).catch(() => {});
        await sub.unsubscribe();
      }
      setSubscribed(false);
      toast.success("Notificações desativadas");
    } catch (err) {
      const msg = (err as Error).message;
      setError(msg);
      toast.error(`Falha ao desativar: ${msg}`);
    } finally {
      setLoading(false);
    }
  };

  if (permission === "unsupported") {
    return (
      <div className="text-xs text-zinc-500">
        Notificações não suportadas neste navegador.
      </div>
    );
  }

  if (permission === "denied") {
    return (
      <div className="text-xs text-zinc-500">
        Notificações bloqueadas. Habilite nas configurações do navegador.
      </div>
    );
  }

  return (
    <div className="flex items-center gap-3 text-sm">
      {subscribed ? (
        <button
          type="button"
          onClick={disable}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-md border border-zinc-300 dark:border-zinc-700 px-3 py-1.5 text-xs hover:bg-zinc-50 dark:hover:bg-zinc-900 disabled:opacity-50"
        >
          <BellOff className="h-3.5 w-3.5" />
          Desativar notificações
        </button>
      ) : (
        <button
          type="button"
          onClick={enable}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-md border border-zinc-300 dark:border-zinc-700 px-3 py-1.5 text-xs hover:bg-zinc-50 dark:hover:bg-zinc-900 disabled:opacity-50"
        >
          <Bell className="h-3.5 w-3.5" />
          {loading ? "Ativando..." : "Ativar notificações"}
        </button>
      )}
      {error && <span className="text-xs text-red-500">{error}</span>}
    </div>
  );
}
