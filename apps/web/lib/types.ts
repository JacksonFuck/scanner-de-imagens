export type JobStatus = "queued" | "running" | "done" | "failed" | "canceled";

export type FileRole = "input" | "output" | "thumbnail" | "log";

export interface JobFile {
  filename: string;
  role: FileRole | string;
  size_bytes: number;
}

export interface JobSummary {
  id: string;
  status: JobStatus;
  title: string | null;
  input_count: number;
  formats: string;
  created_at: string;
  is_favorite: number; // backend serializes SQLite Integer as 0|1
}

export interface JobDetail extends JobSummary {
  merge_mode: number;
  finished_at: string | null;
  error_msg: string | null;
  page_count: number | null;
  files: JobFile[];
}

export interface ProgressEvent {
  // Backend emits one of: 'started' | 'progress' | 'done' | 'error' | 'cancelled'.
  type: "started" | "progress" | "done" | "error" | "cancelled" | string;
  ts?: number;
  // 'started' includes input_count
  input_count?: number;
  // 'progress' includes the file index (1-based) within the batch
  current?: number;
  total?: number;
  current_file?: string;
  // 'done'/'error' include
  page_count?: number;
  message?: string;
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
