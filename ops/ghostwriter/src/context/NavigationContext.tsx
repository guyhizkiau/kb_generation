import {
  createContext, useContext, useState, useEffect, useRef, useCallback,
  type ReactNode,
} from 'react'
import type { AppView } from '@/components/NavSidebar'
import { buildHash, parseHash, type NavState } from '@/lib/hashLocation'

interface NavigationContextValue extends NavState {
  setView: (view: AppView) => void
  setClusterId: (id: string | null) => void
  setFeedbackSlug: (slug: string | null) => void
  openReader: (slug: string) => void
  closeReader: () => void
}

const NavigationContext = createContext<NavigationContextValue | null>(null)

function readHash(): NavState {
  return parseHash(typeof window !== 'undefined' ? window.location.hash : '')
}

export function NavigationProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<NavState>(readHash)

  // The hash we last wrote, so the listener can ignore our own writes and only
  // react to genuine back/forward navigation.
  const lastHashRef = useRef<string>(buildHash(state))

  // State is the single source of truth; mirror it into the URL hash so the
  // location survives a refresh and can be shared. Each navigation adds a
  // history entry so the browser back/forward buttons work.
  useEffect(() => {
    const hash = buildHash(state)
    lastHashRef.current = hash
    if (window.location.hash !== hash) {
      window.location.hash = hash
    }
  }, [state])

  // Back/forward: re-parse the hash. We skip events for our own writes
  // (hash already matches what we wrote) and the empty-hash resets that some
  // environments fire spuriously — the app always maintains a non-empty hash,
  // so a truly empty hash never represents a real destination.
  useEffect(() => {
    const onHashChange = () => {
      const current = window.location.hash
      if (!current || current === lastHashRef.current) return
      setState(readHash())
    }
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  const setView = useCallback(
    (view: AppView) => setState((prev) => ({ ...prev, view })),
    [],
  )
  const setClusterId = useCallback(
    (clusterId: string | null) => setState((prev) => ({ ...prev, clusterId })),
    [],
  )
  const setFeedbackSlug = useCallback(
    (feedbackSlug: string | null) => setState((prev) => ({ ...prev, feedbackSlug })),
    [],
  )
  const openReader = useCallback(
    (readerSlug: string) => setState((prev) => ({ ...prev, readerSlug })),
    [],
  )
  const closeReader = useCallback(
    () => setState((prev) => ({ ...prev, readerSlug: null })),
    [],
  )

  return (
    <NavigationContext.Provider
      value={{
        ...state,
        setView,
        setClusterId,
        setFeedbackSlug,
        openReader,
        closeReader,
      }}
    >
      {children}
    </NavigationContext.Provider>
  )
}

export function useNavigation(): NavigationContextValue {
  const ctx = useContext(NavigationContext)
  if (!ctx) throw new Error('useNavigation must be used within NavigationProvider')
  return ctx
}
