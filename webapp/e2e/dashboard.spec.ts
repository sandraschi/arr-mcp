import { expect, test } from "@playwright/test";

const services = ["Radarr", "Sonarr", "Lidarr", "Prowlarr", "Readarr", "Overseerr", "Bazarr"];

test.describe("Dashboard", () => {
	test.beforeEach(async ({ page }) => {
		await page.goto("/");
	});

	test("loads health cards for all services", async ({ page }) => {
		await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
		for (const service of services) {
			await expect(page.getByRole("heading", { name: service, exact: true })).toBeVisible();
		}
	});

	test("shows stack reachability summary", async ({ page }) => {
		await expect(page.getByText(/\d+\/7 reachable/)).toBeVisible({ timeout: 15_000 });
	});

	test("renders health JSON panel", async ({ page }) => {
		await expect(page.getByRole("heading", { name: "Health JSON" })).toBeVisible({ timeout: 15_000 });
		await expect(page.locator("pre").filter({ hasText: "radarr" })).toBeVisible();
	});
});
