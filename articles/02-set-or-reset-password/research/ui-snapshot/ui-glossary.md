# UI glossary — Set or reset your password

- Captured: 2026-05-27 by `/tmp/run_test_reset.py` (Playwright headless,
  Chromium, 1280×900 viewport) against the production tenant
  `https://app.specterx.com`.
- SpecterX build: not exposed in the UI (no version string on the
  sign-in or reset pages). Treat as "live production as of 2026-05-27."
- Raw notes: `raw-notes.txt` (this directory).
- Source files in this directory (after triage):
  - `00-sign-in-with-reset-link.png` — sign-in page with **Reset
    password** link visible.
  - `01-reset-page.png` — `/forgotPassword` step-1 page.

## Page: SpecterX sign-in (`https://app.specterx.com/signIn`)

Browser tab title: `Login - SpecterX`. URL: `/signIn`.

Visible from top to bottom:

- SpecterX logo (top left).
- Language switcher dropdown (top right; defaults to **English**).
- Page heading **Welcome to SpecterX**.
- Full-width button **Sign in with Google** with a Google `G` icon.
- Horizontal divider with the centred text **or sign in with**.
- Unlabelled email input, placeholder **Enter your email**.
- Unlabelled password input, placeholder **Enter your password**,
  with an eye icon on the right to toggle visibility.
- Primary submit button labelled **Sign In** (capital S, capital I).
  Disabled until both fields contain text.
- Text link **Reset password** directly below the **Sign In** button.
  This is the entry point for the article.

## Page: Reset password — step 1 (`https://app.specterx.com/forgotPassword`)

Browser tab title: `Reset password - SpecterX`. URL: `/forgotPassword`.

Visible from top to bottom:

- SpecterX logo (top left).
- Language switcher dropdown (top right).
- Page heading **Reset password** (lower-case `p`).
- Full-width button **Sign in with One Time Code**. **Conditional**:
  only visible when the user's IP is allowed to use OTP (the
  `DISABLE_OTP_BEHIND_PROXY` flag is off for this network). Article
  should not depend on the button being shown.
- Horizontal divider with the centred text **or create a new password**.
- Unlabelled email input, placeholder **Enter your email**.
- Primary submit button labelled **Reset** (capital R). Disabled until
  the email field passes the local validator (`validateEmail`).
- Text link **Back to Sign In** below the **Reset** button.

There is no inline subtitle or instructional copy on the page. The
copy below the title goes straight from the page heading to the OTP
button (when shown) or to the form.

## Page: Reset password — step 2

**Not captured.** Reaching step 2 requires submitting the form, which
triggers a real password-reset email for the test account. Per
`WORKFLOW.md §5.3`, we do not exercise this in automated tests against
Guy's production account. UI strings for step 2 are documented in
`research/codebase-findings.md` from the source.

## Page: First-time activation

**Not captured.** Reaching the first-time activation page requires a
new admin invitation, which we don't trigger here. The activation flow
re-uses the same `/forgotPassword` and `/confirmUser` React components
(see `research/codebase-findings.md`), so the visible UI is the same
as the reset flow.

## Items flagged `[verify in test]`

1. Whether the **Sign in with One Time Code** button appears for all
   end-user IPs (proxy-fronted enterprise users may not see it). The
   article does not promise it; it is referenced only as an "if shown"
   alternative.
2. Whether the activation email (admin-invited new users) renders
   exactly the same step-2 UI as the reset email's step-2 UI. The
   codebase shares the components; visual identity unconfirmed.

## Differences vs `canon/GLOSSARY.md`

`canon/GLOSSARY.md` does not exist in this repo (no canon directory
yet). Terms this article would propose for inclusion in the glossary
when it's first populated:

- **Reset password** (lower-case `p` — the exact link text and page
  title).
- **Sign in with One Time Code** (canonical label; do not rewrite as
  "OTP" or "one-time password" in article body).
- **Change Password** (the step-2 submit button, two capitals).
- **Verification code** (the 6-digit number sent by email; the UI
  alternates between "code" and "verification code"; pick "code").
