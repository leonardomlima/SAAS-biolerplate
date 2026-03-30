import { test, expect } from "@playwright/test"

test("register screen has production form fields", async ({ page }) => {
  await page.goto("/auth/register")
  await expect(page.getByText("Criar conta")).toBeVisible()
  await expect(page.getByLabel("Nome completo")).toBeVisible()
  await expect(page.getByLabel("Organização")).toBeVisible()
  await expect(page.getByLabel("Email")).toBeVisible()
  await expect(page.getByLabel("Senha")).toBeVisible()
})
