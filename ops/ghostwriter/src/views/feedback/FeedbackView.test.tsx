import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FeedbackView } from './FeedbackView'
import { renderWithProviders } from '@/test/render'
import { mockQueue } from '@/test/fixtures'
import * as hooks from '@/api/hooks'

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
    useFeedback: vi.fn(),
    useTrigger: vi.fn(),
  }
})

describe('FeedbackView', () => {
  const mutateTrigger = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(hooks.useQueue).mockReturnValue({
      data: mockQueue,
      isLoading: false,
    } as ReturnType<typeof hooks.useQueue>)
    vi.mocked(hooks.useFeedback).mockReturnValue({
      data: {
        slug: '01-log-in-to-specterx',
        annotations: [{
          id: 'anno-1',
          body: [{ value: 'Please fix the login step wording' }],
          target: {
            selector: { type: 'TextQuoteSelector', exact: 'Enter your credentials' },
          },
          creator: { name: 'Guy' },
        }],
      },
      isLoading: false,
    } as ReturnType<typeof hooks.useFeedback>)
    vi.mocked(hooks.useTrigger).mockReturnValue({
      mutate: mutateTrigger,
      isPending: false,
    } as unknown as ReturnType<typeof hooks.useTrigger>)
  })

  it('renders annotation quote and author', async () => {
    renderWithProviders(<FeedbackView />)
    await userEvent.click(screen.getAllByText('Log in')[0])
    expect(screen.getByText(/Enter your credentials/)).toBeInTheDocument()
    expect(screen.getByText('Guy')).toBeInTheDocument()
  })

  it('Accept fires feedback trigger with issue', async () => {
    renderWithProviders(<FeedbackView />)
    await userEvent.click(screen.getAllByText('Log in')[0])
    await userEvent.click(screen.getByRole('button', { name: 'Accept → revise' }))
    expect(mutateTrigger).toHaveBeenCalledWith(
      { slug: '01-log-in-to-specterx', reason: 'feedback', issue: '42' },
      expect.any(Object),
    )
  })
})
