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
  it('renders counters and open PRs from status fixture', () => {
    vi.mocked(hooks.useStatus).mockReturnValue({
      data: mockStatus,
      isLoading: false,
      error: null,
    } as ReturnType<typeof hooks.useStatus>)

    renderWithProviders(<HealthView />)

    expect(screen.getByText('Daemon Health')).toBeInTheDocument()
    expect(screen.getByText('comments resolved')).toBeInTheDocument()
    expect(screen.getByText('article/02-set-or-reset-password')).toBeInTheDocument()
    const branchLink = screen.getByRole('link', { name: 'article/02-set-or-reset-password' })
    expect(branchLink).toHaveAttribute('href', 'https://github.com/guyhizkiau/kb_generation/pull/7')
    expect(screen.getByText('Failed comments (1)')).toBeInTheDocument()
  })
})
