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
