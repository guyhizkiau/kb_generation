import type { Page } from '@playwright/test'

export const mockQueue = {
  version: 1,
  next_slug: '02-set-or-reset-password',
  publish_stale: [],
  clusters: [{
    id: '01-login',
    title: 'Login cluster',
    articles: [
      {
        slug: '01-log-in-to-specterx',
        title: 'Log in to SpecterX',
        phase: 'MERGED',
        revision_cycle: 0,
        publish_stale: false,
        feedback_issue: '',
      },
      {
        slug: '02-set-or-reset-password',
        title: 'Reset password',
        phase: 'PLANNED',
        revision_cycle: 0,
        publish_stale: false,
        feedback_issue: '',
      },
    ],
  }],
}

export const mockStatus = {
  daemon: { started_at: '2026-06-01T10:00:00Z', pid: 99, poll_interval: 30 },
  last_poll_at: '2026-06-01T10:05:00Z',
  poll_number: 3,
  next_poll_at: '2026-06-01T10:05:30Z',
  open_prs: [{ number: 5, branch: 'article/02-set-or-reset-password' }],
  current_task: null,
  last_error: null,
  last_task_duration_secs: 60,
  failed_comments: [],
  counters: {
    comments_resolved: 1,
    articles_triggered: 1,
    merges_handled: 1,
    previews_posted: 1,
  },
  recent_log: ['Poll #3 complete'],
}

export async function mockApiRoutes(page: Page) {
  await page.route('**/api/queue', async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({ json: mockQueue })
    } else if (route.request().method() === 'PUT') {
      await route.fulfill({ json: { ok: true } })
    } else {
      await route.continue()
    }
  })
  await page.route('**/api/queue/trigger', async (route) => {
    await route.fulfill({ json: { ok: true, reason: 'manual' } })
  })
  await page.route('**/api/feedback**', async (route) => {
    await route.fulfill({
      json: {
        slug: '01-log-in-to-specterx',
        annotations: [{
          id: 'anno-1',
          body: [{ value: 'Fix login wording' }],
          target: { selector: { type: 'TextQuoteSelector', exact: 'Sign in' } },
          creator: { name: 'Reviewer' },
        }],
      },
    })
  })
  await page.route('**/status/status.json', async (route) => {
    await route.fulfill({ json: mockStatus })
  })
  await page.route('**/poll-now', async (route) => {
    await route.fulfill({ json: { ok: true } })
  })
}
