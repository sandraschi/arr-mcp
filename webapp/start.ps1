param(
    [switch]$Rebuild,
    [switch]$NoBrowser

# Fast port helpers (scripts/PortHelpers.ps1)
param(
    [switch]$Rebuild,
    [switch]$NoBrowser
)

$FrontendPort = 10939
$BackendPort = 10938
$Root = Split-Path -Parent $PSScriptRoot

# Clear port zombies
Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }

Write-Host "arr-mcp - MCP server :$BackendPort | webapp :$FrontendPort" -ForegroundColor Cyan

# Start MCP backend in HTTP mode
$PythonExe = Join-Path $Root ".venv" | Join-Path -ChildPath "Scripts" | Join-Path -ChildPath "python.exe"
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:Root
    $env:ARR_MCP_TRANSPORT = "http"
    $env:ARR_MCP_HOST = "127.0.0.1"
    $env:ARR_MCP_PORT = $using:BackendPort
    try {
        & $using:PythonExe -m arr_mcp 2>&1
    } catch {
        # Try uv run as fallback
        uv run arr-mcp 2>&1
    }
}

Write-Host "Waiting for backend :$BackendPort..." -ForegroundColor Yellow
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:${BackendPort}/api/health" -TimeoutSec 2 -UseBasicParsing
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch { Start-Sleep -Seconds 1 }
}

if (-not $ready) {
    Write-Host "Backend failed to start - check logs" -ForegroundColor Red
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "Backend ready :$BackendPort" -ForegroundColor Green

# Install webapp deps if needed
Push-Location "$PSScriptRoot"
if (-not (Test-Path node_modules) -or $Rebuild) {
    Write-Host "Installing webapp dependencies..." -ForegroundColor Yellow
    npm install
}

# Start frontend dev server
npm run dev &
$frontendPid = $LASTEXITCODE

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

Pop-Location

Write-Host "arr-mcp running - Ctrl+C to stop" -ForegroundColor Green
Write-Host "  Dashboard:  http://localhost:$FrontendPort" -ForegroundColor Gray

try {
    while ($true) { Start-Sleep -Seconds 1 }
} finally {
    Write-Host "Shutting down..." -ForegroundColor Yellow
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
}
_RepoRootForPorts = Split-Path -Parent $PSScriptRoot
param(
    [switch]$Rebuild,
    [switch]$NoBrowser
)

$FrontendPort = 10939
$BackendPort = 10938
$Root = Split-Path -Parent $PSScriptRoot

# Clear port zombies
Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }

Write-Host "arr-mcp - MCP server :$BackendPort | webapp :$FrontendPort" -ForegroundColor Cyan

# Start MCP backend in HTTP mode
$PythonExe = Join-Path $Root ".venv" | Join-Path -ChildPath "Scripts" | Join-Path -ChildPath "python.exe"
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:Root
    $env:ARR_MCP_TRANSPORT = "http"
    $env:ARR_MCP_HOST = "127.0.0.1"
    $env:ARR_MCP_PORT = $using:BackendPort
    try {
        & $using:PythonExe -m arr_mcp 2>&1
    } catch {
        # Try uv run as fallback
        uv run arr-mcp 2>&1
    }
}

Write-Host "Waiting for backend :$BackendPort..." -ForegroundColor Yellow
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:${BackendPort}/api/health" -TimeoutSec 2 -UseBasicParsing
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch { Start-Sleep -Seconds 1 }
}

if (-not $ready) {
    Write-Host "Backend failed to start - check logs" -ForegroundColor Red
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "Backend ready :$BackendPort" -ForegroundColor Green

# Install webapp deps if needed
Push-Location "$PSScriptRoot"
if (-not (Test-Path node_modules) -or $Rebuild) {
    Write-Host "Installing webapp dependencies..." -ForegroundColor Yellow
    npm install
}

# Start frontend dev server
npm run dev &
$frontendPid = $LASTEXITCODE

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

Pop-Location

Write-Host "arr-mcp running - Ctrl+C to stop" -ForegroundColor Green
Write-Host "  Dashboard:  http://localhost:$FrontendPort" -ForegroundColor Gray

try {
    while ($true) { Start-Sleep -Seconds 1 }
} finally {
    Write-Host "Shutting down..." -ForegroundColor Yellow
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
}
_PortHelpers = Join-Path param(
    [switch]$Rebuild,
    [switch]$NoBrowser
)

$FrontendPort = 10939
$BackendPort = 10938
$Root = Split-Path -Parent $PSScriptRoot

# Clear port zombies
Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }

