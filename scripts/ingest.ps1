Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$inboxDir = "raw/inbox"
$processedDir = "raw/processed"
$sourcesDir = "wiki/sources"
$templatePath = "templates/source.md"
$indexPath = "wiki/index.md"
$logPath = "wiki/log.md"

$required = @($inboxDir, $processedDir, $sourcesDir, $templatePath, $indexPath, $logPath)
foreach ($path in $required) {
  if (-not (Test-Path -LiteralPath $path)) {
    throw "缺少必要路径: $path"
  }
}

$candidate = Get-ChildItem -LiteralPath $inboxDir -File | Sort-Object Name | Select-Object -First 1
if ($null -eq $candidate) {
  Write-Host "raw/inbox 中没有可处理文件。"
  exit 0
}

$existing = Get-ChildItem -LiteralPath $sourcesDir -File -Filter "source-*.md"
$maxId = 0
foreach ($file in $existing) {
  if ($file.BaseName -match "^source-(\d+)$") {
    $id = [int]$matches[1]
    if ($id -gt $maxId) { $maxId = $id }
  }
}

$nextId = $maxId + 1
$sourceId = ("source-{0:D4}" -f $nextId)
$sourceFile = "$sourceId.md"
$sourcePath = Join-Path $sourcesDir $sourceFile

$title = [System.IO.Path]::GetFileNameWithoutExtension($candidate.Name)
$sourceContent = Get-Content -Raw -LiteralPath $templatePath
$sourceContent = $sourceContent -replace "(?m)^#\s+来源模板\s*$", ("# " + $sourceId + ": " + $title)
$sourceContent = $sourceContent -replace "(?m)^- id:\s*$", ("- id: " + $sourceId)
$sourceContent = $sourceContent -replace "(?m)^- title:\s*$", ("- title: " + $title)
$sourceContent = $sourceContent -replace "(?m)^- type:\s*.*$", "- type: note"
$sourceContent = $sourceContent -replace "(?m)^- created_at:\s*$", ("- created_at: " + (Get-Date -Format "yyyy-MM-dd"))
$sourceContent = $sourceContent -replace "(?m)^- accessed_at:\s*$", ("- accessed_at: " + (Get-Date -Format "yyyy-MM-dd"))
$sourceContent = $sourceContent -replace "(?m)^- tags:\s*$", "- tags: [ingested]"
Set-Content -LiteralPath $sourcePath -Value $sourceContent -Encoding UTF8

$sourceLink = "- [$sourceId](sources/$sourceFile)"
$indexContent = Get-Content -Raw -LiteralPath $indexPath
if ($indexContent -notmatch [regex]::Escape($sourceLink)) {
  if ($indexContent -match "(?m)^## 来源\s*$") {
    $indexContent = [regex]::Replace($indexContent, "(?m)^## 来源\s*$", "## 来源`r`n$sourceLink", 1)
  } else {
    $indexContent = $indexContent.TrimEnd() + "`r`n`r`n## 来源`r`n$sourceLink`r`n"
  }
  Set-Content -LiteralPath $indexPath -Value $indexContent -Encoding UTF8
}

$processedPath = Join-Path $processedDir $candidate.Name
if (Test-Path -LiteralPath $processedPath) {
  $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
  $processedPath = Join-Path $processedDir ("$timestamp-" + $candidate.Name)
}
Move-Item -LiteralPath $candidate.FullName -Destination $processedPath

$logLine = "- 已摄取 `$($candidate.Name)` -> [${sourceId}](sources/$sourceFile)"
Add-Content -LiteralPath $logPath -Value $logLine -Encoding UTF8

Write-Host "已摄取: $($candidate.Name)"
Write-Host "已创建: $sourcePath"
Write-Host "已移动到: $processedPath"
