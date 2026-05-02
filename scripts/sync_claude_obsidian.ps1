<#
.SYNOPSIS
  Sincroniza chats exportados do Claude Code/Web para o vault Obsidian.

.DESCRIPTION
  Substitui o sync_claude_obsidian.sh do guia (que é bash/Linux).
  1) Exporta novos chats do Claude Code via claude-extract.
  2) Roda o pós-processador Python (claude_to_obsidian.py).
  3) Loga resultado em sync.log.

.NOTES
  Pode ser agendado pelo Task Scheduler do Windows. Veja README ou
  vault/projeto/decisoes.md para o script de agendamento.

  O claude-conversation-extractor (claude-extract) precisa estar instalado:
    pip install claude-conversation-extractor
#>

[CmdletBinding()]
param(
    [switch]$Move,
    [switch]$DryRun,
    [switch]$NoExtract  # pula a etapa de extração (útil se já tem chats em claude-exports/web/)
)

$ErrorActionPreference = 'Continue'

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

$proj      = "C:\Users\jacks\OneDrive\2º Cérebro\Scanner de imagens"
$exportDir = Join-Path $proj 'claude-exports'
$vaultDir  = Join-Path $proj 'vault'
$pyScript  = Join-Path $proj 'scripts\claude_to_obsidian.py'
$logFile   = Join-Path $proj 'scripts\sync.log'

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

function Write-Log {
    param([string]$Message, [string]$Level = 'INFO')
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    $line = "[$timestamp] [$Level] $Message"
    Write-Host $line
    Add-Content -Path $logFile -Value $line -Encoding UTF8
}

function Test-Tool {
    param([string]$Name)
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    return [bool]$cmd
}

# ---------------------------------------------------------------------------
# Pré-flight
# ---------------------------------------------------------------------------

Write-Log "===== Sync iniciado ====="
Write-Log "Projeto: $proj"

if (-not (Test-Path $vaultDir)) {
    Write-Log "vault-dir não existe: $vaultDir" 'ERROR'
    exit 2
}

if (-not (Test-Path $pyScript)) {
    Write-Log "claude_to_obsidian.py não existe: $pyScript" 'ERROR'
    exit 2
}

New-Item -ItemType Directory -Force -Path "$exportDir\code" | Out-Null
New-Item -ItemType Directory -Force -Path "$exportDir\web" | Out-Null

# ---------------------------------------------------------------------------
# 1) Export do Claude Code
# ---------------------------------------------------------------------------

if (-not $NoExtract) {
    if (Test-Tool 'claude-extract') {
        Write-Log "Exportando chats do Claude Code..."
        try {
            claude-extract --all --output (Join-Path $exportDir 'code') 2>&1 |
                ForEach-Object { Write-Log "  $_" 'EXTRACT' }
        } catch {
            Write-Log "claude-extract falhou: $_" 'WARN'
        }
    } else {
        Write-Log "claude-extract não encontrado no PATH. Instale com: pip install claude-conversation-extractor" 'WARN'
        Write-Log "Pulando extração — arquivos manuais em $exportDir\web ainda serão processados."
    }
} else {
    Write-Log "Etapa de extração pulada (--NoExtract)"
}

# ---------------------------------------------------------------------------
# 2) Pós-processamento Python
# ---------------------------------------------------------------------------

$pyArgs = @(
    $pyScript,
    '--export-dir', $exportDir,
    '--vault-dir',  $vaultDir
)
if ($Move)   { $pyArgs += '--move' }
if ($DryRun) { $pyArgs += '--dry-run' }

Write-Log "Rodando: python $($pyArgs -join ' ')"
try {
    python @pyArgs 2>&1 | ForEach-Object { Write-Log "  $_" 'PYTHON' }
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        Write-Log "claude_to_obsidian.py retornou exit=$exitCode" 'WARN'
    }
} catch {
    Write-Log "Erro ao rodar Python: $_" 'ERROR'
    exit 3
}

# ---------------------------------------------------------------------------
# 3) Resumo
# ---------------------------------------------------------------------------

$chatCount = (Get-ChildItem -Path (Join-Path $vaultDir 'chats') -Recurse -Filter '*.md' -ErrorAction SilentlyContinue).Count
Write-Log "Total de chats no vault: $chatCount"
Write-Log "===== Sync concluído ====="