Write-Host "arr-mcp - MCP server :$BackendPort | webapp :$FrontendPort" -ForegroundColor Cyan

# Start MCP backend in HTTP mode
$PythonExe = Join-Path $Root ".venv" | Join-Path -ChildPath "Scripts" | Join-Path -ChildPath "python.exe"
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:Root
    $env:ARR_MCP_TRANSPORT = "http"
    $env:ARR_MCP_HOST = "127.0.0.1"
    $env:ARR_MCP_PORT = $using:BackendPort
    try {
        & $using:PythonExe -m arr_mcp 2>&1
    } catch {
        # Try uv run as fallback
        uv run arr-mcp 2>&1
    }
}

Write-Host "Waiting for backend :$BackendPort..." -ForegroundColor Yellow
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:${BackendPort}/api/health" -TimeoutSec 2 -UseBasicParsing
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch { Start-Sleep -Seconds 1 }
}

if (-not $ready) {
    Write-Host "Backend failed to start - check logs" -ForegroundColor Red
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "Backend ready :$BackendPort" -ForegroundColor Green

# Install webapp deps if needed
Push-Location "$PSScriptRoot"
if (-not (Test-Path node_modules) -or $Rebuild) {
    Write-Host "Installing webapp dependencies..." -ForegroundColor Yellow
    npm install
}

# Start frontend dev server
npm run dev &
$frontendPid = $LASTEXITCODE

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

Pop-Location

Write-Host "arr-mcp running - Ctrl+C to stop" -ForegroundColor Green
Write-Host "  Dashboard:  http://localhost:$FrontendPort" -ForegroundColor Gray

try {
    while ($true) { Start-Sleep -Seconds 1 }
} finally {
    Write-Host "Shutting down..." -ForegroundColor Yellow
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
}
_RepoRootForPorts 'scripts\PortHelpers.ps1'
if (Test-Path -LiteralPath param(
    [switch]$Rebuild,
    [switch]$NoBrowser
)

$FrontendPort = 10939
$BackendPort = 10938
$Root = Split-Path -Parent $PSScriptRoot

# Clear port zombies
Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }

Write-Host "arr-mcp - MCP server :$BackendPort | webapp :$FrontendPort" -ForegroundColor Cyan

# Start MCP backend in HTTP mode
$PythonExe = Join-Path $Root ".venv" | Join-Path -ChildPath "Scripts" | Join-Path -ChildPath "python.exe"
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:Root
    $env:ARR_MCP_TRANSPORT = "http"
    $env:ARR_MCP_HOST = "127.0.0.1"
    $env:ARR_MCP_PORT = $using:BackendPort
    try {
        & $using:PythonExe -m arr_mcp 2>&1
    } catch {
        # Try uv run as fallback
        uv run arr-mcp 2>&1
    }
}

Write-Host "Waiting for backend :$BackendPort..." -ForegroundColor Yellow
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:${BackendPort}/api/health" -TimeoutSec 2 -UseBasicParsing
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch { Start-Sleep -Seconds 1 }
}

if (-not $ready) {
    Write-Host "Backend failed to start - check logs" -ForegroundColor Red
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "Backend ready :$BackendPort" -ForegroundColor Green

# Install webapp deps if needed
Push-Location "$PSScriptRoot"
if (-not (Test-Path node_modules) -or $Rebuild) {
    Write-Host "Installing webapp dependencies..." -ForegroundColor Yellow
    npm install
}

# Start frontend dev server
npm run dev &
$frontendPid = $LASTEXITCODE

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

Pop-Location

Write-Host "arr-mcp running - Ctrl+C to stop" -ForegroundColor Green
Write-Host "  Dashboard:  http://localhost:$FrontendPort" -ForegroundColor Gray

try {
    while ($true) { Start-Sleep -Seconds 1 }
} finally {
    Write-Host "Shutting down..." -ForegroundColor Yellow
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
}
_PortHelpers) { . param(
    [switch]$Rebuild,
    [switch]$NoBrowser
)

$FrontendPort = 10939
$BackendPort = 10938
$Root = Split-Path -Parent $PSScriptRoot

# Clear port zombies
Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }

