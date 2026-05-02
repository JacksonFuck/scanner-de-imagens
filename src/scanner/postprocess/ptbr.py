"""Implementação do pós-processador PT-BR (lib).

Movido de `scripts/postprocess_md.py` para se tornar um módulo importável
(originalmente um script CLI standalone). API pública via
`src/scanner/postprocess/__init__.py`.

Aplica em ordem:
1. `fix_accents`     — palavras comuns sem acento → com acento (ACCENT_MAP)
2. `fix_spaces_and_punct` — espaço antes de pontuação ASCII (.,;:!?)
3. `fix_zero_as_o`   — "0" no início de palavras vira "O" (artigo confundido)

Helpers: `process_markdown(content)` aplica tudo preservando blocos de código.
`fix_text` é alias público de `process_markdown`. `merge_into_book` consolida
vários MDs em um só com sumário.

Pré-requisito da Fase 1 (FastAPI): backend importa este módulo como biblioteca.
"""

from __future__ import annotations

import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Dicionário de correções PT-BR
# ---------------------------------------------------------------------------
# Palavras comuns que o OCR sem PT geralmente vira ASCII puro.
# Formato: { padrao_sem_acento: forma_com_acento }
# Aplicado case-insensitive mantendo o casing original.

ACCENT_MAP: dict[str, str] = {
    # ção, ções
    "satisfacao": "satisfação", "satisfacoes": "satisfações",
    "reducao": "redução", "reducoes": "reduções",
    "admissao": "admissão", "admissoes": "admissões",
    "readmissao": "readmissão", "readmissoes": "readmissões",
    "implantacao": "implantação",
    "instituicao": "instituição", "instituicoes": "instituições",
    "negociacao": "negociação", "negociacoes": "negociações",
    "atracao": "atração",
    "intencao": "intenção",
    "intercorrencia": "intercorrência", "intercorrencias": "intercorrências",
    "informacao": "informação", "informacoes": "informações",
    "atencao": "atenção",
    "operacao": "operação", "operacoes": "operações",
    "geracao": "geração", "geracoes": "gerações",
    "selecao": "seleção", "selecoes": "seleções",
    "execucao": "execução", "execucoes": "execuções",
    "decisao": "decisão", "decisoes": "decisões",
    "construcao": "construção",
    "previsao": "previsão", "previsoes": "previsões",
    "verificacao": "verificação", "verificacoes": "verificações",
    "validacao": "validação", "validacoes": "validações",
    "manutencao": "manutenção",
    "documentacao": "documentação",
    "evolucao": "evolução",
    "transformacao": "transformação", "transformacoes": "transformações",
    "interacao": "interação", "interacoes": "interações",
    "comunicacao": "comunicação", "comunicacoes": "comunicações",
    "regulamentacao": "regulamentação",
    "orientacao": "orientação", "orientacoes": "orientações",
    "investigacao": "investigação", "investigacoes": "investigações",
    "indicacao": "indicação", "indicacoes": "indicações",
    "consultacao": "consultação",
    "definicao": "definição", "definicoes": "definições",
    "preocupacao": "preocupação", "preocupacoes": "preocupações",
    "aplicacao": "aplicação", "aplicacoes": "aplicações",
    "avaliacao": "avaliação", "avaliacoes": "avaliações",
    "discussao": "discussão", "discussoes": "discussões",
    "expansao": "expansão",
    "compreensao": "compreensão",
    "extensao": "extensão", "extensoes": "extensões",
    "tensao": "tensão",
    "pretensao": "pretensão",
    "promocao": "promoção", "promocoes": "promoções",
    "atuacao": "atuação", "atuacoes": "atuações",
    "introducao": "introdução",
    "tributacao": "tributação",
    "publicacao": "publicação", "publicacoes": "publicações",
    "condicao": "condição", "condicoes": "condições",
    "permissao": "permissão", "permissoes": "permissões",
    "remissao": "remissão", "remissoes": "remissões",
    "submissao": "submissão", "submissoes": "submissões",
    "isencao": "isenção", "isencoes": "isenções",
    "concessao": "concessão", "concessoes": "concessões",
    "obtencao": "obtenção",
    "cessao": "cessão",
    "cessacao": "cessação",
    "destruicao": "destruição",
    "reconstrucao": "reconstrução",
    "produzao": "produção", "producao": "produção", "producoes": "produções",
    "reproducao": "reprodução",
    "imprensa": "imprensa",
    "presenca": "presença",
    "ausencia": "ausência",
    "transferencia": "transferência", "transferencias": "transferências",
    "preferencia": "preferência",
    "ocorrencia": "ocorrência", "ocorrencias": "ocorrências",
    "concorrencia": "concorrência",
    "experiencia": "experiência",

    # Vogais acentuadas comuns
    "saude": "saúde",
    "medico": "médico", "medicos": "médicos",
    "medica": "médica", "medicas": "médicas",
    "clinico": "clínico", "clinicos": "clínicos",
    "clinica": "clínica", "clinicas": "clínicas",
    "pratico": "prático", "praticos": "práticos",
    "pratica": "prática", "praticas": "práticas",
    "publico": "público", "publicos": "públicos",
    "publica": "pública", "publicas": "públicas",
    "tecnico": "técnico", "tecnicos": "técnicos",
    "tecnica": "técnica", "tecnicas": "técnicas",
    "minimo": "mínimo", "minimos": "mínimos",
    "minima": "mínima", "minimas": "mínimas",
    "maximo": "máximo", "maximos": "máximos",
    "maxima": "máxima", "maximas": "máximas",
    "rapido": "rápido", "rapidos": "rápidos",
    "rapida": "rápida", "rapidas": "rápidas",
    "basico": "básico", "basicos": "básicos",
    "basica": "básica", "basicas": "básicas",
    "unico": "único", "unicos": "únicos",
    "unica": "única", "unicas": "únicas",
    "ultimo": "último", "ultimos": "últimos",
    "ultima": "última", "ultimas": "últimas",
    "proximo": "próximo", "proximos": "próximos",
    "proxima": "próxima", "proximas": "próximas",
    "cronico": "crônico", "cronicos": "crônicos",
    "cronica": "crônica", "cronicas": "crônicas",
    "agudo": "agudo",
    "tipico": "típico", "tipicos": "típicos",
    "tipica": "típica", "tipicas": "típicas",
    "valido": "válido", "validos": "válidos",
    "valida": "válida", "validas": "válidas",
    "estatistico": "estatístico", "estatistica": "estatística",
    "automatico": "automático", "automatica": "automática",
    "logico": "lógico", "logica": "lógica",
    "fisico": "físico", "fisica": "física",
    "psiquico": "psíquico", "psiquica": "psíquica",
    "credito": "crédito", "creditos": "créditos",
    "metodo": "método", "metodos": "métodos",
    "objetivo": "objetivo",  # já correto

    # Palavras com til/circunflexo
    "nao": "não",
    "voce": "você", "voces": "vocês",
    "tambem": "também",
    "porem": "porém",
    "alem": "além",
    "atraves": "através",
    "pos": "pós",
    "ja": "já",
    "ate": "até",
    "so": "só",
    "tres": "três",
    "apos": "após",
    "esta": "está",  # ATENÇÃO: ambíguo (pronome demonstrativo vs verbo)
    "ele": "ele",
    "alguem": "alguém",
    "ninguem": "ninguém",
    "tem": "tem",  # ambíguo

    # Conectores e palavras frequentes
    "ha": "há",  # ambíguo
    "fim": "fim",
    "porque": "porque",
    "porcao": "porção",
    "numero": "número", "numeros": "números",
    "razao": "razão", "razoes": "razões",
    "missao": "missão", "missoes": "missões",
    "questao": "questão", "questoes": "questões",
    "padrao": "padrão", "padroes": "padrões",
    "ocupacao": "ocupação", "ocupacoes": "ocupações",
    "circunstancia": "circunstância", "circunstancias": "circunstâncias",
    "consciencia": "consciência",
    "diferenca": "diferença", "diferencas": "diferenças",
    "essencial": "essencial",
    "frequencia": "frequência", "frequente": "frequente",
    "consequencia": "consequência", "consequencias": "consequências",
    "agencia": "agência", "agencias": "agências",
    "urgencia": "urgência", "urgencias": "urgências",
    "emergencia": "emergência", "emergencias": "emergências",
    "tendencia": "tendência", "tendencias": "tendências",
    "incidencia": "incidência",
    "incumbencia": "incumbência",

    # Tecnologia / saúde frequentes no contexto
    "ambulatorial": "ambulatorial",
    "ambulatorio": "ambulatório", "ambulatorios": "ambulatórios",
    "consultorio": "consultório", "consultorios": "consultórios",
    "hospitalar": "hospitalar",
    "hospital": "hospital",
    "diaria": "diária", "diarias": "diárias",
    "semanal": "semanal",
    "mensal": "mensal",
    "anual": "anual",
    "necessario": "necessário", "necessaria": "necessária",
    "diagnostico": "diagnóstico", "diagnostica": "diagnóstica",
    "prognostico": "prognóstico", "prognostica": "prognóstica",
    "secretaria": "secretária", "secretarias": "secretárias",
    "preliminar": "preliminar",
    "permanencia": "permanência",
    "intercorrência": "intercorrência",
    "atendimento": "atendimento",
    "ja_existente": "já existente",  # composta — não match

    # ç (cedilha)
    "comecar": "começar",
    "comeca": "começa",
    "comecou": "começou",
    "comeco": "começo",
    "endereco": "endereço",
    "preco": "preço",
    "almoco": "almoço",
    "esforco": "esforço",
    "esforcar": "esforçar",
    "abracar": "abraçar",
    "lancar": "lançar",
    "lancamento": "lançamento",

    # Verbos comuns
    "tera": "terá",
    "fara": "fará",
    "passara": "passará",
    "sera": "será",
    "estara": "estará",
    "ira": "irá",
    "havera": "haverá",
    "podera": "poderá",
    "deverá": "deverá",  # já com acento
    "vira": "virá",  # ambíguo (vira = de virar)
    "encontrara": "encontrará",
    "afetara": "afetará",
    "estimulará": "estimulará",
    "balizara": "balizará",
    "balizar": "balizar",
    "facilitara": "facilitará",
    "tornaria": "tornaria",  # já correto

    # Outros comuns
    "combustivel": "combustível", "combustiveis": "combustíveis",
    "perfil": "perfil",
    "facil": "fácil", "faceis": "fáceis",
    "dificil": "difícil", "dificeis": "difíceis",
    "possivel": "possível", "possiveis": "possíveis",
    "impossivel": "impossível", "impossiveis": "impossíveis",
    "movel": "móvel", "moveis": "móveis",
    "imovel": "imóvel", "imoveis": "imóveis",
    "util": "útil", "uteis": "úteis",
    "inutil": "inútil", "inuteis": "inúteis",
    "fragil": "frágil",
    "agil": "ágil", "ageis": "ágeis",
    "facilmente": "facilmente",  # já correto
    "rapidamente": "rapidamente",  # já correto
    "dificultar": "dificultar",
    "agora": "agora",  # já correto
    "depois": "depois",  # já correto
    "ja_": "já",
    "duvida": "dúvida", "duvidas": "dúvidas",
    "epoca": "época", "epocas": "épocas",
    "historia": "história", "historias": "histórias",
    "vitima": "vítima", "vitimas": "vítimas",
    "tema": "tema",  # já correto
    "ideia": "ideia",  # já correto (acordo ortográfico 2009)
    "fenomeno": "fenômeno",
    "psicologico": "psicológico", "psicologica": "psicológica",
    "fisiologico": "fisiológico",
    "patologico": "patológico", "patologica": "patológica",
    "sintoma": "sintoma",  # já correto
    "alguns": "alguns",  # já correto
    "varias": "várias", "varios": "vários",
    "anteriores": "anteriores", "anterior": "anterior",  # já correto
    "vai": "vai",  # já correto
    "vao": "vão",
    "irao": "irão",
    "serao": "serão",
    "estarao": "estarão",
    "terao": "terão",
    "farao": "farão",
    "deverao": "deverão",
    "poderao": "poderão",
    "verao": "verão",
    "iniciario": "iniciário",
    "responsavel": "responsável", "responsaveis": "responsáveis",
    "tao": "tão",
    "obrigatorio": "obrigatório", "obrigatoria": "obrigatória",
    "voluntario": "voluntário", "voluntaria": "voluntária",
    "imediato": "imediato",  # já correto
    "semanario": "semanário",
    "saidas": "saídas", "saida": "saída",
    "entrada": "entrada", "entradas": "entradas",
    "estrategia": "estratégia", "estrategias": "estratégias",
    "estrategico": "estratégico",
    "categoria": "categoria",  # já correto
    "memoria": "memória", "memorias": "memórias",
    "vitoria": "vitória",
    "matria": "matéria",
    "materia": "matéria", "materias": "matérias",
    "criterio": "critério", "criterios": "critérios",
    "ministerio": "ministério",
    "comprometimento": "comprometimento",  # correto
    "compromisso": "compromisso",  # correto
}

