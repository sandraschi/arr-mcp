import { test, expect } from "@playwright/test";

const PAGES = [
  { path: "/", name: "Dashboard" },
  { path: "/radarr", name: "Radarr" },
  { path: "/sonarr", name: "Sonarr" },
  { path: "/lidarr", name: "Lidarr" },
  { path: "/prowlarr", name: "Prowlarr" },
  { path: "/readarr", name: "Readarr" },
  { path: "/overseerr", name: "Overseerr" },
  { path: "/bazarr", name: "Bazarr" },
  { path: "/orchestrate", name: "Orchestrate" },
  { path: "/chat", name: "Chat" },
  { path: "/logger", name: "Logger" },
  { path: "/help", name: "Help" },
  { path: "/settings", name: "Settings" },
  { path: "/inspector", name: "Inspector" },
];

for (const { path, name } of PAGES) {
  test(`${name} loads without crash`, async ({ page }) => {
    await page.goto(path);
    await page.waitForLoadState("networkidle");
    await expect(page.locator("h2")).toBeVisible({ timeout: 10000 });
  });
}

test("Sidebar navigation works", async ({ page }) => {
  await page.goto("/");
  await page.waitForLoadState("networkidle");

  const sidebarLinks = page.locator("nav a");
  const count = await sidebarLinks.count();
  expect(count).toBeGreaterThan(5);

  await sidebarLinks.first().click();
  await page.waitForLoadState("networkidle");
});

test("Inspector can select a tool", async ({ page }) => {
  await page.goto("/inspector");
  await page.waitForLoadState("networkidle");

  const toolBtn = page.locator("button").filter({ hasText: "arr_health" });
  await toolBtn.first().click();

  await expect(page.locator("code")).toContainText("arr_health");
});
