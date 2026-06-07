import { describe, it, expect, vi } from 'vitest'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { GhostwriterShell } from './GhostwriterShell'
import { renderWithProviders } from '@/test/render'
import { mockQueue, mockStatus } from '@/test/fixtures'
import * as hooks from '@/api/hooks'

vi.mock('@/api/hooks', async (importOriginal) => {
  const actual = await importOriginal<typeof hooks>()
  return {
    ...actual,
    useQueue: vi.fn(() => ({ data: mockQueue, isLoading: false })),
    useStatus: vi.fn(() => ({ data: mockStatus, isLoading: false })),
    useSaveQueue: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
    useTrigger: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
    useFeedback: vi.fn(() => ({ data: { slug: '', annotations: [] }, isLoading: false })),
    usePollNow: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
    useRetry: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
  }
})

describe('GhostwriterShell', () => {
  it('loads Articles as default view', () => {
    renderWithProviders(<GhostwriterShell />)
    expect(screen.getByText('Review published articles and plan what\'s next')).toBeInTheDocument()
  })

  it('toggles sidebar collapse', async () => {
    localStorage.removeItem('gw_sidebar_collapsed')
    renderWithProviders(<GhostwriterShell />)
    await userEvent.click(screen.getAllByRole('button', { name: 'Collapse sidebar' })[0]!)
    expect(localStorage.getItem('gw_sidebar_collapsed')).toBe('true')
  })
})
