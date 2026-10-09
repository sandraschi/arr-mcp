# arr-mcp dashboard — Vite dev server WITH proxy (/api + /mcp -> backend).
# The built dist/ has no proxy, so the container runs the dev server bound to
# 0.0.0.0; same-origin /api calls work from LAN/Tailscale tabs via CORS-allowed origins.
FROM node:22-alpine AS base

WORKDIR /app

COPY webapp/package.json webapp/package-lock.json ./
RUN npm ci

COPY webapp/ ./

ENV VITE_PORT=10939 \
    VITE_API_TARGET=http://arr-mcp:10938

EXPOSE 10939

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD wget -qO- http://127.0.0.1:10939/ > /dev/null

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "10939"]
