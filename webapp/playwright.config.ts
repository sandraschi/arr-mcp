import { defineConfig, devices } from "@playwright/test";

const backendPort = process.env.ARR_MCP_PORT || "10938";
const frontendPort = process.env.ARR_MCP_WEBAPP_PORT || "10939";
const backendUrl = `http://127.0.0.1:${backendPort}`;
const frontendUrl = `http://localhost:${frontendPort}`;

const backendCommand =
	process.platform === "win32"
		? `..\\.venv\\Scripts\\python.exe -m arr_mcp --http --port ${backendPort}`
		: `cd .. && uv run arr-mcp --http --port ${backendPort}`;

export default defineConfig({
	testDir: "./e2e",
	fullyParallel: true,
	forbidOnly: !!process.env.CI,
	retries: process.env.CI ? 2 : 0,
	workers: process.env.CI ? 1 : undefined,
	reporter: process.env.CI ? "github" : "html",
	use: {
		baseURL: frontendUrl,
		trace: "on-first-retry",
		screenshot: "only-on-failure",
	},
	projects: [
		{
			name: "chromium",
			use: { ...devices["Desktop Chrome"] },
		},
	],
	webServer: [
		{
			command: backendCommand,
			url: `${backendUrl}/api/health`,
			reuseExistingServer: !process.env.CI,
			timeout: 120_000,
			env: {
				...process.env,
				ARR_MCP_TRANSPORT: "http",
				ARR_MCP_HOST: "127.0.0.1",
				ARR_MCP_PORT: backendPort,
			},
		},
		{
			command: "npm run dev",
			url: frontendUrl,
			reuseExistingServer: !process.env.CI,
			timeout: 120_000,
		},
	],
});
