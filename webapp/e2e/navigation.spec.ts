import { expect, test } from "@playwright/test";

const pages = [
	{ link: "Dashboard", heading: "Dashboard", path: "/" },
	{ link: "Radarr", heading: "Radarr", path: "/radarr" },
	{ link: "Sonarr", heading: "Sonarr", path: "/sonarr" },
	{ link: "Lidarr", heading: "Lidarr", path: "/lidarr" },
	{ link: "Prowlarr", heading: "Prowlarr", path: "/prowlarr" },
	{ link: "Readarr", heading: "Readarr", path: "/readarr" },
	{ link: "Overseerr", heading: "Overseerr", path: "/overseerr" },
	{ link: "Bazarr", heading: "Bazarr", path: "/bazarr" },
	{ link: "Orchestrate", heading: "Orchestrate", path: "/orchestrate" },
	{ link: "Chat", heading: "Chat", path: "/chat" },
	{ link: "Logger", heading: "Logger", path: "/logger" },
	{ link: "Help", heading: "Help", path: "/help" },
	{ link: "Settings", heading: "Settings", path: "/settings" },
];

test.describe("Navigation", () => {
	for (const pageInfo of pages) {
		test(`sidebar navigates to ${pageInfo.link}`, async ({ page }) => {
			await page.goto("/");
			await page.getByRole("link", { name: pageInfo.link, exact: true }).click();
			await expect(page).toHaveURL(new RegExp(`${pageInfo.path.replace("/", "\\/")}$`));
			await expect(page.getByRole("heading", { name: pageInfo.heading })).toBeVisible();
		});
	}

	test("redirects unknown routes to dashboard", async ({ page }) => {
		await page.goto("/does-not-exist");
		await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
	});
});
