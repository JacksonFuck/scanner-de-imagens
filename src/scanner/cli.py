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
    help="Scanner OCR de fotos de páginas de livros/artigos → Markdown + DOCX.",
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
        typer.Option("-f", "--format", help="Formato de saída"),
    ] = OutputFormat.MD,
    no_ocr: Annotated[bool, typer.Option("--no-ocr", help="Desabilita OCR")] = False,
    no_tables: Annotated[
        bool, typer.Option("--no-tables", help="Desabilita reconhecimento de tabelas")
    ] = False,
) -> None:
    """Converte foto(s) de página(s) em Markdown estruturado.

    Exemplos:

      scanner convert ./pagina.jpg -o ./out

      scanner convert ./fotos/ -o ./out -f both
    """
    try:
        inputs = collect_inputs(source)
    except ScannerError as exc:
        err_console.print(f"[red]Erro:[/red] {exc}")
        raise typer.Exit(code=2) from exc

    console.print(f"[bold]Processando {len(inputs)} arquivo(s)[/bold]")
    output_dir.mkdir(parents=True, exist_ok=True)

    result = scan_batch(
        inputs,
        output_dir,
        formats=fmt,
        do_ocr=not no_ocr,
    )

    _render_results(result)

    if result.failures:
        raise typer.Exit(code=1)


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
