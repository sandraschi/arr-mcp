#Requires -Version 5.1
<#
.SYNOPSIS
Fleet PowerShell 5.1 gate (POWERSHELL_51_STANDARD.md).

Fails on: 5.1 parse errors in any .ps1, Requires-7 directives without a
fleet exemption, `pwsh` tokens in justfiles. Warns on justfiles without a
windows-shell line.

Must itself stay 5.1-parseable (it gates itself): no ??, ?., ternary,
&& chains, or -Parallel in this file.
#>
param(
    [string]$Path = ".",
    [string]$ExemptionsFile = ""
)

# Self-host under REAL 5.1: the 7.x grammar accepts 7-only syntax, which
# would false-pass every check below. powershell.exe ships with Windows,
# so it is always present on fleet machines (dev and naked alike).
if ($PSVersionTable.PSVersion.Major -ne 5) {
    $ps51 = Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
    if (-not (Test-Path -LiteralPath $ps51)) {
        Write-Host 'SKIP: powershell.exe (5.1) not found; 5.1 parse cannot be verified here.' -ForegroundColor Yellow
        exit 0
    }
    $fwd = @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $PSCommandPath, '-Path', $Path)
    if ($ExemptionsFile -ne '') {
        $fwd = $fwd + @('-ExemptionsFile', $ExemptionsFile)
    }
    & $ps51 @fwd
    exit $LASTEXITCODE
}

$ErrorActionPreference = 'Stop'
$failures = @()
$warnings = @()

$repoRoot = (Resolve-Path -LiteralPath $Path).Path
$repoLeaf = Split-Path $repoRoot -Leaf

if ($ExemptionsFile -eq '') {
    $ExemptionsFile = Join-Path (Split-Path $repoRoot -Parent) 'mcp-central-docs\operations\ps7-exemptions.json'
}
$exempted = @()
if (Test-Path -LiteralPath $ExemptionsFile) {
    try {
        $exData = Get-Content -LiteralPath $ExemptionsFile -Raw | ConvertFrom-Json
        foreach ($e in $exData.exemptions) {
            if ($e.file -ne $null -and $e.file -ne '') {
                $exempted = $exempted + $e.file
            }
        }
    } catch {
        $warnings = $warnings + ('EXEMPTIONS-UNREADABLE {0}' -f $ExemptionsFile)
    }
} else {
    $warnings = $warnings + ('EXEMPTIONS-MISSING {0} (treated as empty)' -f $ExemptionsFile)
}

$skipRe = '(?i)(node_modules|\.venv|\\venv\\|\\build_venv\\|\.git\\|\\target\\|\\dist\\|_scratch|/packages/|__pycache__|\.bak(\.|$))'

# --- 1. Parse every .ps1 under real 5.1 -------------------------------------
$psFiles = Get-ChildItem -LiteralPath $repoRoot -Recurse -Filter '*.ps1' -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch $skipRe }
foreach ($f in $psFiles) {
    $tokens = $null
    $errs = $null
    [void][System.Management.Automation.Language.Parser]::ParseFile($f.FullName, [ref]$tokens, [ref]$errs)
    foreach ($e in $errs) {
        $failures = $failures + ('PARSE {0}:{1} {2}' -f $f.FullName, $e.Extent.StartLineNumber, $e.Message)
    }
    $raw = [System.IO.File]::ReadAllText($f.FullName)
    $rel = $f.FullName.Substring($repoRoot.Length).TrimStart('\', '/') -replace '\\', '/'
    $key = "$repoLeaf/$rel"
    if ($raw -match '(?im)^\s*#requires\s+-version\s+7(\.0)?\s*($|#)') {
        if ($exempted -contains $key) {
            $warnings = $warnings + ('EXEMPTED-7 {0}' -f $key)
        } else {
            $failures = $failures + ('REQUIRES-7 {0} (downgrade to #Requires -Version 5.1 after 5.1-parse passes, or exempt in operations/ps7-exemptions.json)' -f $key)
        }
    }
    # No-BOM + non-ASCII bytes: 5.1 reads the file as Windows-1252, so UTF-8
    # multibyte sequences decode to smart quotes (0x92 -> U+2019 etc.) that
    # silently break string boundaries (2026-09-27: emoji in myai gemini_tools
    # produced 9 phantom parse errors). UTF-8 WITH BOM decodes correctly.
    $bytes = [System.IO.File]::ReadAllBytes($f.FullName)
    $hasBom = ($bytes.Count -ge 3 -and $bytes[0] -eq 239 -and $bytes[1] -eq 187 -and $bytes[2] -eq 191)
    if (-not $hasBom) {
        $hi = $false
        foreach ($b in $bytes) {
            if ($b -ge 128) {
                $hi = $true
                break
            }
        }
        if ($hi) {
            $warnings = $warnings + ('NOBOM-UTF8 {0} (non-ASCII bytes without UTF-8 BOM will misparse under 5.1 - save with BOM)' -f $key)
        }
    }
}

# --- 2. Justfiles: no pwsh, windows-shell present -----------------------------
$justExact = Get-ChildItem -LiteralPath $repoRoot -Recurse -Filter 'justfile' -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch $skipRe }
$justDotted = Get-ChildItem -LiteralPath $repoRoot -Recurse -Filter '*.just' -File -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notmatch $skipRe }
$justFiles = @($justExact) + @($justDotted)
foreach ($f in $justFiles) {
    $n = 0
    $hasShell = $false
    foreach ($line in [System.IO.File]::ReadAllLines($f.FullName)) {
        $n = $n + 1
        if ($line -match '^\s*#') {
            continue
        }
        if ($line -match '(?i)\bpwsh(\.exe)?\b') {
            $failures = $failures + ('PWSH {0}:{1} {2}' -f $f.FullName, $n, $line.Trim())
        }
        if ($line -match '(?i)^\s*set\s+windows-shell\s*:=') {
            $hasShell = $true
            if ($line -notmatch '(?i)powershell\.exe') {
                $failures = $failures + ('SHELL-NOT-51 {0}:{1} {2}' -f $f.FullName, $n, $line.Trim())
            }
        }
    }
    if (-not $hasShell -and $f.Name -eq 'justfile') {
        $warnings = $warnings + ('NO-WINDOWS-SHELL {0}' -f $f.FullName)
    }
}

# --- Report --------------------------------------------------------------------
foreach ($w in $warnings) {
    Write-Host ("WARN: " + $w) -ForegroundColor Yellow
}
if ($failures.Count -gt 0) {
    foreach ($fl in $failures) {
        Write-Host ("FAIL: " + $fl) -ForegroundColor Red
    }
    Write-Host ("ps51-gate: {0} failure(s), {1} warning(s)" -f $failures.Count, $warnings.Count) -ForegroundColor Red
    exit 1
}
Write-Host ("ps51-gate: PASS ({0} scripts, {1} justfiles, {2} warning(s))" -f $psFiles.Count, $justFiles.Count, $warnings.Count) -ForegroundColor Green
exit 0
