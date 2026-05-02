import type { ProgressEvent } from "./types";

export interface WsHandlers {
  onEvent?: (ev: ProgressEvent) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (err: Event) => void;
}

export interface WsConnection {
  close: () => void;
}

function buildWsUrl(jobId: string): string {
  if (typeof window === "undefined") return "";
  const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${proto}//${window.location.host}/ws/jobs/${jobId}`;
}

export function connectJobWs(jobId: string, handlers: WsHandlers = {}): WsConnection {
  let ws: WebSocket | null = null;
  let stopped = false;
  let attempt = 0;
  let timer: ReturnType<typeof setTimeout> | null = null;

  const open = () => {
    if (stopped) return;
    const url = buildWsUrl(jobId);
    if (!url) return;
    ws = new WebSocket(url);
    ws.onopen = () => {
      attempt = 0;
      handlers.onOpen?.();
    };
    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data) as ProgressEvent;
        handlers.onEvent?.(data);
      } catch {
        /* ignore non-json */
      }
    };
    ws.onerror = (e) => handlers.onError?.(e);
    ws.onclose = () => {
      handlers.onClose?.();
      if (stopped) return;
      attempt += 1;
      const delay = Math.min(30000, 500 * 2 ** Math.min(attempt, 6));
      timer = setTimeout(open, delay);
    };
  };

  open();

  return {
    close: () => {
      stopped = true;
      if (timer) clearTimeout(timer);
      if (ws && ws.readyState <= 1) ws.close();
    },
  };
}
