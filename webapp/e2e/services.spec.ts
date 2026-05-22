import { expect, test } from "@playwright/test";

const servicePages = [
	{ name: "Radarr", path: "/radarr", subtitle: "Movies" },
	{ name: "Sonarr", path: "/sonarr", subtitle: "TV Series" },
	{ name: "Lidarr", path: "/lidarr", subtitle: "Music" },
	{ name: "Prowlarr", path: "/prowlarr", subtitle: "Indexer Backbone" },
	{ name: "Readarr", path: "/readarr", subtitle: "Books" },
	{ name: "Overseerr", path: "/overseerr", subtitle: "Requests & Discovery" },
	{ name: "Bazarr", path: "/bazarr", subtitle: "Subtitles" },
];

test.describe("Service pages", () => {
	for (const service of servicePages) {
		test(`${service.name} page renders summary shell`, async ({ page }) => {
			await page.goto(service.path);
			await expect(page.getByRole("heading", { name: service.name })).toBeVisible();
			await expect(page.getByText(service.subtitle)).toBeVisible();
			await expect(page.getByText("Raw API Response")).toBeVisible({ timeout: 15_000 });
		});
	}
});
