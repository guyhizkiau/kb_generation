import type { QueueData, StatusData } from '@/api/hooks'

export const mockQueue: QueueData = {
  version: 1,
  next_slug: '02-set-or-reset-password',
  publish_stale: ['01-log-in-to-specterx'],
  clusters: [{
    id: '01-login',
    title: 'Login cluster',
    mode: 'serial',
    status: 'active',
    pause_after: true,
    articles: [
      {
        slug: '01-log-in-to-specterx',
        title: 'Log in',
        phase: 'MERGED',
        revision_cycle: 1,
        publish_stale: true,
        feedback_issue: '42',
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

export const mockStatus: StatusData = {
  daemon: { started_at: '2026-06-01T10:00:00Z', pid: 1234, poll_interval: 30 },
  last_poll_at: '2026-06-01T10:05:00Z',
  poll_number: 5,
  next_poll_at: '2026-06-01T10:05:30Z',
  open_prs: [{ number: 7, branch: 'article/02-set-or-reset-password' }],
  current_task: null,
  last_error: null,
  last_task_duration_secs: 120,
  failed_comments: [{
    comment_id: 'issue-99',
    pr_number: 7,
    body_preview: 'fix wording',
    failure: 'STEP_TIMEOUT',
    failed_at: '2026-06-01T09:00:00Z',
  }],
  counters: {
    comments_resolved: 3,
    articles_triggered: 2,
    merges_handled: 1,
    previews_posted: 2,
  },
  recent_log: ['[2026-06-01] Poll #5', '[2026-06-01] idle'],
  task_log: [],
  phase_log: [],
  phase_log_source: '',
}
