import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'

interface ReaderContextValue {
  readerSlug: string | null
  openReader: (slug: string) => void
  closeReader: () => void
}

const ReaderContext = createContext<ReaderContextValue | null>(null)

export function ReaderProvider({ children }: { children: ReactNode }) {
  const [readerSlug, setReaderSlug] = useState<string | null>(null)

  const openReader = useCallback((slug: string) => setReaderSlug(slug), [])
  const closeReader = useCallback(() => setReaderSlug(null), [])

  return (
    <ReaderContext.Provider value={{ readerSlug, openReader, closeReader }}>
      {children}
    </ReaderContext.Provider>
  )
}

export function useReader(): ReaderContextValue {
  const ctx = useContext(ReaderContext)
  if (!ctx) throw new Error('useReader must be used within ReaderProvider')
  return ctx
}
