param(
    [switch]$NoBrowser
)

$BackendPort = 10938
$FrontendPort = 10939
$Root = Split-Path -Parent $PSScriptRoot

# Clear port zombies
Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }

Write-Host "arr-mcp — MCP server :$BackendPort | webapp :$FrontendPort" -ForegroundColor Cyan

# Start MCP backend
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:Root
    $env:ARR_MCP_TRANSPORT = "http"
    $env:ARR_MCP_HOST = "127.0.0.1"
    $env:ARR_MCP_PORT = $using:BackendPort
    & "$using:Root\.venv\Scripts\python.exe" -m arr_mcp 2>&1
}

Write-Host "Waiting for backend :$BackendPort..." -ForegroundColor Yellow
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:${BackendPort}/health" -TimeoutSec 2 -UseBasicParsing
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch { Start-Sleep -Seconds 1 }
}

if (-not $ready) {
    Write-Host "Backend failed to start — check logs" -ForegroundColor Red
    Stop-Job $backendJob
    exit 1
}

Write-Host "Backend ready :$BackendPort" -ForegroundColor Green

# Start webapp (npm dev) in background
Push-Location "$Root\webapp"
if (-not (Test-Path node_modules)) {
    Write-Host "Installing webapp deps..." -ForegroundColor Yellow
    npm install
}
$webappJob = Start-Job -ScriptBlock {
    Set-Location "$using:Root\webapp"
    npm run dev 2>&1
}
Pop-Location

# Wait for frontend
Write-Host "Waiting for webapp :$FrontendPort..." -ForegroundColor Yellow
$frontendReady = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:${FrontendPort}" -TimeoutSec 2 -UseBasicParsing
        if ($r.StatusCode -eq 200) { $frontendReady = $true; break }
    } catch { Start-Sleep -Seconds 1 }
}

if ($frontendReady -and -not $NoBrowser) {
    Start-Process "http://localhost:${FrontendPort}"
}

Write-Host "arr-mcp running — Ctrl+C to stop" -ForegroundColor Green
Write-Host "  MCP Server: http://localhost:$BackendPort/mcp" -ForegroundColor Gray
Write-Host "  Dashboard:  http://localhost:$FrontendPort" -ForegroundColor Gray

# Wait for user interrupt
try {
    while ($true) { Start-Sleep -Seconds 1 }
} finally {
    Write-Host "Shutting down..." -ForegroundColor Yellow
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Stop-Job $webappJob -ErrorAction SilentlyContinue
    Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
}
