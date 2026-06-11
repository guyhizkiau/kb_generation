import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { PhaseBadge } from './PhaseBadge'
import { renderWithProviders } from '@/test/render'

describe('PhaseBadge', () => {
  it('renders plain phase label for terminal phases', () => {
    renderWithProviders(<PhaseBadge phase="DONE" />)
    expect(screen.getByText('DONE')).toBeInTheDocument()
  })

  it('appends elapsed time for in-progress phases', () => {
    renderWithProviders(
      <PhaseBadge phase="TESTING" lastUpdate="2026-06-03T10:00:00Z" />,
    )
    expect(screen.getByText(/TESTING · \d+[mhd]/)).toBeInTheDocument()
  })

  it('shows elapsed time without running label when active', () => {
    renderWithProviders(
      <PhaseBadge
        phase="TESTING"
        lastUpdate="2026-06-03T10:00:00Z"
        running
      />,
    )
    expect(screen.getByText(/TESTING · \d+[mhd]/)).toBeInTheDocument()
    expect(screen.queryByText(/idle/i)).not.toBeInTheDocument()
  })

  it('shows idle in label when not running', () => {
    renderWithProviders(
      <PhaseBadge
        phase="TESTING"
        lastUpdate="2026-06-03T10:00:00Z"
        running={false}
      />,
    )
    expect(screen.getByText(/TESTING · idle · \d+[mhd]/i)).toBeInTheDocument()
  })

  it('shows plain label for IN_REVIEW without idle suffix', () => {
    renderWithProviders(
      <PhaseBadge
        phase="IN_REVIEW"
        lastUpdate="2026-06-01T10:00:00Z"
        running={false}
      />,
    )
    expect(screen.getByText('IN_REVIEW')).toBeInTheDocument()
    expect(screen.queryByText(/idle/i)).not.toBeInTheDocument()
  })
})
