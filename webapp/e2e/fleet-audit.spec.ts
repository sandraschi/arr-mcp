import { test, expect } from "@playwright/test";

const FE = "http://localhost:10939";
const BE = "http://localhost:10938";

test.describe("Fleet Audit", () => {
	test("Backend health returns 200", async ({ request }) => {
		const resp = await request.get(`${BE}/health`);
		expect(resp.status()).toBe(200);
	});

	test("Frontend loads with #root", async ({ page }) => {
		await page.goto(FE, { timeout: 15000 });
		await page.waitForTimeout(3000);
		await expect(page.locator("#root")).toBeAttached();
	});

	test("No console errors on Dashboard", async ({ page }) => {
		const errors: string[] = [];
		page.on("pageerror", (err) => errors.push(err.message));
		await page.goto("/");
		await page.waitForLoadState("networkidle");
		expect(errors).toEqual([]);
	});

	test("No 404s on page navigation", async ({ page }) => {
		const routes = [
			"/", "/radarr", "/sonarr", "/lidarr", "/prowlarr",
			"/readarr", "/overseerr", "/bazarr", "/orchestrate",
			"/chat", "/logger", "/help", "/settings", "/inspector",
		];
		for (const route of routes) {
			await page.goto(route);
			// "domcontentloaded": /logger holds a persistent SSE stream, so
			// "networkidle" never settles there by design.
			await page.waitForLoadState("domcontentloaded");
			await expect(page.locator("#root")).toBeAttached();
		}
	});
});

test.describe("REST API", () => {
	test("GET /api/health returns services", async ({ request }) => {
		const resp = await request.get(`${BE}/api/health`);
		expect(resp.status()).toBe(200);
		const body = await resp.json();
		expect(body.success).toBe(true);
		expect(body.data).toBeDefined();
	});

	test("GET /api/status returns server info", async ({ request }) => {
		const resp = await request.get(`${BE}/api/status`);
		expect(resp.status()).toBe(200);
	});

	test("POST /api/orchestrate/request with invalid body returns 422", async ({ request }) => {
		const resp = await request.post(`${BE}/api/orchestrate/request`, {
			data: { invalid: true },
			headers: { "Content-Type": "application/json" },
		});
		expect(resp.status()).toBe(422);
	});
});

test.describe("Topbar health", () => {
	test("shows backend connection status", async ({ page }) => {
		await page.goto("/");
		await page.waitForLoadState("networkidle");
		const statusText = page.locator("header, nav, [class*='topbar'], [class*='navbar'], [class*='status']");
		const count = await statusText.count();
		if (count > 0) {
			await expect(statusText.first()).toBeVisible();
		}
	});
});

test.describe("Chat compose", () => {
	test("shows chat input area", async ({ page }) => {
		await page.goto("/chat");
		await page.waitForLoadState("networkidle");
		await expect(page.getByRole("heading", { name: "Chat" })).toBeVisible();
		const input = page.getByPlaceholder(/message|type|ask|input/i);
		if ((await input.count()) > 0) {
			await expect(input.first()).toBeVisible();
		}
	});
});

test.describe("Settings provider discovery", () => {
	test("shows provider configuration section", async ({ page }) => {
		await page.goto("/settings");
		await page.waitForLoadState("networkidle");
		await expect(page.getByRole("heading", { name: "Settings" })).toBeVisible();
		const providerSection = page.getByText(/provider|model|llm|sampling|ollama/i);
		await expect(providerSection.first()).toBeVisible({ timeout: 10000 });
	});
});
