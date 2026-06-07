import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createElement, ReactNode } from 'react'
import { useStatus, useSaveQueue, useTrigger } from './hooks'

function wrapper({ children }: { children: ReactNode }) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return createElement(QueryClientProvider, { client: qc }, children)
}

describe('api hooks', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('useStatus fetches /status/status.json', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        daemon: { started_at: '2026-01-01', pid: 1, poll_interval: 30 },
        counters: {},
        open_prs: [],
        failed_comments: [],
        recent_log: [],
        last_poll_at: '',
        poll_number: 1,
        next_poll_at: '',
        current_task: null,
        last_error: null,
        last_task_duration_secs: null,
      }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const { result } = renderHook(() => useStatus(), { wrapper })
    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/status/status.json'),
      expect.any(Object),
    )
  })

  it('useSaveQueue PUTs to /api/queue', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ ok: true }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const { result } = renderHook(() => useSaveQueue(), { wrapper })
    await result.current.mutateAsync({
      version: 1,
      clusters: [],
      next_slug: null,
      publish_stale: [],
    })
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/api/queue'),
      expect.objectContaining({ method: 'PUT' }),
    )
  })

  it('useTrigger POSTs reason to /api/queue/trigger', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ ok: true }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const { result } = renderHook(() => useTrigger(), { wrapper })
    await result.current.mutateAsync({ slug: '01-log-in-to-specterx', reason: 'manual' })
    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect(init.method).toBe('POST')
    expect(init.body).toContain('"reason":"manual"')
  })
})