Write-Host "arr-mcp - MCP server :$BackendPort | webapp :$FrontendPort" -ForegroundColor Cyan

# Start MCP backend in HTTP mode
$PythonExe = Join-Path $Root ".venv" | Join-Path -ChildPath "Scripts" | Join-Path -ChildPath "python.exe"
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:Root
    $env:ARR_MCP_TRANSPORT = "http"
    $env:ARR_MCP_HOST = "127.0.0.1"
    $env:ARR_MCP_PORT = $using:BackendPort
    try {
        & $using:PythonExe -m arr_mcp 2>&1
    } catch {
        # Try uv run as fallback
        uv run arr-mcp 2>&1
    }
}

Write-Host "Waiting for backend :$BackendPort..." -ForegroundColor Yellow
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:${BackendPort}/api/health" -TimeoutSec 2 -UseBasicParsing
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch { Start-Sleep -Seconds 1 }
}

if (-not $ready) {
    Write-Host "Backend failed to start - check logs" -ForegroundColor Red
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "Backend ready :$BackendPort" -ForegroundColor Green

# Install webapp deps if needed
Push-Location "$PSScriptRoot"
if (-not (Test-Path node_modules) -or $Rebuild) {
    Write-Host "Installing webapp dependencies..." -ForegroundColor Yellow
    npm install
}

# Start frontend dev server
npm run dev &
$frontendPid = $LASTEXITCODE

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

Pop-Location

Write-Host "arr-mcp running - Ctrl+C to stop" -ForegroundColor Green
Write-Host "  Dashboard:  http://localhost:$FrontendPort" -ForegroundColor Gray

try {
    while ($true) { Start-Sleep -Seconds 1 }
} finally {
    Write-Host "Shutting down..." -ForegroundColor Yellow
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
}
_PortHelpers }
)

$FrontendPort = 10939
$BackendPort = 10938
$Root = Split-Path -Parent $PSScriptRoot

# Clear port zombies
Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }

Write-Host "arr-mcp - MCP server :$BackendPort | webapp :$FrontendPort" -ForegroundColor Cyan

# Start MCP backend in HTTP mode
$PythonExe = Join-Path $Root ".venv" | Join-Path -ChildPath "Scripts" | Join-Path -ChildPath "python.exe"
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:Root
    $env:ARR_MCP_TRANSPORT = "http"
    $env:ARR_MCP_HOST = "127.0.0.1"
    $env:ARR_MCP_PORT = $using:BackendPort
    try {
        & $using:PythonExe -m arr_mcp 2>&1
    } catch {
        # Try uv run as fallback
        uv run arr-mcp 2>&1
    }
}

Write-Host "Waiting for backend :$BackendPort..." -ForegroundColor Yellow
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://127.0.0.1:${BackendPort}/api/health" -TimeoutSec 2 -UseBasicParsing
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch { Start-Sleep -Seconds 1 }
}

if (-not $ready) {
    Write-Host "Backend failed to start - check logs" -ForegroundColor Red
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "Backend ready :$BackendPort" -ForegroundColor Green

# Install webapp deps if needed
Push-Location "$PSScriptRoot"
if (-not (Test-Path node_modules) -or $Rebuild) {
    Write-Host "Installing webapp dependencies..." -ForegroundColor Yellow
    npm install
}

# Start frontend dev server
npm run dev &
$frontendPid = $LASTEXITCODE

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

Pop-Location

Write-Host "arr-mcp running - Ctrl+C to stop" -ForegroundColor Green
Write-Host "  Dashboard:  http://localhost:$FrontendPort" -ForegroundColor Gray

try {
    while ($true) { Start-Sleep -Seconds 1 }
} finally {
    Write-Host "Shutting down..." -ForegroundColor Yellow
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Get-NetTCPConnection -LocalPort $BackendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
}

