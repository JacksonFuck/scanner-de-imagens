-- Schema canônico do scanner_api (referência humana — espelha db/models.py).
-- Migrações reais são geridas pelo Alembic (db/migrations/versions/).
-- Útil para debug via `sqlite3 scanner.db` e onboarding sem ler SQLAlchemy.

CREATE TABLE jobs (
  id           TEXT PRIMARY KEY,                          -- UUID4
  status       TEXT NOT NULL CHECK(status IN ('queued','running','done','error','cancelled')),
  title        TEXT,
  input_count  INTEGER NOT NULL,
  merge_mode   INTEGER NOT NULL DEFAULT 0,                -- 0=separados, 1=merge
  formats      TEXT NOT NULL,                             -- 'md' | 'docx' | 'pdf' | 'all'
  advanced     TEXT,                                      -- JSON: ocr_engine, ocr_lang, etc.
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  finished_at  TIMESTAMP,
  expires_at   TIMESTAMP,                                 -- created_at + 72h, NULL se favorito
  is_favorite  INTEGER NOT NULL DEFAULT 0,
  error_msg    TEXT,
  page_count   INTEGER
);

CREATE TABLE job_files (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id      TEXT NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
  role        TEXT NOT NULL CHECK(role IN ('input','output_md','output_docx','output_pdf','image')),
  filename    TEXT NOT NULL,
  size_bytes  INTEGER NOT NULL
);

CREATE TABLE push_subscriptions (
  endpoint    TEXT PRIMARY KEY,
  p256dh      TEXT NOT NULL,
  auth        TEXT NOT NULL,
  created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  user_agent  TEXT
);

-- Índices

CREATE INDEX idx_jobs_expires_nonfav ON jobs(expires_at) WHERE is_favorite = 0;
CREATE INDEX idx_jobs_created_desc ON jobs(created_at);
CREATE INDEX ix_job_files_job_id ON job_files(job_id);
