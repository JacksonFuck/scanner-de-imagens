# Samples (gitignored)

Pasta para fotos/imagens de teste. Conteúdo de imagem é gitignored — só este README é versionado.

## Origens das amostras incluídas

| Arquivo | Origem | Caso de uso |
|---------|--------|-------------|
| `old-newspaper.png` | `docling-main/tests/data_scanned/old_newspaper.png` | Jornal escaneado — simula foto de página antiga |
| `paper-page-with-table.png` | `docling-main/tests/data/2305.03393v1-pg9-img.png` | Página de paper científico com tabela |

## Como adicionar suas próprias

Coloque qualquer JPG/PNG/PDF aqui. O `.gitignore` evita que sejam comitados.

```powershell
# uso:
python -m scanner convert ./samples/minha-foto.jpg -o ./output -f both -v
```
