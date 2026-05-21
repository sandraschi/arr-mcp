param(
    [switch]$Rebuild,
    [switch]$Dev
)

$FrontendPort = 10939
$BackendPort = 10938
$Root = Split-Path -Parent $PSScriptRoot

# Clear port zombies
Get-NetTCPConnection -LocalPort $FrontendPort -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }

Write-Host "arr-mcp webapp — frontend :$FrontendPort" -ForegroundColor Cyan

Push-Location "$PSScriptRoot"

# Install dependencies if needed
if (-not (Test-Path node_modules) -or $Rebuild) {
    Write-Host "Installing npm dependencies..." -ForegroundColor Yellow
    npm install
}

# Start dev server
npm run dev

Pop-Location
