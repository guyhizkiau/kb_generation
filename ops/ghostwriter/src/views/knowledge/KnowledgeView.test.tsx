import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen } from '@testing-library/react'
import { KnowledgeView } from './KnowledgeView'
import { renderWithProviders } from '@/test/render'
import * as hooks from '@/api/hooks'

vi.mock('@/views/knowledge/DocReaderOverlay', () => ({
  DocReaderOverlay: () => null,
}))

vi.mock('@/api/hooks', async (importOriginal) => {
  const actual = await importOriginal<typeof hooks>()
  return {
    ...actual,
    useDocs: vi.fn(),
  }
})

const mockDocs = {
  docs: [
    {
      id: 'style-guide',
      title: 'Style guide',
      group: 'Editorial',
      path: 'editorial/STYLE_GUIDE.md',
      exists: true,
      mtime: 1_700_000_000,
    },
    {
      id: 'glossary',
      title: 'Glossary',
      group: 'Canon',
      path: 'canon/GLOSSARY.md',
      exists: false,
      mtime: null,
    },
  ],
}

describe('KnowledgeView', () => {
  beforeEach(() => {
    vi.mocked(hooks.useDocs).mockReturnValue({
      data: mockDocs,
      isLoading: false,
      isError: false,
    } as ReturnType<typeof hooks.useDocs>)
  })

  it('renders group headings and doc titles', () => {
    renderWithProviders(<KnowledgeView />)
    expect(screen.getByText('EDITORIAL')).toBeInTheDocument()
    expect(screen.getByText('CANON')).toBeInTheDocument()
    expect(screen.getByText('Style guide')).toBeInTheDocument()
    expect(screen.getByText('Glossary')).toBeInTheDocument()
  })

  it('shows not created yet for missing docs', () => {
    renderWithProviders(<KnowledgeView />)
    expect(screen.getByText('not created yet')).toBeInTheDocument()
  })
})
