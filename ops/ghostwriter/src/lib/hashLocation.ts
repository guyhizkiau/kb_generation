import type { AppView } from '@/components/NavSidebar'

/** Full navigation state encoded in the URL hash. */
export interface NavState {
  view: AppView
  clusterId: string | null
  feedbackSlug: string | null
  readerSlug: string | null
}

const VIEWS: readonly AppView[] = ['articles', 'health', 'feedback', 'settings']

function isView(value: string): value is AppView {
  return (VIEWS as readonly string[]).includes(value)
}

export const DEFAULT_NAV_STATE: NavState = {
  view: 'articles',
  clusterId: null,
  feedbackSlug: null,
  readerSlug: null,
}

/**
 * Parse a location hash (e.g. `#/articles/cluster-1?read=01-slug`) into a
 * {@link NavState}. Falls back to {@link DEFAULT_NAV_STATE} for empty or
 * unrecognized hashes so the app always lands on a valid view.
 */
export function parseHash(hash: string): NavState {
  const raw = hash.replace(/^#/, '').replace(/^\//, '')
  if (!raw) return { ...DEFAULT_NAV_STATE }

  const [path, query = ''] = raw.split('?')
  const segments = path!.split('/').filter(Boolean)
  const viewSegment = segments[0] ?? 'articles'
  const view = isView(viewSegment) ? viewSegment : 'articles'

  const readerSlug = new URLSearchParams(query).get('read')

  const state: NavState = {
    view,
    clusterId: null,
    feedbackSlug: null,
    readerSlug: readerSlug || null,
  }

  if (view === 'articles') {
    state.clusterId = segments[1] ?? null
  } else if (view === 'feedback') {
    state.feedbackSlug = segments[1] ?? null
  }

  return state
}

/** Serialize a {@link NavState} back into a location hash string. */
export function buildHash(state: NavState): string {
  const segments: string[] = [state.view]

  if (state.view === 'articles' && state.clusterId) {
    segments.push(state.clusterId)
  } else if (state.view === 'feedback' && state.feedbackSlug) {
    segments.push(state.feedbackSlug)
  }

  let hash = `#/${segments.join('/')}`

  if (state.readerSlug) {
    hash += `?read=${encodeURIComponent(state.readerSlug)}`
  }

  return hash
}
