# arr-mcp starter
param([switch]$BackendOnly)
$ErrorActionPreference = "Stop"
$Repo = $PSScriptRoot
$UV = "C:\Users\sandr\.local\bin\uv.exe"
Write-Host "=== arr-mcp ===" -ForegroundColor Cyan
& $UV run python -m arr_mcp
