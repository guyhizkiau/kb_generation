import { describe, it, expect, vi, beforeEach } from 'vitest'
import { screen } from '@testing-library/react'
import { InProgressPanel } from './InProgressPanel'
import { renderWithProviders } from '@/test/render'
import * as hooks from '@/api/hooks'

vi.mock('@/api/hooks', async (importOriginal) => {
  const actual = await importOriginal<typeof hooks>()
  return {
    ...actual,
    useResearch: vi.fn(),
    researchAssetUrl: () => '/asset.png',
  }
})

describe('InProgressPanel', () => {
  beforeEach(() => {
    vi.mocked(hooks.useResearch).mockReturnValue({
      data: { slug: '05-share-a-folder', files: [], images: [] },
      isLoading: false,
      isError: false,
    } as unknown as ReturnType<typeof hooks.useResearch>)
  })

  it('shows research in progress heading', () => {
    renderWithProviders(<InProgressPanel slug="05-share-a-folder" phase="RESEARCHING" />)
    expect(screen.getByText('Research in progress')).toBeInTheDocument()
    expect(screen.getByText('No research collected yet.')).toBeInTheDocument()
  })
})
