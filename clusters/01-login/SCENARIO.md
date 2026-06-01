# Scenario — cluster 01-login

This is the test-world setup for the three login articles in this
cluster. The cluster runs against the production tenant at
`app.specterx.com` (we do not have a separate staging tenant for tests).

## Articles in this cluster

1. `01-log-in-to-specterx` — log in to the SpecterX web platform
2. `02-set-or-reset-password` — set or reset your password
3. `03-what-is-specterx` — what is SpecterX (overview article)

## Target environment

- Hostname: `app.specterx.com`
- Account: `guy@specterx.com` (credentials in `~/.config/specterx-kb/.env`
  as `SPECTERX_USERNAME` and `SPECTERX_PASSWORD`)
- Tenant identity provider for `guy@specterx.com`: email + password
  (the account is not SSO-bound); SSO sign-in flows must be described
  from product documentation, not exercised, on this account.

## Baseline state before each article's test

Every article in this cluster starts from a **logged-out** browser.

- For the local Playwright runner: launch a fresh Chromium with a clean
  user-data dir (the default in `tester/browser_runner.py` for `local`
  mode creates a fresh context per run, so no cookie cleanup is needed).
- For CDP mode against the VM Chrome: clear cookies for
  `app.specterx.com` (or open an incognito CDP context) before each
  article's test plan executes.

After each article's test, no cleanup is required for cluster 01 —
sessions expire on their own and no shared state is created.

## Article-specific constraints

### 01-log-in-to-specterx

- Exercise the email-plus-password sign-in flow only (the account is
  not SSO).
- Capture two screenshots: the sign-in page (`/signIn`) and the
  post-login dashboard (`/my-files`).
- Do not surface the real account email in screenshots if avoidable;
  blur or redact before publishing per `tester/sensitive-terms.txt`.

### 02-set-or-reset-password

- **Do not run the reset flow against `SPECTERX_USERNAME`** (Guy's
  working account). Resetting his password mid-flow blocks every other
  article in the cluster.
- For runs that need to exercise the end-to-end flow (read the
  verification code, capture the **Create New Password** screen, and
  capture the post-submit success state), use the dedicated test
  account documented in `tester/TEST_RESOURCES.md`
  (`TEST_RECIPIENT_EMAIL` / `TEST_RECIPIENT_GMAIL_PASSWORD`). The
  pipeline can log into that account's Gmail to read the verification
  code without needing Guy to forward it.
- For lightweight runs that only need the entry-point screens (the
  sign-in page's **Reset password** link and the `/forgotPassword`
  request form), capture those only and stop before submit. The
  current `final.md` was produced this way and remains valid.

### 03-what-is-specterx

- Overview article — no procedural test plan; treated as
  `validation: skipped` in the pipeline. Screenshots, if any, come from
  the live dashboard captured during article 01.
