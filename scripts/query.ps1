param(
  [Parameter(Mandatory = $true)]
  [string]$Title
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$templatePath = "templates/query.md"
$queriesDir = "wiki/queries"
$indexPath = "wiki/index.md"
$logPath = "wiki/log.md"

if (-not (Test-Path -LiteralPath $templatePath -PathType Leaf)) {
  throw "模板不存在: $templatePath"
}

if (-not (Test-Path -LiteralPath $queriesDir -PathType Container)) {
  throw "目录不存在: $queriesDir"
}

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$slug = ($Title.ToLowerInvariant() -replace "[^a-z0-9]+", "-").Trim("-")
if ([string]::IsNullOrWhiteSpace($slug)) {
  $slug = "untitled-query"
}
$fileName = "query-$stamp-$slug.md"
$targetPath = Join-Path $queriesDir $fileName

$content = Get-Content -Raw -LiteralPath $templatePath
$content = $content -replace "(?m)^#\s+查询模板\s*$", ("# 查询: " + $Title)
$content = $content -replace "(?m)^- id:\s*$", ("- id: query-" + $stamp)
$content = $content -replace "(?m)^- title:\s*$", ("- title: " + $Title)
$content = $content -replace "(?m)^- created_at:\s*$", ("- created_at: " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))
Set-Content -LiteralPath $targetPath -Value $content -Encoding UTF8

if (Test-Path -LiteralPath $indexPath -PathType Leaf) {
  $index = Get-Content -Raw -LiteralPath $indexPath
  if ($index -notmatch "(?m)^## 查询\s*$") {
    $index = $index.TrimEnd() + "`r`n`r`n## 查询`r`n"
  }
  $index = $index.TrimEnd() + "`r`n- [$fileName](queries/$fileName)`r`n"
  Set-Content -LiteralPath $indexPath -Value $index -Encoding UTF8
}

$logLine = "- 新建查询: [$fileName](queries/$fileName)"
if (Test-Path -LiteralPath $logPath -PathType Leaf) {
  Add-Content -LiteralPath $logPath -Value $logLine -Encoding UTF8
}

Write-Host "已创建: $targetPath"
