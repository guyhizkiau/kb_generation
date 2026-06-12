import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen } from '@testing-library/react'
import { ResearchPanel } from './ResearchPanel'
import { renderWithProviders } from '@/test/render'
import * as hooks from '@/api/hooks'

vi.mock('@/api/hooks', async (importOriginal) => {
  const actual = await importOriginal<typeof hooks>()
  return {
    ...actual,
    useResearch: vi.fn(),
    researchAssetUrl: (slug: string, name: string) =>
      `/api/articles/${slug}/research/asset/${name}`,
  }
})

describe('ResearchPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders research files and image', () => {
    vi.mocked(hooks.useResearch).mockReturnValue({
      data: {
        slug: '05-share-a-folder',
        files: [
          { name: 'competitor-coverage.md', content: 'Coverage notes' },
          { name: 'ui-snapshot/ui-glossary.md', content: 'UI labels' },
        ],
        images: ['shot.png'],
      },
      isLoading: false,
      isError: false,
    } as unknown as ReturnType<typeof hooks.useResearch>)
    renderWithProviders(<ResearchPanel slug="05-share-a-folder" />)
    expect(screen.getByText('competitor-coverage.md')).toBeInTheDocument()
    expect(screen.getByText('Coverage notes')).toBeInTheDocument()
    expect(screen.getByRole('img')).toHaveAttribute(
      'src',
      '/api/articles/05-share-a-folder/research/asset/shot.png',
    )
  })

  it('shows empty state', () => {
    vi.mocked(hooks.useResearch).mockReturnValue({
      data: { slug: '05-share-a-folder', files: [], images: [] },
      isLoading: false,
      isError: false,
    } as unknown as ReturnType<typeof hooks.useResearch>)
    renderWithProviders(<ResearchPanel slug="05-share-a-folder" />)
    expect(screen.getByText('No research collected yet.')).toBeInTheDocument()
  })
})
