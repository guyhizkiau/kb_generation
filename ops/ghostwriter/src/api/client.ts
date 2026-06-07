/** API origin — empty string uses same origin (Vite dev proxy). */
export function resolveApiBase(): string {
  const env = import.meta.env.VITE_API_BASE?.trim()
  if (!env) return ''
  return env.replace(/\/$/, '')
}

/** Full URL for an API or static path. */
export function apiUrl(path: string): string {
  return `${resolveApiBase()}${path}`
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(apiUrl(path), {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })
  if (!res.ok) {
    const err = await res.text()
    throw new Error(`${res.status} ${err}`)
  }
  return res.json() as Promise<T>
}
