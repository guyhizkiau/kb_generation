import { useNavigation } from '@/context/NavigationContext'

interface ReaderContextValue {
  readerSlug: string | null
  openReader: (slug: string) => void
  closeReader: () => void
}

/**
 * Backward-compatible reader API. The reader overlay state now lives in the
 * URL-backed {@link useNavigation} store; this hook is a thin selector so
 * existing call sites keep working.
 */
export function useReader(): ReaderContextValue {
  const { readerSlug, openReader, closeReader } = useNavigation()
  return { readerSlug, openReader, closeReader }
}
