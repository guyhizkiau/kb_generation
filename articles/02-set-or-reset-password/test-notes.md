# Test notes — Set or reset your password

**Tester:** Playwright headed Chromium on Xvfb `:99`
(`/tmp/run_reset_e2e_v7.py`).
**Run dates:** 2026-05-27 (initial), 2026-06-01 (re-capture pass).
**Tenant:** `https://app.specterx.com` (production).
**Account used for the reset trigger:** `TEST_RECIPIENT_EMAIL`
(`davidch@specterx.com`).

## Limitation acknowledged up front

Per `WORKFLOW.md §5.3`, submitting **Reset** against Guy's working
account (`SPECTERX_USERNAME`) would invalidate his live production
password. PR #4 introduced a dedicated test recipient
(`TEST_RECIPIENT_EMAIL`) with a Gmail mailbox the pipeline can read,
specifically to unblock end-to-end capture for this article. The 2026-06-01
pass uses that account.

## 2026-06-01 re-capture pass — outcome

The pass got past the previous Gmail-login wall but stopped at a new
blocker: the SpecterX reset request for `TEST_RECIPIENT_EMAIL` does
**not** deliver a verification email.

### What worked

1. **Env-precedence bug fixed.** The shell that runs the pipeline has
   a stale `TEST_RECIPIENT_GMAIL_PASSWORD` value (length 6). The real
   value in `~/.config/specterx-kb/.env` is length 18. Prior takes
   (v4/v5/v6) used `os.environ.setdefault`, which kept the wrong
   shell-inherited value and produced "Wrong password" on every Gmail
   sign-in. v7 force-overrides from the `.env` file and Gmail web
   login then succeeds:
   ```
   STEP: Gmail: wait for mailbox or challenge
     host transition → accounts.google.com
     host transition → mail.google.com
     reached mailbox host=mail.google.com
   ```
2. **Inbox access confirmed.** Inbox, All Mail, Spam, and label-scoped
   searches all load — only the two Gmail-onboarding messages from
   2026-05-27 are present.

### What did not work

3. **No SpecterX verification email arrives.** After clicking **Reset**
   on `/forgotPassword` with `davidch@specterx.com`, the UI stays on
   the same page (Step 2 "Create New Password" never appears) and no
   email lands in Inbox, All Mail, or Spam within an 8+ minute polling
   window. Three independent searches confirm this:
   - `from:specterx.com newer_than:1h` → 0 hits
   - `cognito` → 0 hits
   - `from:noreply` → 0 hits (apart from the two Gmail Team welcomes)
