# Scanner de Imagens

> OCR de fotografias de páginas de livros e artigos → **Markdown estruturado** + export opcional para **DOCX**, preservando imagens e qualidade.

Construído sobre [Docling](https://github.com/DS4SD/docling) (IBM Research) — engine que aceita JPG/PNG/PDF nativamente, faz OCR, detecta tabelas e classifica imagens dentro das páginas.

📖 **[Documentação completa em docs/HANDOFF.md](docs/HANDOFF.md)** — instalação, arquitetura, decisões, troubleshooting, roadmap.

---

## Instalação

Requer **Python 3.11+** e **pandoc** (para export DOCX).

```bash
# clonar e entrar no diretório do projeto
cd "Scanner de imagens"

# criar venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows PowerShell
# source .venv/bin/activate     # Linux/macOS

# instalar (dev mode)
pip install -e ".[dev]"
```

Pandoc: instale via [pandoc.org/installing](https://pandoc.org/installing.html) ou deixe o `pypandoc` baixar automaticamente na primeira execução.

## Uso

### CLI

```bash
# converter uma foto
scanner convert ./pagina.jpg -o ./output

# converter pasta inteira
scanner convert ./fotos/ -o ./output

# gerar Markdown E DOCX
scanner convert ./pagina.jpg -o ./output -f both

# desabilitar OCR (se a imagem já tem texto selecionável — ex.: PDF nativo)
scanner convert ./doc.pdf -o ./output --no-ocr

# logs detalhados
scanner -v convert ./pagina.jpg -o ./output
```

### Python API

```python
from pathlib import Path
from scanner import scan, ScanRequest, OutputFormat

result = scan(ScanRequest(
    source=Path("./pagina.jpg"),
    output_dir=Path("./output"),
    formats=OutputFormat.BOTH,
))

print(result.markdown_path)  # ./output/pagina.md
print(result.docx_path)      # ./output/pagina.docx
print(result.images)         # tuple de Paths para imagens extraídas
```

### Output

Para `pagina.jpg`, gera:

```
output/
├── pagina.md                 # markdown estruturado
├── pagina.docx               # (se -f both ou -f docx)
└── pagina-images/            # imagens extraídas
    ├── image_000001.png
    ├── image_000002.png
    └── ...
```

O `.md` referencia as imagens por caminho relativo: `![](pagina-images/image_000001.png)`.

## Formatos suportados

| Entrada | Saída |
|---------|-------|
| JPG, JPEG, PNG, TIFF, BMP, WebP | Markdown |
| PDF (digital ou escaneado) | Markdown + imagens extraídas |
|  | DOCX (via pandoc) |

## Arquitetura

```
src/scanner/
├── cli.py                    # Typer + Rich — CLI
├── pipeline.py               # orquestrador (scan, scan_batch, collect_inputs)
├── engine/
│   └── docling_engine.py     # adapter da DocumentConverter API do Docling
├── export/
│   ├── markdown.py           # grava .md
│   └── docx.py               # MD -> DOCX via pypandoc
└── errors.py                 # ScannerError, InvalidInputError, ConversionError
```

## Testes

```bash
# testes rápidos (não carregam Docling)
pytest

# todos os testes incluindo os "slow" (carregam modelos ML)
pytest -m slow

# com cobertura
pytest --cov=scanner --cov-report=html
```

## Memória persistente do projeto

Este repo usa o setup descrito em [`reports/leia-o-texto-abaixo-joyful-bubble.md`](./reports/leia-o-texto-abaixo-joyful-bubble.md):

- **Vault Obsidian** em `vault/` — decisões, arquitetura, logs de sessão
- **Comandos custom** `/retomar` e `/salvar` para o Claude Code
- **Pipeline de chats** em `scripts/` (PowerShell + Python)
- **Knowledge graph** via Graphify (rodar `graphify . --obsidian --obsidian-dir .\vault\graphify`)

## Licença

MIT
