"""initial schema (jobs, job_files, push_subscriptions)

Revision ID: 0001
Revises:
Create Date: 2026-05-02

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Cria as 3 tabelas + 3 índices da Phase 1A."""
    # Table: jobs
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("input_count", sa.Integer(), nullable=False),
        sa.Column(
            "merge_mode",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("formats", sa.String(), nullable=False),
        sa.Column("advanced", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column(
            "is_favorite",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("error_msg", sa.Text(), nullable=True),
        sa.Column("page_count", sa.Integer(), nullable=True),
        sa.CheckConstraint(
            "status IN ('queued','running','done','error','cancelled')",
            name="jobs_status_valid",
        ),
    )
    op.create_index(
        "idx_jobs_expires_nonfav",
        "jobs",
        ["expires_at"],
        sqlite_where=sa.text("is_favorite = 0"),
    )
    op.create_index("idx_jobs_created_desc", "jobs", ["created_at"])

    # Table: job_files
    op.create_table(
        "job_files",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "job_id",
            sa.String(),
            sa.ForeignKey("jobs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "role IN ('input','output_md','output_docx','output_pdf','image')",
            name="job_files_role_valid",
        ),
    )
    op.create_index("ix_job_files_job_id", "job_files", ["job_id"])

    # Table: push_subscriptions
    op.create_table(
        "push_subscriptions",
        sa.Column("endpoint", sa.String(), primary_key=True),
        sa.Column("p256dh", sa.String(), nullable=False),
        sa.Column("auth", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column("user_agent", sa.String(), nullable=True),
    )


def downgrade() -> None:
    """Reverte as 3 tabelas (drop em ordem reversa do upgrade)."""
    op.drop_table("push_subscriptions")
    op.drop_index("ix_job_files_job_id", table_name="job_files")
    op.drop_table("job_files")
    op.drop_index("idx_jobs_created_desc", table_name="jobs")
    op.drop_index("idx_jobs_expires_nonfav", table_name="jobs")
    op.drop_table("jobs")
