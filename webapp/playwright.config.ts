import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 15000,
  retries: 0,
  use: {
    baseURL: "http://localhost:10939",
    headless: true,
  },
  webServer: [
    {
      command: "uv run python -m arr_mcp",
      cwd: "..",
      port: 10938,
      timeout: 30000,
      reuseExistingServer: true,
      env: { ARR_MCP_TRANSPORT: "http", ARR_MCP_PORT: "10938" },
    },
    {
      command: "npm run dev",
      port: 10939,
      timeout: 30000,
      reuseExistingServer: true,
    },
  ],
});
