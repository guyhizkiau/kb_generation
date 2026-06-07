import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ArticlesView } from './ArticlesView'
import { renderWithProviders } from '@/test/render'
import { mockQueue } from '@/test/fixtures'
import * as hooks from '@/api/hooks'
import * as rq from '@tanstack/react-query'

vi.mock('@tanstack/react-query', async (importOriginal) => {
  const actual = await importOriginal<typeof rq>()
  return {
    ...actual,
    useQueries: vi.fn(() => []),
  }
})

vi.mock('@mantine/modals', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@mantine/modals')>()
  return {
    ...actual,
    modals: {
      ...actual.modals,
      openConfirmModal: vi.fn(({ onConfirm }: { onConfirm?: () => void }) => {
        onConfirm?.()
      }),
    },
  }
})

vi.mock('@/api/hooks', async (importOriginal) => {
  const actual = await importOriginal<typeof hooks>()
  return {
    ...actual,
    useQueue: vi.fn(),
    useSaveQueue: vi.fn(),
    useTrigger: vi.fn(),
  }
})

describe('ArticlesView', () => {
  const mutateSave = vi.fn()
  const mutateTrigger = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(hooks.useQueue).mockReturnValue({
      data: mockQueue,
      isLoading: false,
    } as ReturnType<typeof hooks.useQueue>)
    vi.mocked(hooks.useSaveQueue).mockReturnValue({
      mutate: mutateSave,
      isPending: false,
    } as unknown as ReturnType<typeof hooks.useSaveQueue>)
    vi.mocked(hooks.useTrigger).mockReturnValue({
      mutate: mutateTrigger,
      isPending: false,
    } as unknown as ReturnType<typeof hooks.useTrigger>)
  })

  it('shows review section and planning section separately', () => {
    renderWithProviders(<ArticlesView />)
    expect(screen.getAllByText('WRITTEN & IN PROGRESS')[0]).toBeInTheDocument()
    expect(screen.getAllByRole('button', { name: 'Review' })[0]).toBeInTheDocument()
    expect(screen.getAllByText('UP NEXT')[0]).toBeInTheDocument()
    expect(screen.getAllByText('Next up')[0]).toBeInTheDocument()
  })

  it('shows Next up badge in planning section', () => {
    renderWithProviders(<ArticlesView />)
    expect(screen.getAllByText('Next up').length).toBeGreaterThan(0)
  })

  it('delete modal requires typing delete', async () => {
    renderWithProviders(<ArticlesView />)
    await userEvent.click(
      screen.getAllByRole('button', { name: 'Remove 02-set-or-reset-password from cluster' })[0]!,
    )
    expect(await screen.findByTestId('delete-confirm-input')).toBeInTheDocument()
    const removeBtn = screen.getByRole('button', { name: 'Confirm delete' })
    expect(removeBtn).toBeDisabled()
    await userEvent.type(screen.getByTestId('delete-confirm-input'), 'delete')
    expect(removeBtn).not.toBeDisabled()
    await userEvent.click(removeBtn)
    expect(screen.getAllByText('UNSAVED')[0]).toBeInTheDocument()
  })

  it('Write next triggers manual POST from planning section', async () => {
    renderWithProviders(<ArticlesView />)
    const writeNext = screen.getAllByRole('button', {
      name: 'Write next → 02-set-or-reset-password',
    })[0]
    await userEvent.click(writeNext)
    expect(mutateTrigger).toHaveBeenCalledWith(
      { slug: '02-set-or-reset-password', reason: 'manual' },
      expect.any(Object),
    )
  })
})
