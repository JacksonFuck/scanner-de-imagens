---
title: Arquitetura do Scanner de Imagens
tags: [scanner, arquitetura, moc]
created: 2026-05-02
updated: 2026-05-02
status: active
type: moc
---

# Arquitetura do Scanner de Imagens

> MOC (Map of Content) — ponto de entrada para entender o desenho técnico do projeto.

## Visão geral

Aplicação que recebe **fotografias de páginas de livros/artigos** e gera **Markdown estruturado**, com export opcional para **DOCX**. Preserva imagens e qualidade do conteúdo original.

## Pipeline conceitual

```
[fotos JPG/PNG]
      ↓ ingestão (upload / pasta watch)
[pré-processamento]
      ↓ deskew, denoise, contrast, dewarp
[OCR + layout detection]
      ↓ Docling (recomendado) ou OpenDataloader-PDF (via PDF intermediário)
[markdown estruturado]
      ↓ pós-processamento (tabelas, headings, links de imagens)
[output]
      ├→ .md (canônico)
      └→ .docx (via pandoc ou python-docx)
```

## Motor de extração: ✅ Docling

Decisão registrada em [[decisoes#motor-extracao]]. Source clonada em `docling-main/docling-main/` (raiz do projeto).

| Componente Docling | Uso planejado |
|--------------------|---------------|
| `backend/image_backend.py` | Entrada de fotos JPG/PNG |
| `backend/pypdfium2_backend.py` | Fallback para PDFs |
| `backend/msword_backend.py` | (futuro) input Word |
| OCR engine | EasyOCR/Tesseract/RapidOCR — a definir |
| `picture_classifier` | Preservar imagens dentro das páginas |

## Componentes esperados

- [[ingest-pipeline]] — recebe fotos
- [[preprocess]] — limpa imagem
- [[ocr-engine]] — extrai texto + layout
- [[markdown-renderer]] — gera `.md`
- [[docx-exporter]] — converte para Word
- [[image-store]] — guarda imagens originais referenciadas

## Stack

- **Linguagem**: Python 3.13
- **Engine principal**: Docling (fonte local em `docling-main/docling-main/`)
- **API web** (futura): FastAPI
- **Export DOCX**: pandoc CLI ou python-docx (a decidir — ver [[decisoes]])
- **Storage**: filesystem local + manifest JSON

## Links

- [[decisoes]]
- [[convencoes]]
- [[../pipeline/index]] (a criar)
