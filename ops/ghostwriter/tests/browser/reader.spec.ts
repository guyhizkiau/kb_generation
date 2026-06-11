import { test, expect } from '@playwright/test'
import { mockApiRoutes } from './fixtures'

test('reader overlay opens from article title', async ({ page }) => {
  await mockApiRoutes(page)

  await page.route('**/api/articles/*/preview', async (route) => {
    await route.fulfill({
      contentType: 'text/html',
      body: '<html><head></head><body><main>Article preview</main></body></html>',
    })
  })

  await page.goto('./')
  await page.getByRole('button', { name: /Review Log in/i }).click()
  const overlay = page.getByTestId('article-reader-overlay')
  await expect(overlay).toBeVisible()
  await expect(overlay.locator('iframe')).toBeVisible()
  await expect(overlay.getByText(/Fix login wording/)).toBeVisible()
  await overlay.getByRole('button', { name: 'Back' }).click()
  await expect(overlay).not.toBeVisible()
})
