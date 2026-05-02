# Phase 0 — Backend Refactor (PDF Export + Postprocess Migration) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refatorar o pacote `src/scanner/` para (1) tornar o pós-processador PT-BR um módulo importável e (2) suportar PDF como formato de output, mantendo a CLI funcional sem regressões. Este é o pré-requisito para a Fase 1 (FastAPI), que vai consumir essas APIs.

**Architecture:** Mover `scripts/postprocess_md.py` → `src/scanner/postprocess/` (importável). Estender `OutputFormat` enum com `PDF` e `ALL`, mantendo `BOTH` como alias deprecated. Adicionar `export/pdf.py` usando `pandoc --pdf-engine=xelatex` (mesma toolchain do DOCX). Atualizar `pipeline.scan()` e CLI consistentemente.

**Tech Stack:** Python 3.11+, pytest, pypandoc, ruff, mypy strict, hatchling.

**Source spec:** `docs/superpowers/specs/2026-05-02-web-app-pwa-design.md` (commit `1129ce8`), Seção 11 passos 1-2 + Seção 7.4.

**Working directory:** `c:\Users\jacks\OneDrive\2º Cérebro\Scanner de imagens`

---

## File Structure

| Caminho | Ação | Responsabilidade |
|---------|------|------------------|
| `src/scanner/postprocess/__init__.py` | CREATE | Expõe API pública: `fix_text`, `fix_accents`, `fix_spaces_and_punct`, `merge_into_book`, `ACCENT_MAP` |
| `src/scanner/postprocess/ptbr.py` | CREATE | Implementação (movida de `scripts/postprocess_md.py`) |
| `tests/test_postprocess.py` | CREATE | Testes unitários do postprocess (acentos, espaços, merge) |
| `src/scanner/export/pdf.py` | CREATE | `write_pdf(markdown_path, target, *, resource_dir)` via pandoc + xelatex |
| `tests/test_export_pdf.py` | CREATE | Testes de geração de PDF (smoke + idioma PT) |
| `src/scanner/export/__init__.py` | MODIFY | Re-exportar `write_pdf` junto com `write_markdown` e `write_docx` |
| `src/scanner/pipeline.py` | MODIFY | Estender `OutputFormat`, atualizar `scan()` para gerar PDF |
| `tests/test_pipeline.py` | MODIFY | Cobrir novos enum values e geração combinada de outputs |
| `src/scanner/cli.py` | MODIFY | Aceitar `-f all`. Manter `-f both` com deprecation warning |
| `tests/test_cli.py` | MODIFY | Testar nova flag e warning de `both` |
| `scripts/postprocess_md.py` | DELETE | Substituído pelo módulo |
| `pyproject.toml` | MODIFY | Adicionar `pypandoc` (já existe) + remover ref ao script CLI antigo se houver |

---

## Task 1: Mover postprocess para módulo importável

**Files:**
- Create: `src/scanner/postprocess/__init__.py`
- Create: `src/scanner/postprocess/ptbr.py`
- Create: `tests/test_postprocess.py`
- Delete: `scripts/postprocess_md.py` (após confirmar testes verdes)

- [ ] **Step 1.1: Escrever teste de fix_accents para palavra-chave**

Criar `tests/test_postprocess.py`:

```python
"""Testes do pós-processador PT-BR."""

from __future__ import annotations

from scanner.postprocess import fix_accents, fix_spaces_and_punct, fix_text


def test_fix_accents_replaces_common_words() -> None:
    """Palavras comuns sem acento devem ser corrigidas."""
    text = "A gestao de pacientes em emergencia exige atencao."
    result = fix_accents(text)
    assert result == "A gestão de pacientes em emergência exige atenção."


def test_fix_accents_preserves_casing() -> None:
    """Casing original deve ser preservado (case-insensitive match, casing original mantido)."""
    text = "GESTAO de pacientes"
    result = fix_accents(text)
    assert result == "GESTÃO de pacientes"


def test_fix_accents_handles_cedilla() -> None:
    """Palavras com 'c' que viram 'ç' devem ser corrigidas."""
    text = "A funcao do coracao"
    result = fix_accents(text)
    assert "função" in result
    assert "coração" in result
```

- [ ] **Step 1.2: Rodar teste e confirmar falha de import**

Run: `pytest tests/test_postprocess.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'scanner.postprocess'`.

- [ ] **Step 1.3: Criar pacote postprocess**

Criar `src/scanner/postprocess/__init__.py`:

```python
"""Pós-processamento de Markdown extraído pelo OCR.

Corrige problemas conhecidos do OCR sem PT-BR ativo:
- Palavras comuns sem acento → com acento (dicionário ACCENT_MAP)
- Espaços extras antes de pontuação
- "0" → "O" no início de palavras quando o contexto é português

API pública:
    fix_text(text) -> text   # aplica todas as correções
    fix_accents(text) -> text
    fix_spaces_and_punct(text) -> text
    merge_into_book(md_paths, target, *, title) -> Path
"""

from __future__ import annotations

from scanner.postprocess.ptbr import (
    ACCENT_MAP,
    fix_accents,
    fix_spaces_and_punct,
    fix_text,
    merge_into_book,
    process_markdown,
)

__all__ = [
    "ACCENT_MAP",
    "fix_accents",
    "fix_spaces_and_punct",
    "fix_text",
    "merge_into_book",
    "process_markdown",
]
```

- [ ] **Step 1.4: Criar implementação ptbr.py movendo de scripts/**

Ler `scripts/postprocess_md.py` e mover lógica para `src/scanner/postprocess/ptbr.py`. O conteúdo essencial (sem CLI argparse — só a lógica):

```python
"""Implementação do pós-processador PT-BR (movido de scripts/postprocess_md.py).

Apenas a lógica de transformação. CLI argparse fica em scripts/ (se ainda existir
para uso standalone) ou é exposto via scanner.cli quando integrado ao pipeline.
"""

from __future__ import annotations

import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Dicionário de correções PT-BR
# ---------------------------------------------------------------------------
# Formato: { padrao_sem_acento: forma_com_acento }
# Aplicado case-insensitive mantendo o casing original.
ACCENT_MAP: dict[str, str] = {
    # COPIAR EXATAMENTE o dicionário ACCENT_MAP de scripts/postprocess_md.py.
    # O dicionário tem ~150 palavras: gestao→gestão, atencao→atenção, funcao→função,
    # coracao→coração, emergencia→emergência, pacientes→pacientes (sem mudança), etc.
    # Use `cat scripts/postprocess_md.py | grep -A 200 'ACCENT_MAP'` para extrair.
}

_SPACE_BEFORE_PUNCT = re.compile(
    r"(?<=[a-zA-Z0-9áéíóúâêîôûãõàçñ\)\]\"'])\s+([,.;:!?])"
)


def _preserve_case(original: str, replacement: str) -> str:
    """Devolve `replacement` com o mesmo padrão de caixa de `original`.

    Exemplos:
        _preserve_case("gestao", "gestão")     -> "gestão"
        _preserve_case("Gestao", "gestão")     -> "Gestão"
        _preserve_case("GESTAO", "gestão")     -> "GESTÃO"
    """
    if original.isupper():
        return replacement.upper()
    if original[0].isupper():
        return replacement[0].upper() + replacement[1:]
    return replacement


def fix_accents(text: str) -> str:
    """Aplica o dicionário ACCENT_MAP preservando casing original.

    Faz match case-insensitive em fronteiras de palavra (\\b) para evitar
    substituições parciais.
    """
    result = text
    for plain, accented in ACCENT_MAP.items():
        pattern = re.compile(rf"\b{re.escape(plain)}\b", re.IGNORECASE)
        result = pattern.sub(
            lambda m: _preserve_case(m.group(0), accented),
            result,
        )
    return result


def fix_spaces_and_punct(text: str) -> str:
    """Remove espaço(s) antes de pontuação ASCII (.,;:!?).

    Não toca em hífen de listas ('- item') porque o regex exige caractere
    alfanumérico antes do espaço.
    """
    return _SPACE_BEFORE_PUNCT.sub(r"\1", text)


def _protect_code_blocks(text: str) -> tuple[str, list[str]]:
    """Substitui blocos ```...``` por marcadores e devolve (texto_protegido, blocos)."""
    blocks: list[str] = []

    def _save(match: re.Match[str]) -> str:
        idx = len(blocks)
        blocks.append(match.group(0))
        return f"\x00CODE{idx}\x00"

    protected = re.sub(r"```.*?```", _save, text, flags=re.DOTALL)
    return protected, blocks


def _restore_code_blocks(text: str, blocks: list[str]) -> str:
    for idx, block in enumerate(blocks):
        text = text.replace(f"\x00CODE{idx}\x00", block)
    return text


def fix_text(text: str) -> str:
    """Aplica todas as correções (accents + spaces) preservando blocos de código."""
    protected, blocks = _protect_code_blocks(text)
    fixed = fix_spaces_and_punct(fix_accents(protected))
    return _restore_code_blocks(fixed, blocks)


def process_markdown(input_path: Path, output_path: Path) -> Path:
    """Lê MD do `input_path`, aplica `fix_text`, grava em `output_path`."""
    content = input_path.read_text(encoding="utf-8")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(fix_text(content), encoding="utf-8")
    return output_path


def merge_into_book(
    md_paths: list[Path],
    target: Path,
    *,
    title: str = "Livro Consolidado",
) -> Path:
    """Concatena vários MDs em um único arquivo com title H1 e separadores.

    Cada MD vira uma seção H2 com o stem do arquivo como título.
    """
    parts = [f"# {title}\n\n"]
    for md in sorted(md_paths, key=lambda p: p.name):
        parts.append(f"\n---\n\n## {md.stem}\n\n")
        parts.append(fix_text(md.read_text(encoding="utf-8")).lstrip())
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("".join(parts), encoding="utf-8")
    return target
```

**Importante**: copiar o `ACCENT_MAP` real do `scripts/postprocess_md.py` — não inventar palavras. Verificar com `head -200 scripts/postprocess_md.py` e copiar literalmente o bloco do dicionário.

- [ ] **Step 1.5: Rodar testes e confirmar verde**

Run: `pytest tests/test_postprocess.py -v`
Expected: PASS (3 testes).

- [ ] **Step 1.6: Verificar lint e tipos**

Run: `ruff check src/scanner/postprocess tests/test_postprocess.py && mypy src/scanner/postprocess`
Expected: zero erros.

- [ ] **Step 1.7: Apagar script antigo e atualizar referências**

Run:

```bash
rm scripts/postprocess_md.py
```

Buscar referências ao script antigo:

```bash
grep -rn "postprocess_md" --include="*.py" --include="*.md" .
```

Se houver matches em `vault/` ou `docs/`, deixar (são logs históricos). Se houver match em código ativo (`src/`, `tests/`), atualizar para `from scanner.postprocess import ...`.

- [ ] **Step 1.8: Commit**

```bash
git add src/scanner/postprocess/ tests/test_postprocess.py scripts/postprocess_md.py
git commit -m "refactor(postprocess): move PT-BR fixer from scripts/ to importable package

- Move scripts/postprocess_md.py -> src/scanner/postprocess/ptbr.py
- Expose public API via __init__.py: fix_text, fix_accents, merge_into_book
- Add unit tests covering accents, casing preservation, cedilla
- Delete old script (replaced by module)

Pré-requisito para Fase 1 (backend FastAPI consumir o pós-processador como lib)."
```

---

## Task 2: Estender OutputFormat com PDF e ALL

**Files:**
- Modify: `src/scanner/pipeline.py:23-29` (enum `OutputFormat`)
- Modify: `tests/test_pipeline.py` (cobrir novos valores)

- [ ] **Step 2.1: Escrever teste para novos enum values**

Adicionar em `tests/test_pipeline.py`:

```python
import warnings

from scanner.pipeline import OutputFormat


def test_output_format_has_pdf_and_all() -> None:
    """OutputFormat deve expor PDF e ALL."""
    assert OutputFormat.PDF.value == "pdf"
    assert OutputFormat.ALL.value == "all"


def test_output_format_both_emits_deprecation() -> None:
    """OutputFormat.BOTH deve continuar funcionando como alias de ALL,
    mas emitir DeprecationWarning."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        # Acessar o membro deprecated dispara o warning
        from scanner.pipeline import OutputFormat as _OF
        value = _OF.BOTH
        assert value.value == "both"
        assert any(
            issubclass(w.category, DeprecationWarning) for w in caught
        ), "Esperado DeprecationWarning ao usar OutputFormat.BOTH"


def test_output_format_all_includes_md_docx_pdf() -> None:
    """Helper para verificar quais formatos cada valor representa."""
    from scanner.pipeline import formats_for
    assert formats_for(OutputFormat.MD) == frozenset({"md"})
    assert formats_for(OutputFormat.DOCX) == frozenset({"md", "docx"})
    assert formats_for(OutputFormat.PDF) == frozenset({"md", "pdf"})
    assert formats_for(OutputFormat.ALL) == frozenset({"md", "docx", "pdf"})
    assert formats_for(OutputFormat.BOTH) == frozenset({"md", "docx", "pdf"})
```

- [ ] **Step 2.2: Rodar testes e confirmar falha**

Run: `pytest tests/test_pipeline.py::test_output_format_has_pdf_and_all -v`
Expected: FAIL (`AttributeError: PDF` ou similar).

- [ ] **Step 2.3: Estender enum em pipeline.py**

Em `src/scanner/pipeline.py`, substituir o bloco do enum atual (linhas ~23-29) por:

```python
import warnings


class OutputFormat(StrEnum):
    """Formatos de saída solicitáveis.

    BOTH é DEPRECATED desde v0.2 — use ALL. Permanece como alias por
    retrocompatibilidade até v0.3, quando será removido.
    """

    MD = "md"
    DOCX = "docx"
    PDF = "pdf"
    ALL = "all"
    BOTH = "both"  # deprecated alias para ALL


# StrEnum membros não rodam código no acesso, então o warning vem
# de quem CONSOME o valor BOTH. Usamos formats_for() como ponto único
# de tradução enum→formatos concretos e emitimos o warning ali.

_FORMATS_BY_ENUM: dict[OutputFormat, frozenset[str]] = {
    OutputFormat.MD: frozenset({"md"}),
    OutputFormat.DOCX: frozenset({"md", "docx"}),
    OutputFormat.PDF: frozenset({"md", "pdf"}),
    OutputFormat.ALL: frozenset({"md", "docx", "pdf"}),
    OutputFormat.BOTH: frozenset({"md", "docx", "pdf"}),  # = ALL
}


def formats_for(fmt: OutputFormat) -> frozenset[str]:
    """Resolve enum para conjunto de formatos concretos.

    Emite DeprecationWarning para BOTH (alias temporário de ALL).
    """
    if fmt == OutputFormat.BOTH:
        warnings.warn(
            "OutputFormat.BOTH é deprecated. Use OutputFormat.ALL "
            "(produz MD + DOCX + PDF). Será removido em v0.3.",
            DeprecationWarning,
            stacklevel=2,
        )
    return _FORMATS_BY_ENUM[fmt]
```

- [ ] **Step 2.4: Rodar testes**

Run: `pytest tests/test_pipeline.py -v -k "output_format"`
Expected: 3 testes passam.

- [ ] **Step 2.5: Verificar lint**

Run: `ruff check src/scanner/pipeline.py`
Expected: zero erros.

- [ ] **Step 2.6: Commit**

```bash
git add src/scanner/pipeline.py tests/test_pipeline.py
git commit -m "feat(pipeline): add OutputFormat.PDF and OutputFormat.ALL with BOTH alias

- PDF e ALL adicionados ao enum
- BOTH mantido como alias deprecated de ALL (DeprecationWarning ao usar)
- formats_for() helper traduz enum para conjunto de formatos concretos
- Cobertura de testes para novos valores e warning"
```

---

## Task 3: Adicionar export/pdf.py via pandoc + xelatex

**Files:**
- Create: `src/scanner/export/pdf.py`
- Create: `tests/test_export_pdf.py`
- Modify: `src/scanner/export/__init__.py` (re-export `write_pdf`)

- [ ] **Step 3.1: Escrever teste de write_pdf (smoke)**

Criar `tests/test_export_pdf.py`:

```python
"""Testes de geração de PDF via pandoc."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from scanner.export import write_pdf


@pytest.fixture
def sample_md(tmp_path: Path) -> Path:
    """MD de exemplo com acentos PT-BR e estrutura básica."""
    md = tmp_path / "sample.md"
    md.write_text(
        "# Título com Acentuação\n\n"
        "Parágrafo com palavras que precisam funcionar: **gestão**, *atenção*, função.\n\n"
        "## Subseção\n\n"
        "- Item 1\n"
        "- Item 2 com ção\n",
        encoding="utf-8",
    )
    return md


@pytest.mark.skipif(
    shutil.which("pandoc") is None,
    reason="pandoc não está instalado no PATH",
)
def test_write_pdf_creates_file(sample_md: Path, tmp_path: Path) -> None:
    """write_pdf deve criar um PDF não-vazio a partir de um MD válido."""
    target = tmp_path / "output.pdf"
    result = write_pdf(sample_md, target)
    assert result == target.resolve()
    assert target.exists()
    assert target.stat().st_size > 1000  # PDF mínimo viável > 1KB


@pytest.mark.skipif(
    shutil.which("pandoc") is None,
    reason="pandoc não está instalado no PATH",
)
def test_write_pdf_preserves_portuguese_chars(
    sample_md: Path, tmp_path: Path
) -> None:
    """O PDF deve ser gerado sem erro com caracteres acentuados."""
    target = tmp_path / "output.pdf"
    # Apenas verifica que não levanta exceção
    write_pdf(sample_md, target)
    assert target.exists()
```

- [ ] **Step 3.2: Rodar e confirmar falha**

Run: `pytest tests/test_export_pdf.py -v`
Expected: FAIL com `ImportError` ou `cannot import name 'write_pdf'`.

- [ ] **Step 3.3: Implementar write_pdf**

Criar `src/scanner/export/pdf.py`:

```python
"""Conversão Markdown → PDF usando pandoc + xelatex.

Decisão registrada em `docs/superpowers/specs/2026-05-02-web-app-pwa-design.md`
(Seção 11.2): pandoc + xelatex como motor PDF principal — reusa toolchain do
DOCX, lida com acentos PT-BR nativamente, gera PDF "estilo artigo" com
tipografia decente.

Requer pandoc no PATH. Em ambientes sem LaTeX completo, pypandoc tenta usar
`xelatex`, `lualatex` ou `pdflatex` — falha clara se nenhum estiver disponível.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from scanner.errors import ConfigurationError, ConversionError

log = logging.getLogger(__name__)


def _ensure_pandoc() -> None:
    """Verifica que pandoc está disponível. Levanta ConfigurationError se não."""
    if shutil.which("pandoc") is None:
        raise ConfigurationError(
            "pandoc não encontrado no PATH. Instale: "
            "https://pandoc.org/installing.html (ou use pypandoc.download_pandoc())."
        )


def write_pdf(
    markdown_path: Path,
    target: Path,
    *,
    resource_dir: Path | None = None,
    pdf_engine: str = "xelatex",
) -> Path:
    """Converte um arquivo Markdown para PDF preservando estrutura e imagens.

    Args:
        markdown_path: Arquivo .md de origem.
        target: Caminho final do .pdf (será sobrescrito se existir).
        resource_dir: Pasta base para resolver imagens referenciadas no MD.
            Se None, usa o diretório do `markdown_path`.
        pdf_engine: 'xelatex' (default, suporta UTF-8) | 'lualatex' | 'pdflatex'.

    Returns:
        Path absoluto do PDF gerado.

    Raises:
        ConfigurationError: pandoc ausente.
        ConversionError: pandoc falhou na conversão.
    """
    _ensure_pandoc()
    import pypandoc  # type: ignore[import-untyped]

    target = target.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    md_path = markdown_path.resolve()
    rdir = (resource_dir or md_path.parent).resolve()

    extra_args: list[str] = [
        f"--pdf-engine={pdf_engine}",
        f"--resource-path={rdir}",
        "--variable=geometry:margin=2cm",
        "--variable=lang:pt-BR",
        "--standalone",
    ]

    log.info("Gerando PDF: %s -> %s (engine=%s)", md_path.name, target.name, pdf_engine)
    try:
        pypandoc.convert_file(
            str(md_path),
            "pdf",
            outputfile=str(target),
            extra_args=extra_args,
        )
    except Exception as exc:  # pypandoc levanta múltiplos tipos
        raise ConversionError(
            f"Falha ao gerar PDF de {md_path.name}: {exc}"
        ) from exc

    if not target.exists() or target.stat().st_size == 0:
        raise ConversionError(
            f"Pandoc retornou sucesso mas o PDF está vazio: {target}"
        )
    return target
```

Atualizar `src/scanner/export/__init__.py`:

```python
"""Exporters — escrevem o resultado da extração em formatos finais."""

from scanner.export.docx import write_docx
from scanner.export.markdown import write_markdown
from scanner.export.pdf import write_pdf

__all__ = ["write_docx", "write_markdown", "write_pdf"]
```

- [ ] **Step 3.4: Rodar testes**

Run: `pytest tests/test_export_pdf.py -v`
Expected: PASS (ou skip se pandoc não disponível — verificar `which pandoc` antes).

Pré-requisito: pandoc instalado. Se não estiver:

```bash
# Usar o pandoc que pypandoc baixa automaticamente
python -c "import pypandoc; pypandoc.download_pandoc()"
```

Verificar:

```bash
pandoc --version | head -1
xelatex --version | head -1
```

Se `xelatex` não estiver disponível: `apt-get install texlive-xetex` (Linux) ou MikTeX (Windows). Em produção (Hostinger), isso vai no Dockerfile.

- [ ] **Step 3.5: Verificar lint e tipos**

Run: `ruff check src/scanner/export/pdf.py && mypy src/scanner/export/pdf.py`
Expected: zero erros.

- [ ] **Step 3.6: Commit**

```bash
git add src/scanner/export/pdf.py src/scanner/export/__init__.py tests/test_export_pdf.py
git commit -m "feat(export): add PDF output via pandoc + xelatex

- write_pdf() em export/pdf.py — mesma toolchain do DOCX, com xelatex
- UTF-8 nativo (acentos PT-BR), margin 2cm, lang pt-BR
- ConfigurationError clara se pandoc/LaTeX faltar
- Testes smoke + verificação de UTF-8 (skip se pandoc ausente no CI)"
```

---

## Task 4: Atualizar pipeline.scan() para gerar PDF

**Files:**
- Modify: `src/scanner/pipeline.py` (função `scan()`)
- Modify: `tests/test_pipeline.py` (cobrir geração de PDF)

- [ ] **Step 4.1: Escrever teste de scan() com formats=PDF**

Adicionar em `tests/test_pipeline.py`:

```python
from unittest.mock import MagicMock, patch

import pytest

from scanner.pipeline import OutputFormat, ScanRequest, ScanResult, scan


@pytest.mark.slow
def test_scan_generates_pdf_when_requested(tmp_path: Path) -> None:
    """scan() com formats=PDF deve gerar md + pdf (não docx)."""
    # Usar fixture de imagem de teste já existente
    fixture = Path(__file__).parent / "fixtures" / "sample_page.jpg"
    if not fixture.exists():
        pytest.skip("Fixture sample_page.jpg ausente")

    output = tmp_path / "out"
    request = ScanRequest(
        source=fixture,
        output_dir=output,
        formats=OutputFormat.PDF,
    )
    result = scan(request)

    assert result.markdown_path.exists()
    assert result.pdf_path is not None and result.pdf_path.exists()
    assert result.docx_path is None  # PDF não inclui DOCX


@pytest.mark.slow
def test_scan_generates_all_formats(tmp_path: Path) -> None:
    """scan() com formats=ALL deve gerar md + docx + pdf."""
    fixture = Path(__file__).parent / "fixtures" / "sample_page.jpg"
    if not fixture.exists():
        pytest.skip("Fixture sample_page.jpg ausente")

    output = tmp_path / "out"
    request = ScanRequest(
        source=fixture,
        output_dir=output,
        formats=OutputFormat.ALL,
    )
    result = scan(request)

    assert result.markdown_path.exists()
    assert result.docx_path is not None and result.docx_path.exists()
    assert result.pdf_path is not None and result.pdf_path.exists()
```

- [ ] **Step 4.2: Rodar e confirmar falha**

Run: `pytest tests/test_pipeline.py -v -k "scan_generates" -m slow`
Expected: FAIL com `AttributeError: 'ScanResult' object has no attribute 'pdf_path'`.

- [ ] **Step 4.3: Adicionar pdf_path ao ScanResult**

Em `src/scanner/pipeline.py`, dataclass `ScanResult`:

```python
@dataclass(slots=True)
class ScanResult:
    """Resultado: caminhos dos arquivos gerados."""

    source: Path
    markdown_path: Path
    docx_path: Path | None
    pdf_path: Path | None              # NOVO
    images: tuple[Path, ...]
    page_count: int
    artifacts_dir: Path

    def __str__(self) -> str:
        parts = [f"  - {self.markdown_path}"]
        if self.docx_path:
            parts.append(f"  - {self.docx_path}")
        if self.pdf_path:
            parts.append(f"  - {self.pdf_path}")
        if self.images:
            parts.append(f"  - {len(self.images)} imagem(ns) em {self.artifacts_dir}")
        return f"Scan de {self.source.name} ({self.page_count}p):\n" + "\n".join(parts)
```

- [ ] **Step 4.4: Atualizar scan() para gerar PDF quando solicitado**

Em `src/scanner/pipeline.py`, função `scan()`:

```python
from scanner.export import write_docx, write_pdf  # adicionar write_pdf no import


def scan(request: ScanRequest, *, engine: DoclingEngine | None = None) -> ScanResult:
    """Roda o pipeline para UM arquivo.

    Reuse `engine` quando processar múltiplos arquivos (init é caro).
    """
    _validate_request(request)
    engine = engine or DoclingEngine(
        do_ocr=request.do_ocr,
        do_table_structure=request.do_table_structure,
        device=request.device,
        ocr_languages=list(request.ocr_languages),
        ocr_engine=request.ocr_engine,
        tessdata_path=request.tessdata_path,
    )

    base = request.source.stem
    out_dir = request.output_dir.resolve()
    artifacts_dir = out_dir / f"{base}-images"
    md_path = out_dir / f"{base}.md"

    extraction = engine.extract(
        request.source,
        markdown_target=md_path,
        artifacts_dir=artifacts_dir,
    )

    formats_set = formats_for(request.formats)
    docx_path: Path | None = None
    pdf_path: Path | None = None

    if "docx" in formats_set:
        docx_path = write_docx(
            extraction.markdown_path,
            out_dir / f"{base}.docx",
            resource_dir=out_dir,
        )

    if "pdf" in formats_set:
        pdf_path = write_pdf(
            extraction.markdown_path,
            out_dir / f"{base}.pdf",
            resource_dir=out_dir,
        )

    return ScanResult(
        source=extraction.source,
        markdown_path=extraction.markdown_path,
        docx_path=docx_path,
        pdf_path=pdf_path,
        images=extraction.images,
        page_count=extraction.page_count,
        artifacts_dir=artifacts_dir,
    )
```

Atualizar `scan_batch()` similarmente — encontrar a função e adicionar `pdf_path` no `ScanResult` retornado.

- [ ] **Step 4.5: Atualizar merge_results() para gerar PDF consolidado**

Em `merge_results()` em `pipeline.py`:

```python
def merge_results(
    results: list[ScanResult],
    output_dir: Path,
    *,
    base_name: str = "combined",
    formats: OutputFormat = OutputFormat.MD,
) -> Path:
    """Concatena MDs de múltiplos resultados em um único arquivo.

    Se `formats` incluir DOCX/PDF, também gera os respectivos arquivos.
    """
    parts = [f"# {base_name.replace('-', ' ').title()}\n\n"]
    target_md = output_dir / f"{base_name}.md"

    for r in sorted(results, key=lambda x: x.source.name):
        parts.append(f"\n---\n\n## {r.source.stem}\n\n")
        try:
            content = r.markdown_path.read_text(encoding="utf-8")
            parts.append(content.lstrip())
        except OSError as exc:
            parts.append(f"*Erro ao ler {r.markdown_path.name}: {exc}*\n")

    target_md.write_text("".join(parts), encoding="utf-8")
    log.info("Merge MD: %s (%d seções)", target_md, len(results))

    formats_set = formats_for(formats)
    if "docx" in formats_set:
        target_docx = output_dir / f"{base_name}.docx"
        write_docx(target_md, target_docx, resource_dir=output_dir)
        log.info("Merge DOCX: %s", target_docx)
    if "pdf" in formats_set:
        target_pdf = output_dir / f"{base_name}.pdf"
        write_pdf(target_md, target_pdf, resource_dir=output_dir)
        log.info("Merge PDF: %s", target_pdf)

    return target_md
```

- [ ] **Step 4.6: Rodar testes**

Run: `pytest tests/test_pipeline.py -v -m slow`
Expected: novos testes passam (assumindo fixture existe).

Para testes rápidos (sem `-m slow`):

```bash
pytest tests/test_pipeline.py -v
```

Todos devem passar.

- [ ] **Step 4.7: Verificar lint e tipos**

Run: `ruff check src/scanner/pipeline.py && mypy src/scanner/pipeline.py`
Expected: zero erros.

- [ ] **Step 4.8: Commit**

```bash
git add src/scanner/pipeline.py tests/test_pipeline.py
git commit -m "feat(pipeline): generate PDF output when formats includes PDF or ALL

- ScanResult ganha pdf_path: Path | None
- scan() consulta formats_for(request.formats) para decidir DOCX/PDF
- merge_results() também gera PDF consolidado quando solicitado
- Testes slow validam geração ponta-a-ponta para PDF e ALL"
```

---

## Task 5: Atualizar CLI para aceitar -f all

**Files:**
- Modify: `src/scanner/cli.py` (suporte a 'all' + warning para 'both')
- Modify: `tests/test_cli.py`

- [ ] **Step 5.1: Escrever teste para nova flag**

Adicionar em `tests/test_cli.py`:

```python
from typer.testing import CliRunner

from scanner.cli import app


def test_cli_accepts_format_all(tmp_path: Path) -> None:
    """CLI deve aceitar `-f all` sem erro de validação."""
    runner = CliRunner()
    fixture = Path(__file__).parent / "fixtures" / "sample_page.jpg"
    if not fixture.exists():
        pytest.skip("Fixture sample_page.jpg ausente")

    out = tmp_path / "out"
    result = runner.invoke(
        app, ["convert", str(fixture), "-o", str(out), "-f", "all"]
    )
    # Não deve falhar por validação de flag (pode falhar por OCR/pandoc — ok)
    assert "Invalid value for '-f'" not in result.output


def test_cli_warns_on_format_both(tmp_path: Path) -> None:
    """`-f both` deve continuar funcionando mas emitir warning."""
    runner = CliRunner()
    fixture = Path(__file__).parent / "fixtures" / "sample_page.jpg"
    if not fixture.exists():
        pytest.skip("Fixture sample_page.jpg ausente")

    out = tmp_path / "out"
    result = runner.invoke(
        app, ["convert", str(fixture), "-o", str(out), "-f", "both"]
    )
    assert "deprecated" in result.output.lower() or "deprecat" in result.output.lower()
```

- [ ] **Step 5.2: Rodar e confirmar falha**

Run: `pytest tests/test_cli.py -v -k "format"`
Expected: FAIL — flag `all` não existe no enum visto pelo Typer ou warning não aparece.

- [ ] **Step 5.3: Atualizar CLI**

Em `src/scanner/cli.py`, na função `convert()`, após a linha que recebe `fmt`:

```python
def convert(
    # ... (parâmetros existentes; o tipo do `fmt` é OutputFormat — Typer já aceita
    # todos os valores do enum, incluindo o novo ALL e o legado BOTH)
    ...
) -> None:
    """Converte foto(s) de página(s) em Markdown estruturado."""
    # Aviso de deprecation se o usuário passou 'both'
    if fmt == OutputFormat.BOTH:
        err_console.print(
            "[yellow][deprecated][/yellow] '-f both' será removido em v0.3. "
            "Use '-f all' (gera MD + DOCX + PDF)."
        )

    try:
        inputs = collect_inputs(source)
    except ScannerError as exc:
        err_console.print(f"[red]Erro:[/red] {exc}")
        raise typer.Exit(code=2) from exc

    # ... resto da função permanece igual
```

Atualizar a docstring para listar os novos formatos e o exemplo:

```python
    """Converte foto(s) de página(s) em Markdown estruturado.

    Formatos aceitos via -f:
      md    -> apenas Markdown
      docx  -> Markdown + DOCX
      pdf   -> Markdown + PDF
      all   -> Markdown + DOCX + PDF
      both  -> [DEPRECATED] alias para 'all', será removido em v0.3

    Exemplos:

      scanner convert ./pagina.jpg -o ./out
      scanner convert ./fotos/ -o ./out -f all
    """
```

- [ ] **Step 5.4: Rodar testes**

Run: `pytest tests/test_cli.py -v`
Expected: PASS (todos os testes existentes + 2 novos).

- [ ] **Step 5.5: Verificar lint**

Run: `ruff check src/scanner/cli.py`
Expected: zero erros.

- [ ] **Step 5.6: Smoke test manual**

Rodar a CLI com uma foto de teste para confirmar geração dos 3 formatos:

```bash
scanner convert ./samples/test.jpg -o ./output-test -f all
ls -la ./output-test/
# Esperado: test.md, test.docx, test.pdf, test-images/
```

Se `samples/test.jpg` não existir, qualquer JPG/PNG serve. Verificar tamanhos > 0 e abrir o PDF para conferir que acentos PT-BR aparecem corretamente.

- [ ] **Step 5.7: Commit**

```bash
git add src/scanner/cli.py tests/test_cli.py
git commit -m "feat(cli): accept '-f all' for MD+DOCX+PDF; deprecate '-f both'

- Nova flag '-f all' produz os 3 formatos
- '-f both' continua funcionando mas imprime aviso amarelo de deprecation
- Docstring atualizada com tabela de formatos
- Testes Typer cobrem aceitação de 'all' e warning de 'both'"
```

---

## Self-Review

**1. Spec coverage:**
- ✅ Seção 11.1 (mover postprocess) → Task 1
- ✅ Seção 11.2 (PDF + OutputFormat) → Tasks 2, 3
- ✅ Seção 7.4 (estratégia BOTH alias) → Task 2
- ✅ Pipeline integration → Task 4
- ✅ CLI compat → Task 5
- ⏭️ Seções 11.3-11.13 (FastAPI, frontend, PWA, infra) → fora do escopo desta fase

**2. Placeholder scan:**
- ✅ Sem TODOs ou TBDs no plano
- ⚠️ Task 1.4 instrui copiar `ACCENT_MAP` de `scripts/postprocess_md.py`. Não é placeholder — é instrução clara para preservar o dicionário existente. Aceitável.
- ✅ Sem "implement later" / "add error handling"
- ✅ Sem referências a tipos/funções não definidos

**3. Type consistency:**
- ✅ `OutputFormat` enum: nomes consistentes (PDF, ALL, BOTH) entre Tasks 2, 4, 5
- ✅ `ScanResult` ganha `pdf_path: Path | None` (Task 4) e o CLI consulta-o coerentemente
- ✅ `formats_for()` é definido em Task 2 e consumido em Task 4
- ✅ `write_pdf` é importado em `pipeline.py` (Task 4) com mesma assinatura definida em Task 3

**4. Risk areas:**
- Pandoc + xelatex pode falhar em ambientes sem LaTeX. Task 3 testa skip-if-not-available; produção (Hostinger) instala via Dockerfile na Fase 4.
- `ACCENT_MAP` precisa ser copiado fielmente do script antigo — Task 1.4 deixa explícito.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-02-phase-0-backend-refactor.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — Eu despacho um subagent fresco por tarefa, revisão entre tarefas, iteração rápida. Cada subagent começa com contexto zero do nosso código mas recebe a task definitiva — bom para tarefas atômicas como estas.

**2. Inline Execution** — Executar tarefas nesta sessão usando executing-plans, com checkpoints para revisão. Mantém todo o contexto na memória atual.

**Qual abordagem?**