# Padrões NUNCA aplicar (palavras que existem em português sem acento)
# Estas palavras estão no dicionário acima por ambiguidade — vamos confiar no contexto.
SKIP_PATTERNS: set[str] = {
    "esta", "tem", "vira", "ele",  # palavras 100% válidas sem acento em outros usos
}

# ---------------------------------------------------------------------------
# Regex
# ---------------------------------------------------------------------------

# espaço antes de pontuação — só dentro de palavras/frases, NÃO em listas markdown
# (não casa quando o caractere ANTES do espaço é início de linha, '-' ou '*')
_SPACE_BEFORE_PUNCT = re.compile(r"(?<=[a-zA-Z0-9áéíóúâêîôûãõàçñÁÉÍÓÚÂÊÎÔÛÃÕÀÇÑ\)\]\"'])\s+([,.;:!?])")
# múltiplos espaços
_MULTI_SPACE = re.compile(r" {2,}")
# ponto-e-vírgula seguido de letra minúscula em meio de frase corrente:
# o OCR confunde vírgula com ; em fontes antigas. Heurística: ; no meio
# de frase com letra minúscula depois → vírgula
_SEMICOLON_TO_COMMA = re.compile(r"([a-záéíóúâêîôûãõàçñ]) ?; ?(?=[a-záéíóúâêîôûãõàçñ])")
# "0" começo de palavra ASCII em meio de texto PT (artigo "O" confundido)
_ZERO_AS_O = re.compile(
    r"(?:^|(?<=[\s\(\.,;:!?]))0(?=\s+[A-ZÁÉÍÓÚÂÊÎÔÛÃÕÀÇ][a-záéíóúâêîôûãõàçñ])"
)


