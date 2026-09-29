FROM python:3.12-slim AS build

WORKDIR /build
COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip wheel --no-cache-dir --wheel-dir /wheels .

FROM python:3.12-slim

COPY --from=build /wheels /wheels
RUN python -m pip install --no-cache-dir /wheels/*.whl \
    && rm -rf /wheels \
    && useradd --uid 10001 --create-home --shell /usr/sbin/nologin app

USER 10001:10001
ENV PYTHONUNBUFFERED=1 \
    ARR_MCP_TRANSPORT=http \
    ARR_MCP_HOST=0.0.0.0 \
    ARR_MCP_PORT=10938

EXPOSE 10938
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:10938/api/diagnostics', timeout=3).close()"
CMD ["arr-mcp"]
