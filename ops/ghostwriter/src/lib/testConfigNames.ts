/** Realistic test file name generator for Settings UI. */

const ADJECTIVES = [
  'quarterly', 'annual', 'vendor', 'client', 'project', 'budget', 'compliance',
  'internal', 'draft', 'final', 'signed', 'review',
]

const NOUNS = [
  'report', 'contract', 'summary', 'invoice', 'proposal', 'brief', 'memo',
  'checklist', 'analysis', 'statement',
]

const FOLDER_PREFIXES = ['KB-Test', 'Share-Test', 'Upload-Test']

function pick<T>(items: readonly T[]): T {
  return items[Math.floor(Math.random() * items.length)]!
}

function slugPart(text: string): string {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
}

/** Generate a single realistic file name with the given extension. */
export function generateFileName(ext = 'pdf'): string {
  const adj = pick(ADJECTIVES)
  const noun = pick(NOUNS)
  const year = new Date().getFullYear()
  return `${adj}-${noun}-${year}.${ext.replace(/^\./, '')}`
}

/** Generate a list of distinct file names. */
export function generateFileList(count: number, ext = 'pdf'): string[] {
  const names = new Set<string>()
  while (names.size < count) {
    names.add(generateFileName(ext))
  }
  return [...names]
}

/** Generate a folder name for upload tests. */
export function generateFolderName(): string {
  const prefix = pick(FOLDER_PREFIXES)
  const date = new Date().toISOString().slice(0, 10)
  return `${prefix}-${date}`
}

/** Generate file names for inside a folder (mixed extensions). */
export function generateFolderFiles(count = 3): string[] {
  const exts = ['pdf', 'pdf', 'txt', 'png']
  const names = new Set<string>()
  let i = 0
  while (names.size < count) {
    const ext = exts[i % exts.length] ?? 'txt'
    names.add(generateFileName(ext))
    i += 1
  }
  return [...names]
}

/** Convert a role key to a human label. */
export function roleLabel(role: string): string {
  const known: Record<string, string> = {
    data_owner: 'Data owner',
    recipient: 'Recipient',
  }
  if (known[role]) return known[role]
  return role
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}

/** Suggest a new custom role key from a display name. */
export function suggestRoleKey(label: string): string {
  return slugPart(label) || `account_${Date.now()}`
}
