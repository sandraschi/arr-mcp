param(
    [switch]$Headless,
    [switch]$FrontendOnly,
    [switch]$BackendOnly,
    [switch]$NoBrowser
)

# --- Headless mode ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }

$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot
$BackendPort = 10938
$FrontendPort = 10939
$BackendModule = "arr_mcp"
$WebRoot = Join-Path $RepoRoot "webapp"

Write-Host "=== arr-mcp ===" -ForegroundColor Cyan

# --- Port zombie kill ---
foreach ($port in @($BackendPort, $FrontendPort)) {
    Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | ForEach-Object {
        Write-Host "  Killing zombie on :$port (PID $($_.OwningProcess))" -ForegroundColor Yellow
        Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}
Start-Sleep -Milliseconds 500

# --- Start backend ---
if (-not $FrontendOnly) {
    Write-Host "Starting backend on :$BackendPort ..." -ForegroundColor Yellow
    $backendProc = Start-Process pwsh -PassThru -WindowStyle $WindowStyle -ArgumentList @(
        "-NoProfile", "-Command", "uv run python -m $BackendModule"
    )

    # Health poll (up to 30s)
    $ok = $false
    for ($i = 0; $i -lt 30; $i++) {
        try {
            $r = Invoke-WebRequest -Uri "http://127.0.0.1:$BackendPort/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
            if ($r.StatusCode -eq 200) { $ok = $true; break }
        } catch {}
        Start-Sleep 1
    }
    if ($ok) {
        Write-Host "Backend ready on :$BackendPort" -ForegroundColor Green
    } else {
        Write-Host "WARN: backend health not confirmed after 30s" -ForegroundColor Yellow
    }
}

if ($BackendOnly) {
    Write-Host "Backend-only mode. Press Ctrl+C to stop."
    Wait-Process -Id $backendProc.Id
    exit
}

# --- Start frontend ---
if (-not $BackendOnly -and (Test-Path $WebRoot)) {
    Write-Host "Starting frontend on :$FrontendPort ..." -ForegroundColor Yellow
    if (-not (Test-Path (Join-Path $WebRoot "node_modules"))) {
        Push-Location $WebRoot
        npm install
        Pop-Location
    }
    $frontendProc = Start-Process pwsh -PassThru -WindowStyle $WindowStyle -ArgumentList @(
        "-NoProfile", "-Command", "npm run dev -- --port $FrontendPort"
    ) -WorkingDirectory $WebRoot

    # Open browser
    if (-not $NoBrowser) {
        Start-Sleep 3
        try { Start-Process "http://127.0.0.1:$FrontendPort" } catch {}
        Write-Host "Frontend at http://127.0.0.1:$FrontendPort" -ForegroundColor Green
    }
}

Write-Host "=== arr-mcp running ===" -ForegroundColor Cyan
Write-Host "Backend  : http://127.0.0.1:$BackendPort"
Write-Host "Frontend : http://127.0.0.1:$FrontendPort"

# Keep alive
try {
    while ($true) {
        Start-Sleep 5
        if ($null -ne $backendProc -and $backendProc.HasExited) {
            Write-Host "Backend exited! ($($backendProc.ExitCode))" -ForegroundColor Red
            break
        }
    }
} finally {
    if ($null -ne $backendProc -and -not $backendProc.HasExited) {
        Stop-Process -Id $backendProc.Id -Force -ErrorAction SilentlyContinue
    }
}
