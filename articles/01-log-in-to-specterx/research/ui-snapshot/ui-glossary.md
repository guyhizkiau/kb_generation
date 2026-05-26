# UI glossary — Log in to the SpecterX web platform

- Captured: 2026-05-26 (screenshots reused from `workspace/articles/01-login/screenshots/`,
  which were captured 2026-05-26T14:04Z by the local Playwright runner
  against the production tenant `app.specterx.com`).
- SpecterX build: unknown from the live UI; no version string is
  exposed on the sign-in page or in the dashboard chrome that was
  captured. Treat as "live production as of 2026-05-26."
- Source files in this directory:
  - `00-login-page.png` — the sign-in page at `/signIn`
  - `02-dashboard.png` — the post-login My Files page (**not
    committed**: flagged for PII; the original lives at
    `screenshots/_flagged/02-dashboard.png` in this article directory,
    which is git-ignored)

## Page: SpecterX sign-in (`https://app.specterx.com/signIn`)

The browser tab title is `Login - SpecterX`. The visible URL the user
ends up on is `https://app.specterx.com/signIn` — typing
`https://app.specterx.com` redirects there automatically.

What's visible on the page, from top to bottom:

- **SpecterX logo** in the page header.
- A primary, full-width button labeled **"Sign in with Google"** with
  a small Google `G` icon to the left.
- A horizontal divider with the centred text **"or sign in with"**.
- An unlabelled email input with the placeholder **"Enter your email"**.
- An unlabelled password input with the placeholder **"Enter your
  password"**. A small eye icon sits inside the right edge of the
  field; clicking it toggles password visibility.
- A primary submit button labeled exactly **"Sign In"** (capital S,
  capital I — distinct from "Sign in with Google"). The button starts
  greyed out and becomes active only when both fields contain text.
- A text link **"Reset password"** below the Sign In button, for the
  password-reset flow (covered by cluster article 02).

What is **not** visible on the page in our captured screenshot:

- No "Sign in with Microsoft", "Sign in with Okta", or generic SSO
  button. The Entra ID / Okta / Google Cloud Identity SSO flows
  described in `editorial/ARTICLES_PLAN.md` are presumably triggered by
  going to an organisation-specific subdomain (e.g.
  `yourorg.specterx.com`), not from the shared `app.specterx.com`
  sign-in page. Treat this as `[verify in test]` in the draft and call
  it out in the troubleshooting section.
- No "Remember me" checkbox, no "Sign up" link, no language selector.

## Page: My Files dashboard (`https://app.specterx.com/my-files`)

The browser tab title after a successful sign-in is `My Files -
SpecterX`. The page lands at `/my-files` (this is the post-login
landing page for the `guy@specterx.com` test account; other accounts
may land elsewhere depending on tenant configuration — `[verify in
test]`).

Visible elements:

- A left-hand navigation rail with section icons (folders, shared,
  recent, etc. — labels not all visible in the captured screenshot).
- The main content area heading reads **"My Files"**.
- The signed-in user's email address appears in the top-right of the
  page header.

## Differences vs `canon/GLOSSARY.md`

`canon/GLOSSARY.md` is currently a header-only stub (this is the first
article in the pipeline). No diff to perform. New terms this article
would propose for inclusion in the glossary when it's first populated:

- **Sign in** (preferred verb; the button is labelled "Sign In")
- **My Files** (the default post-login landing page in V1)
- **Reset password** (the link text on the sign-in page)
- **Sign in with Google** (canonical label; do **not** rewrite as
  "Google SSO" or "Google login" in article body)

## Items flagged `[verify in test]`

1. Whether `https://app.specterx.com` or
   `https://yourorg.specterx.com` is the right URL to send a reader to
   when the org uses SSO. The plan entry suggests both URL forms are
   in production; only `app.specterx.com` was reachable in this recon.
2. Whether SSO orgs see a different sign-in page (e.g. only an SSO
   button, no email/password form). Not exercised on this account.
3. Whether the post-login URL is always `/my-files` for every user or
   depends on tenant configuration.
