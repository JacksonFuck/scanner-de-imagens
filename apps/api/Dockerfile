# syntax=docker/dockerfile:1.7

FROM python:3.13-slim AS base

# Dependências de sistema:
# - pandoc + texlive-xetex: PDF export (Phase 0)
# - tesseract-ocr-por: OCR fallback PT-BR (engine alternativo do Docling)
# - libgl1, libglib2.0-0: dependências transitivas do Docling/OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    pandoc \
    texlive-xetex \
    texlive-fonts-recommended \
    texlive-lang-portuguese \
    tesseract-ocr \
    tesseract-ocr-por \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia o monorepo: scanner core (src/) + api (apps/api/) + pyproject root.
# README.md é referenciado por hatchling — copiamos o suficiente para os builds.
COPY pyproject.toml README.md ./
COPY src ./src
COPY apps/api ./apps/api

# Instala scanner core (editável) + api (editável).
# Ordem importa: api depende do scanner core via import.
RUN pip install --no-cache-dir -e . \
    && pip install --no-cache-dir -e ./apps/api

# Pasta padrão de dados — montada como volume em produção
ENV SCANNER_DATA_DIR=/data
RUN mkdir -p /data/jobs

EXPOSE 8000

CMD ["uvicorn", "scanner_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
