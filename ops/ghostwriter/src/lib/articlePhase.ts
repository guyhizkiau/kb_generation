import type { ArticleEntry } from '@/api/hooks'

export const WRITTEN_PHASES = new Set(['DONE', 'MERGED'])

export const IN_PROGRESS_PHASES = new Set([
  'DRAFTING',
  'TESTING',
  'REVISING',
  'FINALIZING',
  'PR_OPEN',
  'PR_REVISION_NEEDED',
])

export function isWrittenPhase(phase: string): boolean {
  return WRITTEN_PHASES.has(phase)
}

export function isInProgressPhase(phase: string): boolean {
  return IN_PROGRESS_PHASES.has(phase)
}

/** Article has content to open in the reader (phase or typical pipeline progress). */
export function isReviewable(art: ArticleEntry): boolean {
  return isWrittenPhase(art.phase) || isInProgressPhase(art.phase)
}

/** Article not yet written — belongs in the planning / Up next section. */
export function isPlannable(art: ArticleEntry): boolean {
  return !isReviewable(art)
}

export function partitionArticles(articles: ArticleEntry[]): {
  reviewable: ArticleEntry[]
  plannable: ArticleEntry[]
} {
  const reviewable: ArticleEntry[] = []
  const plannable: ArticleEntry[] = []
  for (const art of articles) {
    if (isReviewable(art)) reviewable.push(art)
    else plannable.push(art)
  }
  return { reviewable, plannable }
}

/** Parse STATE LAST_UPDATE (ISO or date-only) into a Date, or null if invalid. */
function parseLastUpdate(lastUpdate: string): Date | null {
  const trimmed = lastUpdate.trim()
  if (!trimmed) return null
  const iso = new Date(trimmed)
  if (!Number.isNaN(iso.getTime())) return iso
  const dateOnly = new Date(`${trimmed}T00:00:00Z`)
  if (!Number.isNaN(dateOnly.getTime())) return dateOnly
  return null
}

/**
 * Format coarse elapsed time since last_update (e.g. "5m", "2h", "3d").
 * Returns null when the timestamp is missing or unparseable.
 */
export function formatPhaseElapsed(lastUpdate: string, now: Date = new Date()): string | null {
  const parsed = parseLastUpdate(lastUpdate)
  if (!parsed) return null
  const ms = now.getTime() - parsed.getTime()
  if (ms < 0) return null
  const minutes = Math.floor(ms / 60_000)
  if (minutes < 60) return `${Math.max(1, minutes)}m`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h`
  const days = Math.floor(hours / 24)
  return `${days}d`
}
