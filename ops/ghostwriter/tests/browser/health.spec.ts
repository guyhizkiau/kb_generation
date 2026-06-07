import { test, expect } from '@playwright/test'
import { mockApiRoutes } from './fixtures'

test('health view renders status and poll-now', async ({ page }) => {
  await mockApiRoutes(page)
  let pollCalled = false
  await page.route('**/poll-now', async (route) => {
    pollCalled = true
    await route.fulfill({ json: { ok: true } })
  })

  await page.goto('./')
  await page.getByText('Health', { exact: true }).click()
  await expect(page.getByText('Daemon Health')).toBeVisible()
  await expect(page.getByText('comments resolved')).toBeVisible()
  await page.getByRole('button', { name: 'Poll now' }).click()
  await expect.poll(() => pollCalled).toBe(true)
  await page.screenshot({ path: 'test-results/health.png', fullPage: true })
})