4. **Direct sign-in with `TEST_RECIPIENT_GMAIL_PASSWORD` also fails**
   on `/signIn` for `davidch@specterx.com` ("Incorrect username or
   password"). Cognito does not distinguish "user not found" from
   "wrong password" in this string, so this is ambiguous on its own,
   but combined with (3) it is consistent with the account not being
   provisioned in SpecterX's Cognito user pool.

### Most likely cause

`davidch@specterx.com` exists as a Google Workspace mailbox (we read
it directly) but has not been invited into the SpecterX tenant.
SpecterX's reset endpoint correctly suppresses user enumeration: an
unregistered email gets the same silent UI response as a real reset,
and no email is sent. The article already documents this behavior in
the troubleshooting section ("SpecterX does not tell you whether an
address is registered; if you enter a typo or an unregistered
address, the page silently looks the same.").

### What this needs from a human

1. Provision `davidch@specterx.com` in the SpecterX tenant (admin
   portal → Users → invite). The first-time-setup email will go to
   the same `davidch@specterx.com` Gmail inbox the pipeline can read,
   and that single delivery also confirms end-to-end Cognito → SES →
   inbox plumbing works for this address.
2. After the account is active, a future pipeline run can rerun
   `/tmp/run_reset_e2e_v7.py` (or its successor) and capture the
   verification-email and post-submit screens unattended.

Until then, step-2 UI strings remain sourced from the codebase
(`general.json:22-29` for password rules and submit button label;
`EnterCode` and `CreateNewPassword` components for the field
structure) and `research/codebase-findings.md` for the success-toast
text — the article body is correct, only the screenshots after the
"Reset" submit are still missing.

## Captured artifacts (v7)

| File | Content |
| --- | --- |
| `screenshots/_all/v7-01-sign-in.png` | SpecterX `/signIn`. |
| `screenshots/_all/v7-02-forgot-empty.png` | `/forgotPassword`, empty form. |
| `screenshots/_all/v7-03-forgot-filled-raw.png` | `/forgotPassword`, email filled, pre-Reset. |
| `screenshots/_all/v7-gmail-inbox.png` | Gmail inbox (redacted), `from:specterx.com newer_than:1h` → no hits. |
| `screenshots/_all/v7-gmail-email.png` | Gmail "email view" attempt (nothing to open). |
| `screenshots/_all/v7-mailbox-all-mail.png` | All Mail listing (redacted). |
| `screenshots/_all/v7-mailbox-spam.png` | Spam listing (redacted). |
| `research/ui-snapshot/raw-notes-e2e.txt` | Full transcript of the run. |

## Steps executed (2026-05-27 pass, unchanged below)

### Step 01 — Navigate to the sign-in page

- Action: `goto https://app.specterx.com/signIn`.
- Result: SUCCESS.
- Page title: `Login - SpecterX`.
- Screenshot: `screenshots/_all/01-sign-in.png` (promoted to
  `screenshots/01-sign-in-with-reset-link.png`).
- Verify "Reset password link is visible below Sign In": PASS
  (`get_by_role("link", name="Reset password").is_visible()` returned
  true).
- Observations:
  - The page lands at `/signIn` directly; no redirect from `/`.
  - The **Reset password** link is text (no underline by default;
    underlined on hover in the cropped detail).
  - No "Sign up" link is shown (consistent with admin-driven
    provisioning).

### Step 02 — Crop the reset-link region

- Action: bounding-box lookup on the **Reset password** link, then
  `page.screenshot` with a `clip` rectangle.
- Result: SUCCESS.
- Screenshot: `screenshots/02-reset-link-detail.png`.
- The crop shows the bottom of the password field, the **Sign In**
  button (disabled state), and the **Reset password** link
  immediately below.

### Step 03 — Click "Reset password" to open `/forgotPassword`

- Action: `get_by_text("Reset password", exact=True).first.click()`.
- Result: SUCCESS.
- Final URL: `https://app.specterx.com/forgotPassword`.
- Page title: `Reset password - SpecterX`.
- Screenshot: `screenshots/03-reset-page-step1.png`.
- Verify "Page title equals 'Reset password'": PASS.
- Verify "Submit button reads 'Reset'": PASS
  (`button[0].inner_text() == "Reset"`).
- Verify "Email field placeholder is 'Enter your email'": PASS
  (`input[1].placeholder == "Enter your email"`).
- Observations:
  - The **Sign in with One Time Code** button is visible on this
    machine (so `DISABLE_OTP_BEHIND_PROXY` is off here). The article
    treats this button as conditional.
  - The codebase advertises a `firstStep.title` translation key
    `"You can reset it by entering your email address and clicking
    \"Reset\""`. That string does **not** render in the live UI —
    the EnterEmail component never reads it. The page is
    title + form, no inline subtitle.
  - The first `<input>` on the page is the language-switcher search
    combobox (Ant Design). The email field is `input[1]`. Article
    text avoids this distinction.

### Step 04 — Step-2 (code + new password)

- Action: **attempted** on 2026-06-01 using `TEST_RECIPIENT_EMAIL`;
  see the re-capture-pass section above. The Step-2 screen did not
  appear because no email was delivered.
- Coverage: step-2 UI strings remain sourced from
  `research/codebase-findings.md` and `general.json` lines
  1089–1130. All five password-rule labels and the exact submit-button
  text are verbatim from `general.json:22-29`.

## Comparison against public KBs (re PR#4 review)

Re-read `research/competitor-coverage.md` after the re-capture pass.
Nothing in the captured Egnyte/Dropbox/HubSpot articles describes the
mailbox/code-fetch step in a way that would change what the article
already says — all three vendors use a clickable link, not a 6-digit
code, so SpecterX's prose at step 3 ("Open the email and copy the
code. The message comes from an `@specterx.com` sender. If you do not
see it within a minute or two, check your spam or junk folder.") is
intentionally divergent. No article changes follow from the
competitor scan; the gap that remains is the end-to-end screenshot
set, not the wording.

## Glossary candidates surfaced

- **Reset password** (lower-case `p`, exact link text and page title).
- **Sign in with One Time Code** (alternative button on `/forgotPassword`,
  conditional).
- **Change Password** (step-2 submit, two capitals).
- **Verification code** (the 6-digit code sent by email; pick "code"
  in body prose).

## Known limitations

- Step-2 (`/forgotPassword` after submit) and the success toast are
  still not captured — the 2026-06-01 attempt was blocked by the
  `TEST_RECIPIENT_EMAIL` provisioning gap described above.
- The activation-email flow for admin-invited new users was not
  captured. The codebase confirms that flow reaches the same
  `/forgotPassword` and `/confirmUser` components.
- The article does not document the admin-side reset path
  (`admin.specterx.com`); that is a different application and a
  different article scope.
