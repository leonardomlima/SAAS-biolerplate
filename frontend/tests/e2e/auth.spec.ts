import { expect, test } from "@playwright/test"
test("landing", async ({ page }) => { await page.goto("/"); await expect(page.locator("text=SaaS")).toBeVisible() })
