"""SQLAlchemy ORM models — espelha spec Section 7.3.

3 tabelas:
- jobs: trabalho de OCR (1 por upload do usuário; pode conter N inputs)
- job_files: arquivos do job (inputs + outputs + imagens extraídas)
- push_subscriptions: subscrições Web Push (1 por dispositivo)

CheckConstraints inline garantem enums no nível do schema (defesa em profundidade
contra dados inválidos vindos via SQL direto).
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    """Base declarativa do scanner_api."""


class Job(Base):
    """Trabalho de OCR — agrupa N inputs e M outputs."""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # UUID4
    status: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    input_count: Mapped[int] = mapped_column(Integer, nullable=False)
    merge_mode: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    formats: Mapped[str] = mapped_column(String, nullable=False)
    advanced: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON serializado
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_favorite: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    error_msg: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    files: Mapped[list[JobFile]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('queued','running','done','error','cancelled')",
            name="jobs_status_valid",
        ),
        Index(
            "idx_jobs_expires_nonfav",
            "expires_at",
            sqlite_where=text("is_favorite = 0"),
        ),
        Index("idx_jobs_created_desc", "created_at"),
    )


class JobFile(Base):
    """Arquivo associado a um Job (input ou output ou imagem extraída)."""

    __tablename__ = "job_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String, nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    job: Mapped[Job] = relationship(back_populates="files")

    __table_args__ = (
        CheckConstraint(
            "role IN ('input','output_md','output_docx','output_pdf','image')",
            name="job_files_role_valid",
        ),
    )


class PushSubscription(Base):
    """Web Push subscription (browser/PWA, 1 por dispositivo)."""

    __tablename__ = "push_subscriptions"

    endpoint: Mapped[str] = mapped_column(String, primary_key=True)
    p256dh: Mapped[str] = mapped_column(String, nullable=False)
    auth: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )
    user_agent: Mapped[str | None] = mapped_column(String, nullable=True)
