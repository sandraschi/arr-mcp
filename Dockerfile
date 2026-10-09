# arr-mcp backend — FastMCP stdio/HTTP server over --http transport.
# Build: docker build -t arr-mcp .   Run: docker compose up arr-mcp
# Config via environment (see .env.example). Never bake .env into the image.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS base

WORKDIR /app

# Dependency layer (rebuilt only when pins change; uv.lock is committed).
COPY pyproject.toml uv.lock README.md ./
COPY src/ src/
RUN uv sync --frozen --no-dev

ENV ARR_MCP_TRANSPORT=http \
    ARR_MCP_HOST=0.0.0.0 \
    ARR_MCP_PORT=10938 \
    PYTHONUNBUFFERED=1

EXPOSE 10938

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:10938/api/health')"

CMD ["uv", "run", "--frozen", "--no-dev", "python", "-m", "arr_mcp", "--http", "--port", "10938"]
