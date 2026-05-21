$Root = Split-Path -Parent $PSScriptRoot
$RepoName = "arr-mcp"
$BackendPath = "$PSScriptRoot\binaries"
$TargetTriple = "x86_64-pc-windows-msvc"

# Step 1: Build React frontend
Push-Location "$Root\webapp"
npm install
npm run build
Pop-Location

# Step 2: Build Python backend as standalone .exe
Push-Location "$Root"
& ".venv\Scripts\python.exe" -m PyInstaller `
    --onedir -y --clean `
    --name "${RepoName}-backend" `
    --add-data "src/${RepoName};${RepoName}" `
    --copy-metadata fastmcp --copy-metadata fastapi `
    --hidden-import uvicorn.logging `
    --hidden-import rich.logging `
    --hidden-import pydantic `
    run_server.py
Pop-Location

# Step 3: Copy sidecar binary for Tauri
New-Item -ItemType Directory -Force -Path $BackendPath
Copy-Item "$Root\dist\${RepoName}-backend\${RepoName}-backend.exe" `
    "$BackendPath\${RepoName}-backend-${TargetTriple}.exe" -Force

# Step 4: Build Tauri bundle
Push-Location $PSScriptRoot
npx @tauri-apps/cli build
Pop-Location
