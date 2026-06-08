import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiFetch, apiUrl } from './client'

// ── types ────────────────────────────────────────────────────────────────────

export interface ArticleEntry {
  slug: string
  title: string
  phase: string
  revision_cycle: number
  publish_stale: boolean
  feedback_issue: string
  last_update?: string
  pr_number?: number
}

export interface Cluster {
  id: string
  title: string
  mode: 'serial' | 'parallel'
  status: 'active' | 'paused' | 'done'
  pause_after: boolean
  articles: ArticleEntry[]
}

export interface QueueData {
  version: number
  clusters: Cluster[]
  next_slug: string | null
  publish_stale: string[]
  claude_running?: boolean
}

export interface Annotation {
  id: string
  body: { value: string }[]
  target: {
    selector: { type: string; exact?: string; value?: string }
    source?: string
  }
  creator?: { name: string }
  created?: string
}

export interface FeedbackData {
  slug: string
  annotations: Annotation[]
}

export interface StatusData {
  daemon: { started_at: string; pid: number; poll_interval: number }
  last_poll_at: string
  poll_number: number
  next_poll_at: string
  open_prs: { number: number; branch: string }[]
  current_task: null | {
    pr_number: number
    comment_id: string
    step: string
    started_at: string
  }
  last_error: null | { message: string; at: string }
  last_task_duration_secs: number | null
  failed_comments: {
    comment_id: string
    pr_number: number
    body_preview: string
    failure: string
    failed_at: string
  }[]
  counters: {
    comments_resolved: number
    articles_triggered: number
    merges_handled: number
    previews_posted: number
  }
  recent_log: string[]
}

// ── queue ────────────────────────────────────────────────────────────────────

export function useQueue() {
  return useQuery<QueueData>({
    queryKey: ['queue'],
    queryFn: () => apiFetch('/api/queue'),
    refetchInterval: 3000,
  })
}

export function useSaveQueue() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (q: QueueData) =>
      apiFetch('/api/queue', { method: 'PUT', body: JSON.stringify(q) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['queue'] }),
  })
}

export function useTrigger() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: { slug: string; reason: 'manual' | 'feedback'; issue?: string }) =>
      apiFetch('/api/queue/trigger', { method: 'POST', body: JSON.stringify(data) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['queue'] }),
  })
}

export function useMergeArticle() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: { slug: string; pr_number?: number }) =>
      apiFetch('/api/queue/merge', { method: 'POST', body: JSON.stringify(data) }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['queue'] })
      qc.invalidateQueries({ queryKey: ['status'] })
    },
  })
}

export function useDeleteArticle() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ slug, removeFromPlan }: { slug: string; removeFromPlan: boolean }) =>
      apiFetch(
        `/api/articles/${encodeURIComponent(slug)}?remove_from_plan=${removeFromPlan}`,
        { method: 'DELETE' },
      ),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['queue'] })
      qc.invalidateQueries({ queryKey: ['status'] })
    },
  })
}

// ── feedback ─────────────────────────────────────────────────────────────────

export function useFeedback(slug: string) {
  return useQuery<FeedbackData>({
    queryKey: ['feedback', slug],
    queryFn: () => apiFetch(`/api/feedback?slug=${slug}`),
    enabled: !!slug,
  })
}

/** Build iframe URL for article HTML preview with Ghostwriter config injected server-side. */
export function articlePreviewUrl(slug: string): string {
  return apiUrl(`/api/articles/${encodeURIComponent(slug)}/preview`)
}

export function usePostAnnotation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: { slug: string } & Record<string, unknown>) =>
      apiFetch('/api/feedback', { method: 'POST', body: JSON.stringify(data) }),
    onSuccess: (_data, variables) => {
      qc.invalidateQueries({ queryKey: ['feedback', variables.slug] })
    },
  })
}

export function useDismissAnnotation() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ slug, id }: { slug: string; id: string }) =>
      apiFetch(`/api/feedback?slug=${encodeURIComponent(slug)}&id=${encodeURIComponent(id)}`, {
        method: 'DELETE',
      }),
    onMutate: async ({ slug, id }) => {
      await qc.cancelQueries({ queryKey: ['feedback', slug] })
      const prev = qc.getQueryData<FeedbackData>(['feedback', slug])
      if (prev) {
        qc.setQueryData<FeedbackData>(['feedback', slug], {
          ...prev,
          annotations: prev.annotations.filter((a) => a.id !== id),
        })
      }
      return { prev }
    },
    onError: (_err, { slug }, ctx) => {
      if (ctx?.prev) {
        qc.setQueryData(['feedback', slug], ctx.prev)
      }
    },
    onSuccess: (_data, { slug }) => {
      qc.invalidateQueries({ queryKey: ['feedback', slug] })
    },
  })
}

// ── daemon status ─────────────────────────────────────────────────────────────

export function useStatus() {
  return useQuery<StatusData>({
    queryKey: ['status'],
    queryFn: () => apiFetch('/status/status.json'),
    refetchInterval: 5000,
  })
}

export function usePollNow() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => apiFetch('/poll-now', { method: 'POST', body: '{}' }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['status'] }),
  })
}

export function useRetry() {
  return useMutation({
    mutationFn: (commentId: string) =>
      apiFetch('/retry', {
        method: 'POST',
        body: JSON.stringify({ comment_id: commentId }),
      }),
  })
}
