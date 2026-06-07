import { test, expect } from '@playwright/test'

test('annotation in reader posts to /api/feedback and refreshes sidebar', async ({ page }) => {
  await page.route('**/api/queue', async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({ json: (await import('./fixtures')).mockQueue })
    } else {
      await route.continue()
    }
  })
  await page.route('**/status/status.json', async (route) => {
    await route.fulfill({ json: (await import('./fixtures')).mockStatus })
  })

  let feedbackPost: unknown = null
  const annotations: Array<Record<string, unknown>> = []

  await page.route('**/api/feedback**', async (route) => {
    if (route.request().method() === 'POST') {
      feedbackPost = route.request().postDataJSON()
      annotations.push(feedbackPost as Record<string, unknown>)
      await route.fulfill({ json: { ok: true, annotation: feedbackPost } })
      return
    }
    await route.fulfill({
      json: {
        slug: '01-log-in-to-specterx',
        annotations,
      },
    })
  })

  await page.route('**/api/articles/*/preview', async (route) => {
    await route.fulfill({
      contentType: 'text/html',
      body: `<!doctype html><html><head>
        <script>window.__GHOSTWRITER__={apiBase:"",n8nWebhook:""}</script>
        </head><body><main><p>Sign in to SpecterX to continue.</p></main>
        <script src="/static/ghostwriter-annotate.js" data-slug="01-log-in-to-specterx"></script>
        </body></html>`,
    })
  })

  await page.route('**/static/ghostwriter-annotate.js', async (route) => {
    await route.fulfill({
      contentType: 'application/javascript',
      body: `
        window.addEventListener('DOMContentLoaded', function() {
          fetch('/api/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              id: 'e2e-new',
              slug: '01-log-in-to-specterx',
              body: [{ value: 'New inline comment' }],
              target: { selector: { type: 'TextQuoteSelector', exact: 'Sign in' } },
            }),
          }).then(function(r) {
            if (r.ok) window.parent.postMessage({
              type: 'ghostwriter:annotation-created',
              slug: '01-log-in-to-specterx',
            }, '*');
          });
        });
      `,
    })
  })

  await page.goto('./')
  await page.getByRole('button', { name: 'Review' }).first().click()
  const overlay = page.getByTestId('article-reader-overlay')
  await expect(overlay).toBeVisible()
  await expect.poll(() => feedbackPost).not.toBeNull()
  await expect.poll(async () =>
    overlay.getByText('New inline comment').isVisible(),
  ).toBe(true)
})
