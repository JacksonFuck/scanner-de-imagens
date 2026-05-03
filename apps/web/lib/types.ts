export type JobStatus = "queued" | "running" | "done" | "failed" | "canceled";

export type FileKind = "input" | "output" | "thumbnail" | "log";

export interface JobFile {
  filename: string;
  kind: FileKind | string;
  size_bytes: number;
}

export interface JobSummary {
  id: string;
  title: string;
  status: JobStatus;
  progress: number;
  created_at: string;
  is_favorite: boolean;
  thumbnail?: string | null;
}

export interface JobDetail extends JobSummary {
  files: JobFile[];
  started_at?: string | null;
  completed_at?: string | null;
  error?: string | null;
}

export interface JobListResponse {
  items: JobSummary[];
  total: number;
  page: number;
  limit: number;
}

export interface ProgressEvent {
  type: "progress" | "status" | "message";
  progress?: number;
  status?: JobStatus;
  message?: string;
  ts?: string;
}

export interface JobListFilters {
  favorite?: boolean;
  status?: JobStatus;
  page?: number;
  limit?: number;
}

export interface CreateJobOptions {
  files: File[];
  formats?: string[];
  merge?: boolean;
  device?: string;
  lang?: string;
  ocr_engine?: string;
}

export interface JobCreated {
  id: string;
  status: JobStatus;
}

export interface PatchJobBody {
  is_favorite?: boolean;
  title?: string;
}
