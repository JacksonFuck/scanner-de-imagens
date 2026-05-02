import type {
  CreateJobOptions,
  JobDetail,
  JobListFilters,
  JobListResponse,
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

export async function listJobs(filters: JobListFilters = {}): Promise<JobListResponse> {
  const params = new URLSearchParams();
  if (filters.favorite !== undefined) params.set("favorite", String(filters.favorite));
  if (filters.status) params.set("status", filters.status);
  if (filters.page) params.set("page", String(filters.page));
  if (filters.limit) params.set("limit", String(filters.limit));
  const qs = params.toString();
  const res = await fetch(`${BASE}/jobs${qs ? `?${qs}` : ""}`, { cache: "no-store" });
  return jsonOrThrow<JobListResponse>(res);
}

export async function getJob(id: string): Promise<JobDetail> {
  const res = await fetch(`${BASE}/jobs/${id}`, { cache: "no-store" });
  return jsonOrThrow<JobDetail>(res);
}

export async function createJob(opts: CreateJobOptions): Promise<JobDetail> {
  const fd = new FormData();
  for (const f of opts.files) fd.append("files", f);
  if (opts.formats) for (const fmt of opts.formats) fd.append("formats", fmt);
  if (opts.merge !== undefined) fd.append("merge", String(opts.merge));
  if (opts.device) fd.append("device", opts.device);
  if (opts.lang) fd.append("lang", opts.lang);
  if (opts.ocr_engine) fd.append("ocr_engine", opts.ocr_engine);
  const res = await fetch(`${BASE}/jobs`, { method: "POST", body: fd });
  return jsonOrThrow<JobDetail>(res);
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
