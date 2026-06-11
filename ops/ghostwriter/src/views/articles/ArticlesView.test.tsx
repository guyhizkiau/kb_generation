import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ArticlesView } from './ArticlesView'
import { renderWithProviders } from '@/test/render'
import { mockQueue } from '@/test/fixtures'
import * as hooks from '@/api/hooks'
import * as rq from '@tanstack/react-query'

const openReaderMock = vi.fn()

vi.mock('@/context/ReaderContext', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/context/ReaderContext')>()
  return {
    ...actual,
    useReader: () => ({
      readerSlug: null,
      openReader: openReaderMock,
      closeReader: vi.fn(),
    }),
  }
})

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
    useApproveArticle: vi.fn(),
    useRequestChanges: vi.fn(),
    useDeleteArticle: vi.fn(),
  }
})

describe('ArticlesView', () => {
  const mutateSave = vi.fn()
  const mutateTrigger = vi.fn()
  const mutateDelete = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    openReaderMock.mockClear()
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
    vi.mocked(hooks.useApproveArticle).mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    } as unknown as ReturnType<typeof hooks.useApproveArticle>)
    vi.mocked(hooks.useRequestChanges).mockReturnValue({
      mutate: vi.fn(),
      isPending: false,
    } as unknown as ReturnType<typeof hooks.useRequestChanges>)
    vi.mocked(hooks.useDeleteArticle).mockReturnValue({
      mutate: mutateDelete,
      isPending: false,
    } as unknown as ReturnType<typeof hooks.useDeleteArticle>)
  })

  it('shows review section and planning section separately', () => {
    renderWithProviders(<ArticlesView />)
    expect(screen.getAllByText('WRITTEN & IN PROGRESS')[0]).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Review Log in/i })).toBeInTheDocument()
    expect(screen.getAllByText('UP NEXT')[0]).toBeInTheDocument()
    expect(screen.getAllByText('Next up')[0]).toBeInTheDocument()
  })

  it('clicking article title opens review', async () => {
    renderWithProviders(<ArticlesView />)
    await userEvent.click(screen.getByRole('button', { name: /Review Log in/i }))
    expect(openReaderMock).toHaveBeenCalledWith('01-log-in-to-specterx')
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

  it('written-row delete opens two-option modal gated on typing delete', async () => {
    renderWithProviders(<ArticlesView />)
    await userEvent.click(
      screen.getByRole('button', { name: 'Delete 01-log-in-to-specterx' }),
    )
    expect(await screen.findByTestId('delete-confirm-input')).toBeInTheDocument()
    const deleteOnly = screen.getByRole('button', { name: 'Delete article' })
    const deleteAndPlan = screen.getByRole('button', { name: 'Delete & remove from plan' })
    expect(deleteOnly).toBeDisabled()
    expect(deleteAndPlan).toBeDisabled()
    await userEvent.type(screen.getByTestId('delete-confirm-input'), 'delete')
    expect(deleteOnly).not.toBeDisabled()
    expect(deleteAndPlan).not.toBeDisabled()
    await userEvent.click(deleteOnly)
    expect(mutateDelete).toHaveBeenCalledWith(
      { slug: '01-log-in-to-specterx', removeFromPlan: false },
      expect.any(Object),
    )
  })

  it('written-row delete with remove-from-plan passes removeFromPlan true', async () => {
    renderWithProviders(<ArticlesView />)
    await userEvent.click(
      screen.getByRole('button', { name: 'Delete 01-log-in-to-specterx' }),
    )
    await userEvent.type(await screen.findByTestId('delete-confirm-input'), 'delete')
    await userEvent.click(screen.getByRole('button', { name: 'Delete & remove from plan' }))
    expect(mutateDelete).toHaveBeenCalledWith(
      { slug: '01-log-in-to-specterx', removeFromPlan: true },
      expect.any(Object),
    )
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
