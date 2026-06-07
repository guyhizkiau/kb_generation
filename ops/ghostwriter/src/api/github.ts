/** GitHub repo slug (owner/name) for KB article PRs. */
export const GITHUB_REPO =
  import.meta.env.VITE_GITHUB_REPO ?? 'guyhizkiau/kb_generation'

/** Link to a pull request on GitHub. */
export function githubPullUrl(prNumber: number): string {
  return `https://github.com/${GITHUB_REPO}/pull/${prNumber}`
}
