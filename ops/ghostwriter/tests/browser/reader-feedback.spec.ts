import { test, expect } from '@playwright/test'
import { mockApiRoutes, mockQueue } from './fixtures'

test('reader accept triggers revision from articles view', async ({ page }) => {
  await mockApiRoutes(page)
  const queueWithIssue = {
    ...mockQueue,
    clusters: [{
      ...mockQueue.clusters[0],
      articles: mockQueue.clusters[0].articles.map((a) =>
        a.slug === '01-log-in-to-specterx'
          ? { ...a, feedback_issue: '42', phase: 'REVISING' }
          : a,
      ),
    }],
  }
  await page.route('**/api/queue', async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({ json: queueWithIssue })
    } else {
      await route.continue()
    }
  })

  let triggerBody: unknown = null
  await page.route('**/api/queue/trigger', async (route) => {
    triggerBody = route.request().postDataJSON()
    await route.fulfill({ json: { ok: true } })
  })

  await page.route('**/api/articles/*/preview', async (route) => {
    await route.fulfill({
      contentType: 'text/html',
      body: '<html><head></head><body><main>Article preview</main></body></html>',
    })
  })

  await page.goto('./')
  await page.getByRole('button', { name: 'Review Log in to SpecterX' }).click()
  const overlay = page.getByTestId('article-reader-overlay')
  await expect(overlay.getByText(/Sign in/)).toBeVisible()
  await overlay.getByRole('button', { name: 'Accept → revise' }).click()
  await page.getByRole('button', { name: 'Launch revision' }).click()
  await expect.poll(() => triggerBody).toMatchObject({
    slug: '01-log-in-to-specterx',
    reason: 'feedback',
    issue: '42',
  })
  await page.screenshot({ path: 'test-results/reader-feedback.png', fullPage: true })
})
