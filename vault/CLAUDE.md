# Vault — Instruções Zettelkasten para o Claude Code

> Estas regras se aplicam a **qualquer arquivo dentro de `vault/`**.
> O `CLAUDE.md` da raiz do projeto cobre regras gerais (context-mode, Context Navigation, stack).

## O que é este vault

Memória persistente do projeto **Scanner de Imagens**. Armazena decisões, contexto, progresso, conhecimento técnico e histórico de chats. Lido pelo Claude Code a cada sessão para evitar amnésia.

Este é um **vault local** — vive dentro do repositório do projeto e viaja com ele no `git`.

## Estrutura

| Pasta | Função |
|-------|--------|
| `permanent/` | Notas atômicas consolidadas (Zettelkasten clássico) |
| `inbox/` | Captura bruta — ideias, recortes, anotações rápidas |
| `fleeting/` | Rascunhos temporários — promovidos para `permanent/` ou descartados |
| `templates/` | Templates para criação de notas |
| `logs/` | Session logs gerados pelo comando `/salvar` |
| `references/` | Material de referência externo (papers, docs colados) |
| `projeto/` | MOCs do projeto — `arquitetura.md`, `decisoes.md`, `convencoes.md` |
| `pipeline/` | Fluxos de dados, estágios de processamento (foto → markdown → docx) |
| `dados/` | Schema, modelos, formatos de saída |
| `features/` | Features planejadas/implementadas (uma nota por feature) |
| `chats/code/` | Conversas importadas do Claude Code (auto-import) |
| `chats/web/` | Conversas importadas do Claude Web/App (auto-import) |
| `graphify/` | Notas geradas automaticamente pelo Graphify — **NÃO editar manualmente** |

## Regras Zettelkasten

### Criação de notas
- **Wikilinks obrigatórios**: use `[[nome-da-nota]]`, nunca `[texto](nota.md)`.
- **Frontmatter YAML obrigatório** em toda nota.
- **kebab-case** nos nomes de arquivo: `docling-pipeline.md`, não `Docling Pipeline.md`.
- **1 conceito por nota permanente** (atomicidade).
- **Mínimo 2 wikilinks por nota** (linking denso — princípio do Zettelkasten).

### Frontmatter padrão

```yaml
---
title: Nome da Nota
tags: [scanner, ocr]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: active
type: permanent
---
```

### Tags do projeto (vocabulário controlado)

| Tag | Quando usar |
|-----|-------------|
| `scanner` | Tudo relacionado ao app de scanner em si |
| `ocr` | OCR, Tesseract, reconhecimento óptico |
| `docling` | Decisões/notas sobre Docling |
| `opendataloader` | Decisões/notas sobre OpenDataloader-PDF |
| `markdown` | Output em markdown |
| `docx` | Export para Word |
| `imagem` | Processamento de imagens |
| `decisao` | Decisão arquitetural registrada |
| `bug` | Bug ou debugging em andamento |
| `pipeline` | Pipeline de processamento |
| `chat-import` | Auto-aplicada pelo pipeline de import |

### Nunca faça
- Não delete notas sem perguntar (use `status: archived` no frontmatter).
- Não use links markdown para notas internas (use sempre wikilinks).
- Não crie notas sem frontmatter.
- Não edite arquivos em `graphify/` manualmente.
- Não mude a estrutura de pastas sem documentar em `projeto/decisoes.md`.

## Comandos `/retomar` e `/salvar`

Os comandos custom estão em `.claude/commands/retomar.md` e `.claude/commands/salvar.md` na raiz do projeto. Detalhes lá.

**Resumo `/retomar`**: lê últimos 3 logs em `logs/`, lê `projeto/decisoes.md`, resume estado atual.

**Resumo `/salvar`**: cria `logs/YYYY-MM-DD-{slug}.md` com frontmatter, lista trabalho da sessão.

## Plugins recomendados (Obsidian Community)

Instalar manualmente em Settings → Community Plugins:

| Plugin | Função |
|--------|--------|
| BRAT | Instalar plugins beta (necessário para 3D Graph) |
| 3D Graph (v2.4.1) | Visualização 3D do vault — instalar via BRAT |
| Folders to Graph | Mostra pastas como nós no graph view |
| Calendar | Navegação via daily notes |
| Templater | Variáveis dinâmicas em templates |

## Filtros úteis no Graph View

| Filtro | Mostra |
|--------|--------|
| `path:permanent` | Só notas permanentes (conhecimento consolidado) |
| `path:graphify` | Só nós do codebase (gerados pelo Graphify) |
| `tag:#chat-import` | Só chats importados |
| `-path:graphify -path:chats` | Só notas manuais (vault "puro") |
