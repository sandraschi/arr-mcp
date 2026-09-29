// Minimal MCP streamable-HTTP client for the webapp.
// FastMCP 3.4 requires an initialize handshake + Mcp-Session-Id header on every
// request; bare JSON-RPC POSTs fail with "Missing session ID". Responses are
// SSE-formatted (event: message / data: {...}).

import { API_BASE } from "./api";

const MCP_URL = `${API_BASE}/mcp`;

let sessionId: string | null = null;
let sessionPromise: Promise<string> | null = null;

const JSON_HEADERS = {
  "Content-Type": "application/json",
  Accept: "application/json, text/event-stream",
};

async function ensureSession(): Promise<string> {
  if (sessionId) return sessionId;
  if (!sessionPromise) {
    sessionPromise = (async () => {
      const init = await fetch(MCP_URL, {
        method: "POST",
        headers: JSON_HEADERS,
        body: JSON.stringify({
          jsonrpc: "2.0",
          id: 1,
          method: "initialize",
          params: {
            protocolVersion: "2025-11-25",
            capabilities: {},
            clientInfo: { name: "arr-webapp", version: "0.1.0" },
          },
        }),
      });
      sessionId = init.headers.get("Mcp-Session-Id") || init.headers.get("mcp-session-id");
      if (!sessionId) throw new Error("MCP session negotiation failed");
      await fetch(MCP_URL, {
        method: "POST",
        headers: { ...JSON_HEADERS, "Mcp-Session-Id": sessionId },
        body: JSON.stringify({ jsonrpc: "2.0", method: "notifications/initialized" }),
      });
      return sessionId;
    })();
  }
  return sessionPromise;
}

function parseSse(text: string): any {
  let parsed: any = null;
  for (const line of text.split(/\r?\n/)) {
    if (line.startsWith("data: ")) {
      const payload = line.slice(6).trim();
      if (payload) {
        try { parsed = JSON.parse(payload); } catch { /* keep last valid */ }
      }
    }
  }
  if (parsed !== null) return parsed;
  try { return JSON.parse(text); } catch { return null; }
}

export async function mcpRequest(method: string, params: unknown, timeoutMs = 15000): Promise<any> {
  const sid = await ensureSession();
  const r = await fetch(MCP_URL, {
    method: "POST",
    headers: { ...JSON_HEADERS, "Mcp-Session-Id": sid },
    body: JSON.stringify({ jsonrpc: "2.0", id: Date.now(), method, params: params ?? {} }),
    signal: AbortSignal.timeout(timeoutMs),
  });
  const text = await r.text();
  const data = parseSse(text);
  if (data?.error) throw new Error(data.error.message || JSON.stringify(data.error));
  return data?.result;
}

export async function callTool(name: string, args: Record<string, unknown>): Promise<any> {
  const result = await mcpRequest("tools/call", { name, arguments: args });
  const content: Array<{ type?: string; text?: string }> = result?.content ?? [];
  for (const block of content) {
    if (block && typeof block.text === "string") {
      try { return JSON.parse(block.text); } catch { return block.text; }
    }
  }
  return result;
}
