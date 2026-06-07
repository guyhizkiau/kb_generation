import { describe, it, expect } from 'vitest'
import { formatPhaseElapsed, isReviewable, isPlannable, partitionArticles } from './articlePhase'
import type { ArticleEntry } from '@/api/hooks'

const base = (phase: string): ArticleEntry => ({
  slug: '01-test',
  title: 'Test',
  phase,
  revision_cycle: 0,
  publish_stale: false,
  feedback_issue: '',
})

describe('articlePhase', () => {
  it('DONE and MERGED are reviewable', () => {
    expect(isReviewable(base('DONE'))).toBe(true)
    expect(isReviewable(base('MERGED'))).toBe(true)
    expect(isPlannable(base('DONE'))).toBe(false)
  })

  it('in-progress phases are reviewable', () => {
    expect(isReviewable(base('REVISING'))).toBe(true)
    expect(isReviewable(base('PR_OPEN'))).toBe(true)
  })

  it('UNKNOWN and PLANNED are plannable only', () => {
    expect(isReviewable(base('UNKNOWN'))).toBe(false)
    expect(isPlannable(base('UNKNOWN'))).toBe(true)
    expect(isPlannable(base('PLANNED'))).toBe(true)
  })

  it('partitionArticles splits lists', () => {
    const { reviewable, plannable } = partitionArticles([
      base('DONE'),
      base('UNKNOWN'),
      base('DRAFTING'),
    ])
    expect(reviewable).toHaveLength(2)
    expect(plannable).toHaveLength(1)
    expect(plannable[0]?.phase).toBe('UNKNOWN')
  })

  describe('formatPhaseElapsed', () => {
    const now = new Date('2026-06-03T12:34:00Z')

    it('formats minutes from ISO timestamp', () => {
      expect(formatPhaseElapsed('2026-06-03T12:29:00Z', now)).toBe('5m')
    })

    it('formats hours from ISO timestamp', () => {
      expect(formatPhaseElapsed('2026-06-03T10:34:00Z', now)).toBe('2h')
    })

    it('formats days from date-only timestamp', () => {
      expect(formatPhaseElapsed('2026-06-01', now)).toBe('2d')
    })

    it('returns null for empty or invalid input', () => {
      expect(formatPhaseElapsed('', now)).toBeNull()
      expect(formatPhaseElapsed('not-a-date', now)).toBeNull()
    })
  })
})