# ---------------------------------------------------------------------------
# Aplicação
# ---------------------------------------------------------------------------


def _apply_accent(match: re.Match[str], dictionary: dict[str, str]) -> str:
    word = match.group(0)
    lower = word.lower()
    if lower in SKIP_PATTERNS:
        return word
    repl = dictionary.get(lower)
    if not repl:
        return word
    # preserva casing: TUDO MAIÚSCULO, Capitalizado, ou tudo minúsculo
    if word.isupper():
        return repl.upper()
    if word[0].isupper():
        return repl[0].upper() + repl[1:]
    return repl


def fix_accents(text: str) -> str:
    # Build pattern: alternativas ordenadas por tamanho desc para evitar match parcial
    keys = sorted(ACCENT_MAP.keys(), key=len, reverse=True)
    pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in keys) + r")\b", re.IGNORECASE)
    return pattern.sub(lambda m: _apply_accent(m, ACCENT_MAP), text)


def fix_spaces_and_punct(text: str) -> str:
    text = _SPACE_BEFORE_PUNCT.sub(r"\1", text)
    text = _MULTI_SPACE.sub(" ", text)
    text = _SEMICOLON_TO_COMMA.sub(r"\1, ", text)
    return text


def fix_zero_as_o(text: str) -> str:
    return _ZERO_AS_O.sub("O", text)


