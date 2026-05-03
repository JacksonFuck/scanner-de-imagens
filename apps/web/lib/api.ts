import type {
  CreateJobOptions,
  JobCreated,
  JobDetail,
  JobListFilters,
  JobStatus,
  JobSummary,
  PatchJobBody,
} from "./types";

const BASE = "/api";

async function jsonOrThrow<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let msg = `HTTP ${res.status}`;
    try {
      const data = await res.json();
      if (data?.detail) msg = `${msg}: ${typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail)}`;
    } catch {
      /* ignore */
    }
    throw new Error(msg);
  }
  return (await res.json()) as T;
}

export async function getHealth(): Promise<Record<string, unknown>> {
  const res = await fetch(`${BASE}/health`, { cache: "no-store" });
  return jsonOrThrow(res);
}

export async function listJobs(filters: JobListFilters = {}): Promise<JobSummary[]> {
  const params = new URLSearchParams();
  if (filters.favorite !== undefined) params.set("favorite", String(filters.favorite));
  if (filters.status) params.set("status", filters.status);
  if (filters.page) params.set("page", String(filters.page));
  if (filters.limit) params.set("limit", String(filters.limit));
  const qs = params.toString();
  const res = await fetch(`${BASE}/jobs${qs ? `?${qs}` : ""}`, { cache: "no-store" });
  // Backend returns a plain array (not wrapped). Defensive: accept either.
  const raw = await jsonOrThrow<JobSummary[] | { items: JobSummary[] }>(res);
  return Array.isArray(raw) ? raw : raw.items ?? [];
}

export async function getJob(id: string): Promise<JobDetail> {
  const res = await fetch(`${BASE}/jobs/${id}`, { cache: "no-store" });
  return jsonOrThrow<JobDetail>(res);
}

export async function createJob(opts: CreateJobOptions): Promise<JobCreated> {
  const fd = new FormData();
  for (const f of opts.files) fd.append("files", f);

  // Backend espera 'formats' como string única ('md'|'docx'|'pdf'|'all'|'both').
  // Quando o usuário marca múltiplos formatos no UI, mandamos 'all'.
  const fmts = opts.formats ?? ["md"];
  const formatStr = fmts.length > 1 ? "all" : fmts[0];
  fd.append("formats", formatStr);

  if (opts.merge !== undefined) fd.append("merge", String(opts.merge));

  // Backend espera 'advanced' como JSON (JobAdvancedOptions). Embrulha as
  // opções avançadas — só envia se o usuário customizou pelo menos uma.
  const advanced: Record<string, string> = {};
  if (opts.device) advanced.device = opts.device;
  if (opts.lang) advanced.ocr_lang = opts.lang;
  if (opts.ocr_engine) advanced.ocr_engine = opts.ocr_engine;
  if (Object.keys(advanced).length > 0) {
    fd.append("advanced", JSON.stringify(advanced));
  }

  const res = await fetch(`${BASE}/jobs`, { method: "POST", body: fd });
  // Backend retorna { job_id, status } — mapeia para o shape do frontend.
  const raw = await jsonOrThrow<{ job_id: string; status: JobStatus }>(res);
  return { id: raw.job_id, status: raw.status };
}

export async function patchJob(id: string, body: PatchJobBody): Promise<JobDetail> {
  const res = await fetch(`${BASE}/jobs/${id}`, {
    method: "PATCH",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  return jsonOrThrow<JobDetail>(res);
}

export async function deleteJob(id: string): Promise<void> {
  const res = await fetch(`${BASE}/jobs/${id}`, { method: "DELETE" });
  if (!res.ok && res.status !== 204) throw new Error(`HTTP ${res.status}`);
}

export function fileUrl(id: string, filename: string): string {
  return `${BASE}/jobs/${id}/files/${encodeURIComponent(filename)}`;
}

export function jobZipUrl(id: string): string {
  return `${BASE}/jobs/${id}/download`;
}
