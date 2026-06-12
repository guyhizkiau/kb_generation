import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { DocReaderOverlay } from './DocReaderOverlay'
import { renderWithProviders } from '@/test/render'
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
    useDocs: vi.fn(),
    useDoc: vi.fn(),
    useSaveDoc: vi.fn(),
    useFeedback: vi.fn(),
    useReviseDoc: vi.fn(),
    useDismissAnnotation: vi.fn(),
    docPreviewUrl: (id: string) => `/api/docs/${id}/preview`,
  }
})

describe('DocReaderOverlay', () => {
  const mutateSave = vi.fn()
  const mutateRevise = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(hooks.useDocs).mockReturnValue({
      data: {
        docs: [{
          id: 'glossary',
          title: 'Glossary',
          group: 'Canon',
          path: 'canon/GLOSSARY.md',
          exists: true,
          mtime: null,
        }],
      },
    } as ReturnType<typeof hooks.useDocs>)
    vi.mocked(hooks.useDoc).mockReturnValue({
      data: { id: 'glossary', content: '# A' },
      isError: false,
    } as ReturnType<typeof hooks.useDoc>)
    vi.mocked(hooks.useFeedback).mockReturnValue({
      data: { slug: 'doc--glossary', annotations: [] },
      isLoading: false,
    } as unknown as ReturnType<typeof hooks.useFeedback>)
    vi.mocked(hooks.useSaveDoc).mockReturnValue({
      mutate: mutateSave,
      isPending: false,
    } as unknown as ReturnType<typeof hooks.useSaveDoc>)
    vi.mocked(hooks.useReviseDoc).mockReturnValue({
      mutate: mutateRevise,
      isPending: false,
    } as unknown as ReturnType<typeof hooks.useReviseDoc>)
    vi.mocked(hooks.useDismissAnnotation).mockReturnValue({
      mutate: vi.fn(),
    } as unknown as ReturnType<typeof hooks.useDismissAnnotation>)
  })

  it('disables Save until draft changes', async () => {
    renderWithProviders(<DocReaderOverlay docId="glossary" onClose={vi.fn()} />)
    await userEvent.click(screen.getByRole('tab', { name: 'Edit' }))
    const save = screen.getByRole('button', { name: 'Save' })
    expect(save).toBeDisabled()
    const textarea = screen.getByRole('textbox')
    await userEvent.clear(textarea)
    await userEvent.type(textarea, '# B')
    expect(save).toBeEnabled()
    await userEvent.click(save)
    expect(mutateSave).toHaveBeenCalledWith(
      { id: 'glossary', content: '# B' },
      expect.any(Object),
    )
  })

  it('shows Accept feedback when annotations exist', async () => {
    vi.mocked(hooks.useFeedback).mockReturnValue({
      data: {
        slug: 'doc--glossary',
        annotations: [{
          id: 'ann-1',
          body: [{ value: 'fix this' }],
          target: { selector: { type: 'TextQuoteSelector', exact: 'term' } },
        }],
      },
      isLoading: false,
    } as unknown as ReturnType<typeof hooks.useFeedback>)
    renderWithProviders(<DocReaderOverlay docId="glossary" onClose={vi.fn()} />)
    expect(screen.getByRole('button', { name: 'Accept feedback' })).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Accept feedback' }))
    expect(mutateRevise).toHaveBeenCalledWith('glossary', expect.any(Object))
  })

  it('hides Accept feedback without annotations', () => {
    renderWithProviders(<DocReaderOverlay docId="glossary" onClose={vi.fn()} />)
    expect(screen.queryByRole('button', { name: 'Accept feedback' })).not.toBeInTheDocument()
  })
})
