import { describe, it, expect, vi } from 'vitest'
import { screen } from '@testing-library/react'
import { HealthView } from './HealthView'
import { renderWithProviders } from '@/test/render'
import { mockStatus } from '@/test/fixtures'
import * as hooks from '@/api/hooks'

vi.mock('@/api/hooks', async (importOriginal) => {
  const actual = await importOriginal<typeof hooks>()
  return {
    ...actual,
    useStatus: vi.fn(),
    usePollNow: vi.fn(() => ({ mutate: vi.fn(), isPending: false })),
    useRetry: vi.fn(() => ({ mutate: vi.fn() })),
  }
})

describe('HealthView', () => {
  it('renders daemon counters without legacy PR sections', () => {
    vi.mocked(hooks.useStatus).mockReturnValue({
      data: mockStatus,
      isLoading: false,
      error: null,
    } as ReturnType<typeof hooks.useStatus>)

    renderWithProviders(<HealthView />)

    expect(screen.getByText('Daemon Health')).toBeInTheDocument()
    expect(screen.getByText('articles triggered')).toBeInTheDocument()
    expect(screen.queryByText('Open PRs')).not.toBeInTheDocument()
    expect(screen.queryByText('Failed comments')).not.toBeInTheDocument()
  })
})
