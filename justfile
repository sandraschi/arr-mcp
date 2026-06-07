set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

default:
    @just --list

version:
    uv run python -c "from arr_mcp import __version__; print(__version__)"

install:
    uv sync
    uv run pre-commit install

start:
    uv run arr-mcp

webapp:
    powershell webapp/start.ps1

build-webapp:
    cd webapp; npm run build

lint-webapp:
    cd webapp; npx @biomejs/biome check src/

fix-webapp:
    cd webapp; npx @biomejs/biome check src/ --write

build-native:
    Set-Location '{{justfile_directory()}}\native'
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    .\build.ps1

build-native-debug:
    Set-Location '{{justfile_directory()}}\native'
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    npx @tauri-apps/cli build --debug

tauri-sidecar:
    pwsh -NoLogo -File '{{justfile_directory()}}\native\build-sidecar.ps1'

tauri-build:
    Set-Location '{{justfile_directory()}}\native'
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    .\build.ps1

tauri-dev:
    Set-Location '{{justfile_directory()}}\native'
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    npm install
    npx @tauri-apps/cli dev

lint:
    uv run ruff check src/arr_mcp tests/
    uv run ruff format src/arr_mcp tests/ --check

typecheck:
    uv run mypy

fix:
    uv run ruff check src/arr_mcp tests/ --fix
    uv run ruff format src/arr_mcp tests/

fmt:
    uv run ruff format src/arr_mcp tests/

test:
    uv run pytest -v --cov=arr_mcp --cov-report=term-missing

e2e:
    Set-Location '{{justfile_directory()}}\webapp'
    npm run test:e2e

e2e-ui:
    Set-Location '{{justfile_directory()}}\webapp'
    npm run test:e2e:ui

ci: lint typecheck test
    cd webapp; npx @biomejs/biome check src/
    cd webapp; npx tsc -b
    cd webapp; npm run build

clean:
    Get-ChildItem -Recurse -Include '__pycache__','*.pyc','.pytest_cache','.ruff_cache','.mypy_cache' -Path . | Remove-Item -Recurse -Force

