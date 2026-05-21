set windows-shell := ["pwsh.exe", "-NoLogo", "-Command"]

default:
    @pwsh.exe -NoProfile -ExecutionPolicy Bypass -File ../mcp-central-docs/scripts/just-dashboard.ps1 -Path .

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

lint:
    C:\Users\sandr\AppData\Local\Programs\Python\Python313\Scripts\ruff.exe check src/arr_mcp tests/
    C:\Users\sandr\AppData\Local\Programs\Python\Python313\Scripts\ruff.exe format src/arr_mcp tests/ --check

fix:
    C:\Users\sandr\AppData\Local\Programs\Python\Python313\Scripts\ruff.exe check src/arr_mcp tests/ --fix
    C:\Users\sandr\AppData\Local\Programs\Python\Python313\Scripts\ruff.exe format src/arr_mcp tests/

fmt:
    C:\Users\sandr\AppData\Local\Programs\Python\Python313\Scripts\ruff.exe format src/arr_mcp tests/

test:
    uv run pytest -v --cov=arr_mcp --cov-report=term-missing

ci: lint test
    cd webapp; npx @biomejs/biome check src/

clean:
    Get-ChildItem -Recurse -Include '__pycache__','*.pyc','.pytest_cache','.ruff_cache','.mypy_cache' -Path . | Remove-Item -Recurse -Force