def process_markdown(content: str) -> str:
    """Aplica todas as correções e retorna o texto pós-processado."""
    # Preserva blocos de código markdown — não toca neles
    code_blocks: list[str] = []

    def _stash(m: re.Match[str]) -> str:
        code_blocks.append(m.group(0))
        return f"\x00CODE{len(code_blocks)-1}\x00"

    text = re.sub(r"```.*?```", _stash, content, flags=re.DOTALL)
    text = re.sub(r"`[^`]+`", _stash, text)

    text = fix_accents(text)
    text = fix_spaces_and_punct(text)
    text = fix_zero_as_o(text)

    # Restaura blocos de código
    def _unstash(m: re.Match[str]) -> str:
        return code_blocks[int(m.group(1))]

    text = re.sub(r"\x00CODE(\d+)\x00", _unstash, text)
    return text


def merge_into_book(
    md_files: list[Path], target: Path, *, title: str = "Documento Consolidado"
) -> Path:
    """Concatena MDs num único arquivo com ToC."""
    parts: list[str] = []
    parts.append(f"# {title}\n\n")
    parts.append(f"*Documento consolidado de {len(md_files)} páginas/seções.*\n\n")
    parts.append("## Sumário\n\n")
    for i, md in enumerate(sorted(md_files), 1):
        anchor = re.sub(r"[^a-z0-9]+", "-", md.stem.lower()).strip("-")
        parts.append(f"{i}. [{md.stem}](#{anchor})\n")
    parts.append("\n---\n")

    for md in sorted(md_files):
        parts.append(f"\n\n## {md.stem}\n\n")
        parts.append(md.read_text(encoding="utf-8").strip())
        parts.append("\n\n---")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("".join(parts), encoding="utf-8")
    return target


# ---------------------------------------------------------------------------
# Public API alias
# ---------------------------------------------------------------------------
# `fix_text` é o nome canônico exposto via __init__.py — apontamos para a
# implementação histórica `process_markdown` para manter retrocompat.

fix_text = process_markdown
