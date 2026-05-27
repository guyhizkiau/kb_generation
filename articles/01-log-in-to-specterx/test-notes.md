# test-notes — 01-log-in-to-specterx

Generated: 2026-05-26T19:17:41+00:00
Backend: playwright local chromium (headless, fresh context, viewport 1280x800)
Plan step IDs: 01-navigate, 02-fill-email, 03-fill-password, 04-click-signin, 05-dashboard

## UI facts observed

Reusable observations the writer will use when reconciling draft-1 -> draft-2:

- Sign-in URL the app actually serves: `https://app.specterx.com/signIn` (typing `https://app.specterx.com` redirects there).
- Browser tab title on the sign-in page: `Login - SpecterX`.
- The sign-in page shows a primary **Sign in with Google** button at the top, an `or sign in with` divider, then the email + password form, then a **Sign In** submit button, then a **Reset password** link.
- Email field placeholder: `Enter your email` (no label).
- Password field placeholder: `Enter your password` (no label); an eye icon at the right toggles visibility.
- The **Sign In** button is greyed out until both fields are populated.
- After a successful sign-in the user lands at `https://app.specterx.com/my-files` with tab title `My Files - SpecterX`.

## Step 01-navigate — ok

- description: navigate to https://app.specterx.com
- observation: loaded url=https://app.specterx.com/signIn title='Login - SpecterX'
- screenshot: `screenshots/_all/01-login-page.png`

## Step 02-fill-email — ok

- description: fill email field with guy@specterx.com
- observation: email filled; selector strategy worked

## Step 03-fill-password — ok

- description: fill password field
- observation: password filled (value redacted)

## Step 04-click-signin — ok

- description: click sign-in button
- observation: clicked sign-in button; button_text='Sign In'

## Step 05-dashboard — ok

- description: wait for dashboard to load
- observation: post-login url=https://app.specterx.com/my-files title='My Files - SpecterX'
- screenshot: `screenshots/_flagged/02-dashboard.png` (see PII note below)

## PII review

`screenshots/_all/01-login-page.png` was reviewed against
`tester/sensitive-terms.txt` and the general PII guidance in
`CLAUDE.md`. It shows no PII — the sign-in page is anonymous.

`screenshots/_all/02-dashboard.png` was reviewed and **flagged**: the
captured My Files list contained real internal data —

- The signed-in user's email (`guy@specterx.com`) in the page chrome.
- Filenames referencing internal legal artifacts ("Equity Grant
  Letter", "Option Plan [Barnea]", "Employment Agreement", "MSA
  SPECTERX N.D. LTD ...", "Super Secret Document.docx").
- Names of internal SpecterX colleagues in the "Last Used" column.

Per `CLAUDE.md` ("PII / customer data must never appear in screenshots
that get committed") and `WORKFLOW.md` section 12 rule 6, this
screenshot was moved to `screenshots/_flagged/` (git-ignored) and
**not** used in `draft-2.md` / `final.md`. The article's "confirm
you've reached your dashboard" step describes the landing page
textually instead. A future capture against a clean tenant account
(empty My Files, or an account configured for KB screenshots) can
replace it.
