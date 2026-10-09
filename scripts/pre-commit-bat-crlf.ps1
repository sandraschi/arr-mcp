# Fleet: CRLF guard for Windows batch files (TRAPS_AND_PITFALLS.md #43).
# Copy to {repo}/scripts/pre-commit-bat-crlf.ps1 - used by .pre-commit-config.yaml local hook.
# AI file tools write LF; cmd.exe misparses LF-only .bat files with paren blocks.
# Check-only on purpose: fails with the one-line fix, never rewrites (no stash churn).

param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Files)

$bad = @()
foreach ($f in $Files) {
    if (-not (Test-Path -LiteralPath $f -PathType Leaf)) { continue }
    $raw = [IO.File]::ReadAllBytes($f)
    $lfTotal = 0
    $crlf = 0
    for ($i = 0; $i -lt $raw.Length; $i++) {
        if ($raw[$i] -eq 10) {
            $lfTotal++
            if ($i -gt 0 -and $raw[$i - 1] -eq 13) { $crlf++ }
        }
    }
    if ($lfTotal -gt $crlf) { $bad += $f }
}

if ($bad.Count -gt 0) {
    Write-Host 'LF-only batch file(s) detected - cmd.exe requires CRLF:' -ForegroundColor Red
    foreach ($b in $bad) { Write-Host "  $b" -ForegroundColor Yellow }
    Write-Host 'Fix one file: $t=[IO.File]::ReadAllText("FILE"); [IO.File]::WriteAllText("FILE",(($t -replace "`n","`r`n") -replace "`r`r`n","`r`n"))' -ForegroundColor DarkGray
    exit 1
}
