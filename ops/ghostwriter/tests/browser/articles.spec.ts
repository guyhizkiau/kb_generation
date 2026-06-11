import { test, expect } from '@playwright/test'
import { mockApiRoutes } from './fixtures'

test('articles view is default; save and write-this-next in Up next', async ({ page }) => {
  await mockApiRoutes(page)
  let putBody: unknown = null
  let triggerBody: unknown = null

  await page.route('**/api/queue', async (route) => {
    if (route.request().method() === 'PUT') {
      putBody = route.request().postDataJSON()
      await route.fulfill({ json: { ok: true } })
    } else {
      await route.fulfill({ json: (await import('./fixtures')).mockQueue })
    }
  })
  await page.route('**/api/queue/trigger', async (route) => {
    triggerBody = route.request().postDataJSON()
    await route.fulfill({ json: { ok: true } })
  })

  await page.goto('./')
  await expect(page.getByText('Review published articles and plan what\'s next')).toBeVisible()
  await expect(page.getByText('UP NEXT')).toBeVisible()
  await expect(page.getByText('Next up')).toBeVisible()
  await expect(page.getByRole('button', { name: /Review Log in/i })).toBeVisible()

  await page.getByRole('button', { name: 'Remove 02-set-or-reset-password from cluster' }).click()
  await page.getByTestId('delete-confirm-input').fill('delete')
  await page.getByRole('button', { name: 'Confirm delete' }).click()
  await expect(page.getByText('UNSAVED')).toBeVisible()
  await page.getByRole('button', { name: 'Save' }).click()
  await expect.poll(() => putBody).not.toBeNull()

  await page.getByRole('button', { name: 'Write next → 02-set-or-reset-password' }).click()
  await page.getByRole('button', { name: 'Write it' }).click()
  await expect.poll(() => triggerBody).toMatchObject({
    slug: '02-set-or-reset-password',
    reason: 'manual',
  })
})
