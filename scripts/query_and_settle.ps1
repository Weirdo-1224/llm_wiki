param(
  [Parameter(Mandatory = $true)]
  [string]$Title
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Test-Path -LiteralPath "scripts/query.ps1" -PathType Leaf)) {
  throw "Missing script: scripts/query.ps1"
}
if (-not (Test-Path -LiteralPath "scripts/lint.ps1" -PathType Leaf)) {
  throw "Missing script: scripts/lint.ps1"
}

# 1) Create query page
powershell -ExecutionPolicy Bypass -File "scripts/query.ps1" -Title $Title

# 2) Locate latest query
$latest = Get-ChildItem -LiteralPath "wiki/queries" -File -Filter "query-*.md" |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

if ($null -eq $latest) {
  throw "No new query file found."
}

# 3) Ask Codex to answer and settle
$prompt = @"
Follow AGENTS.md strictly and complete answer-and-settle workflow:
1. Read wiki/index.md first.
2. Focus on this query file: $($latest.FullName)
3. Answer the question and write the result to section '???????'.
4. If needed, create or update a page in wiki/syntheses/ for reusable synthesis.
5. Update wiki/index.md and wiki/log.md.
6. All new/updated Markdown headings and body text must be Chinese; id/path/commands/code blocks may stay English.
7. Distinguish facts, interpretations, and open questions; if conflicting with older claims, add conflict/revision notes.
8. Output changed file list and next suggestions.
"@

try {
  codex exec $prompt
} catch {
  throw "codex exec failed. Please fix local Codex config and retry. Original error: $($_.Exception.Message)"
}

# 4) Run lint
powershell -ExecutionPolicy Bypass -File "scripts/lint.ps1"

Write-Host "Done: query answered, settled, and linted."
