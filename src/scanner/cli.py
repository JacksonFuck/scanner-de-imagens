"""CLI Typer + Rich.

Apresentação fina sobre `pipeline.scan_batch`. Toda lógica de negócio fica no
pipeline; aqui só lemos args, configuramos logging e formatamos output.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from scanner import __version__
from scanner.errors import ScannerError
from scanner.pipeline import OutputFormat, collect_inputs, scan_batch

app = typer.Typer(
    name="scanner",
    help="Scanner OCR de fotos de páginas de livros/artigos → Markdown + DOCX + PDF.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()
err_console = Console(stderr=True)


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"scanner {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option("--version", callback=_version_callback, is_eager=True, help="Exibe versão"),
    ] = False,
    verbose: Annotated[bool, typer.Option("-v", "--verbose", help="Logs detalhados (DEBUG)")] = False,
) -> None:
    """Configura logging com base nas flags globais."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


@app.command()
def convert(
    source: Annotated[
        Path,
        typer.Argument(
            exists=True,
            help="Arquivo (JPG/PNG/PDF) ou pasta com múltiplos arquivos",
        ),
    ],
    output_dir: Annotated[
        Path,
        typer.Option("-o", "--output", help="Pasta de saída"),
    ] = Path("./output"),
    fmt: Annotated[
        OutputFormat,
        typer.Option(
            "-f",
            "--format",
            help="Formato de saída: md | docx | pdf | all | both (deprecated alias de all)",
        ),
    ] = OutputFormat.MD,
    no_ocr: Annotated[bool, typer.Option("--no-ocr", help="Desabilita OCR")] = False,
    no_tables: Annotated[
        bool, typer.Option("--no-tables", help="Desabilita reconhecimento de tabelas")
    ] = False,
    device: Annotated[
        str,
        typer.Option(
            "--device",
            help="Dispositivo de inferência: 'auto' (default, usa GPU se disponível), 'cuda', 'cpu'",
        ),
    ] = "auto",
    ocr_lang: Annotated[
        str,
        typer.Option(
            "--ocr-lang",
            help="Idiomas do OCR separados por vírgula (default: 'pt,en')",
        ),
    ] = "pt,en",
    ocr_engine: Annotated[
        str,
        typer.Option(
            "--ocr-engine",
            help="Engine de OCR: 'easyocr' (default, melhor para PT) ou 'tesseract'",
        ),
    ] = "easyocr",
    tessdata: Annotated[
        str | None,
        typer.Option(
            "--tessdata",
            help="Caminho do tessdata (apenas com --ocr-engine tesseract). "
                 "Default tenta ./tessdata-portuguese e PATH.",
        ),
    ] = None,
    merge: Annotated[
        bool | None,
        typer.Option(
            "--merge/--no-merge",
            help="Consolidar múltiplas imagens em um único arquivo. "
                 "Se não passado, pergunta interativamente quando há > 1 imagem.",
        ),
    ] = None,
    merge_name: Annotated[
        str,
        typer.Option("--merge-name", help="Nome base do arquivo consolidado (sem extensão)"),
    ] = "combined",
) -> None:
    """Converte foto(s) de página(s) em Markdown estruturado.

    Formatos aceitos via -f:
      md    → apenas Markdown
      docx  → Markdown + DOCX
      pdf   → Markdown + PDF
      all   → Markdown + DOCX + PDF
      both  → [DEPRECATED] alias de 'all', será removido em v0.3

    Exemplos:

      scanner convert ./pagina.jpg -o ./out

      scanner convert ./fotos/ -o ./out -f all
    """
    # Aviso de deprecation se o usuário passou 'both'
    if fmt == OutputFormat.BOTH:
        err_console.print(
            "[yellow]DEPRECATED:[/yellow] '-f both' será removido em v0.3. "
            "Use '-f all' (gera MD + DOCX + PDF)."
        )

    try:
        inputs = collect_inputs(source)
    except ScannerError as exc:
        err_console.print(f"[red]Erro:[/red] {exc}")
        raise typer.Exit(code=2) from exc

    console.print(f"[bold]Processando {len(inputs)} arquivo(s)[/bold]")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Resolve merge: explícito > pergunta interativa > default (False)
    merge_resolved = _resolve_merge(merge, len(inputs))

    languages = tuple(s.strip() for s in ocr_lang.split(",") if s.strip())
    if not languages:
        languages = ("pt", "en")

    if merge_resolved:
        console.print(
            f"[dim]Modo: arquivo único → {merge_name}.md "
            f"(+ docx/pdf conforme -f {fmt.value})[/dim]"
        )
    else:
        console.print("[dim]Modo: arquivos separados (um por imagem)[/dim]")

    # Auto-detect tessdata path se Tesseract sem path explícito
    resolved_tessdata = tessdata
    if ocr_engine == "tesseract" and not resolved_tessdata:
        local = Path("./tessdata-portuguese").resolve()
        if local.is_dir():
            resolved_tessdata = str(local)
            console.print(f"[dim]tessdata local detectado: {local}[/dim]")

    console.print(
        f"[dim]OCR: engine={ocr_engine}, idiomas={list(languages)}, device={device}[/dim]"
    )

    result = scan_batch(
        inputs,
        output_dir,
        formats=fmt,
        do_ocr=not no_ocr,
        device=device,
        ocr_languages=languages,
        ocr_engine=ocr_engine,
        tessdata_path=resolved_tessdata,
        merge=merge_resolved,
        merge_name=merge_name,
    )

    _render_results(result)

    if result.failures:
        raise typer.Exit(code=1)


def _resolve_merge(explicit: bool | None, n_inputs: int) -> bool:
    """Resolve a flag --merge.

    - Se explícito (True/False): usa o valor passado.
    - Se None E há > 1 imagem E stdin é TTY: pergunta interativamente.
    - Caso contrário (None + 1 imagem ou não-tty): default False.
    """
    if explicit is not None:
        return explicit
    if n_inputs <= 1:
        return False
    # Pergunta apenas em sessão interativa (evita travar em pipes/CI)
    if not sys.stdin.isatty():
        return False
    return typer.confirm(
        f"Consolidar as {n_inputs} imagens em UM único arquivo?",
        default=False,
    )


def _render_results(result) -> None:  # type: ignore[no-untyped-def]
    """Imprime tabela Rich com sucessos e falhas."""
    table = Table(title="Resultados", show_lines=False)
    table.add_column("Arquivo", style="cyan")
    table.add_column("Páginas", justify="right")
    table.add_column("Imagens", justify="right")
    table.add_column("Status", style="green")

    for r in result.successes:
        table.add_row(r.source.name, str(r.page_count), str(len(r.images)), "OK")
    for src, exc in result.failures:
        table.add_row(src.name, "—", "—", f"[red]ERRO: {exc}[/red]")

    console.print(table)
    console.print(
        f"\n[bold]Total[/bold]: {result.total} | "
        f"[green]OK[/green]: {len(result.successes)} | "
        f"[red]Falhas[/red]: {len(result.failures)}"
    )


if __name__ == "__main__":
    sys.exit(app())
