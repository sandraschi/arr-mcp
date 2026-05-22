import { expect, test } from "@playwright/test";

const mockHealth = {
	success: true,
	data: {
		radarr: { reachable: true, version: "5.12.0" },
		sonarr: { reachable: false, reason: "not configured" },
		lidarr: { reachable: false, reason: "not configured" },
		prowlarr: { reachable: false, reason: "not configured" },
		readarr: { reachable: false, reason: "not configured" },
		overseerr: { reachable: false, reason: "not configured" },
		bazarr: { reachable: false, reason: "not configured" },
	},
};

const mockRadarrSummary = {
	success: true,
	data: {
		movies: 42,
		wanted: 3,
		queue: 1,
		disk: [{ path: "/movies", freeSpace: 500_000_000_000, totalSpace: 1_000_000_000_000 }],
	},
};

test.describe("Configured Radarr (mocked API)", () => {
	test.beforeEach(async ({ page }) => {
		await page.route("**/api/health", async (route) => {
			await route.fulfill({ json: mockHealth });
		});
		await page.route("**/api/radarr/summary", async (route) => {
			await route.fulfill({ json: mockRadarrSummary });
		});
	});

	test("dashboard shows reachable Radarr with version", async ({ page }) => {
		await page.goto("/");
		await expect(page.getByText("1/7 reachable")).toBeVisible({ timeout: 15_000 });
		await expect(page.getByText("v5.12.0")).toBeVisible();
		await expect(page.getByText("Running").first()).toBeVisible();
	});

	test("radarr page shows movie stats", async ({ page }) => {
		await page.goto("/radarr");
		await expect(page.getByRole("heading", { name: "Radarr" })).toBeVisible();
		await expect(page.locator("p.text-3xl").filter({ hasText: "42" })).toBeVisible({ timeout: 15_000 });
		await expect(page.locator("p.text-3xl").filter({ hasText: "3" })).toBeVisible();
	});
});
