import { expect, test } from "@playwright/test";

test.describe("Help page", () => {
	test("shows setup guide and expandable tool reference", async ({ page }) => {
		await page.goto("/help");
		await expect(page.getByRole("heading", { name: "Help" })).toBeVisible();
		await expect(page.getByText("What is arr-mcp?")).toBeVisible();
		await expect(page.getByText("Docker Compose — Full *Arr Stack")).toBeVisible();
		await page.getByRole("button", { name: /MCP Tool Reference/ }).click();
		await expect(page.getByText("radarr_movies")).toBeVisible();
		await expect(page.getByText("arr_orchestrate")).toBeVisible();
	});
});

test.describe("Settings page", () => {
	test("checks backend health", async ({ page }) => {
		await page.goto("/settings");
		await expect(page.getByRole("heading", { name: "Settings" })).toBeVisible();
		await page.getByRole("button", { name: "Check" }).click();
		await expect(page.getByText(/Connected|not configured|Unreachable/)).toBeVisible({ timeout: 15_000 });
	});

	test("shows arr port reference", async ({ page }) => {
		await page.goto("/settings");
		await expect(page.getByText(":7878")).toBeVisible();
		await expect(page.getByText(":8989")).toBeVisible();
	});
});

test.describe("Logger page", () => {
	test("loads log viewer controls", async ({ page }) => {
		await page.goto("/logger");
		await expect(page.getByRole("heading", { name: "Logger" })).toBeVisible();
		await expect(page.getByPlaceholder("Filter...")).toBeVisible();
	});
});

test.describe("Orchestrate page", () => {
	test("shows pipeline overview", async ({ page }) => {
		await page.goto("/orchestrate");
		await expect(page.getByRole("heading", { name: "Orchestrate" })).toBeVisible();
		await expect(page.getByText("Jellyfin Check")).toBeVisible();
		await expect(page.getByText("Type Detection")).toBeVisible();
	});
});

test.describe("Chat page", () => {
	test("shows chat interface", async ({ page }) => {
		await page.goto("/chat");
		await expect(page.getByRole("heading", { name: "Chat" })).toBeVisible();
		await expect(page.getByPlaceholder("Configure an LLM in Settings first...")).toBeVisible();
	});
});
