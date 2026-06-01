# Test notes — Set or reset your password

**Tester:** Playwright headed Chromium on Xvfb `:99`
(latest: `/tmp/run_reset_e2e_v13.py`).
**Run dates:** 2026-05-27 (initial), 2026-06-01 (re-capture pass),
2026-06-01 11:10 UTC (end-to-end completion after admin provisioned
the test user).
**Tenant:** `https://app.specterx.com` (production).
**Account used for the reset trigger:** `TEST_RECIPIENT_EMAIL`
(`davidch@specterx.com`).

## Limitation acknowledged up front

Per `WORKFLOW.md §5.3`, submitting **Reset** against Guy's working
account (`SPECTERX_USERNAME`) would invalidate his live production
password. PR #4 introduced a dedicated test recipient
(`TEST_RECIPIENT_EMAIL`) with a Gmail mailbox the pipeline can read,
specifically to unblock end-to-end capture for this article.

## 2026-06-01 end-to-end pass (v13) — SUCCESS

After the admin provisioned `davidch@specterx.com` in the SpecterX
tenant (PR#4 review comment, 2026-06-01), the v13 pipeline run
completed the password-reset flow end-to-end on the first attempt:

```
STEP: SpecterX: open /signIn (fresh profile)
STEP: SpecterX: click Reset password
STEP: SpecterX: fill email and submit Reset
  'Create New Password' visible
STEP: Gmail: poll Inbox and Spam for the fresh reset code
  attempt 1 #spam row[3]: 00**** (code 001895, fresh ≠ KNOWN_OLD_CODES)
STEP: SpecterX: type code in 'Enter the code' field
STEP: SpecterX: type new password in 'Create your password'
STEP: SpecterX: click Change Password
STEP: SpecterX: wait for redirect/success
  redirected to https://app.specterx.com/forgotPassword/signIn
  success toast count=1  ("Your password has been successfully changed")
rc=0
```

### Captured artifacts (v13)

| File | Content |
| --- | --- |
| `screenshots/_all/v13-01-signin.png` | SpecterX `/signIn`, clean. |
| `screenshots/_all/v13-02-forgot-empty.png` | `/forgotPassword`, empty. |
| `screenshots/_all/v13-03-forgot-filled-raw.png` | Email filled, pre-Reset. |
| `screenshots/_all/v13-04-create-new-password-empty.png` | Step-2 page after Reset. |
| `screenshots/_all/v13-05-create-new-password-filled.png` | Step-2 page with code (redacted) + password entered, button active. |
| `screenshots/_all/v13-gmail-inbox.png` | Spam listing with the fresh `Your verification code is 001895` row. |
| `screenshots/_all/v13-gmail-email.png` | Opened verification email body (header redacted). |
| `screenshots/_all/v13-06-after-submit.png` | `/signIn` redirect with the `Your password has been successfully changed` toast. |

### Promoted into the article

The previously-missing end-to-end screenshots were promoted into
`screenshots/`:
- `10-password-reset-success.png` — success toast on `/signIn` (from
  `_all/v13-06-after-submit.png`).
- `11-reset-code-email-body.png` — opened verification email showing
  the 6-digit code (from `_all/v13-gmail-email.png`).

`08-create-new-password-empty.png` was promoted earlier in the
2026-06-01 morning pass; the v13 re-capture matches that screen
verbatim, so the existing file is kept.

### Observations from the v13 successful pass

- **Sender domain.** The verification email arrives from
  `no-reply@verificationemail.com`, not directly from `@specterx.com`.
  The article wording was updated to mention this so users do not
  discard it as spam from an unknown sender.
- **Spam classification.** Gmail places the verification email in
  Spam, not Inbox, on a fresh mailbox. The article's existing
  "check your spam or junk folder" guidance is therefore correct.
- **Redirect URL.** After `Change Password`, the page redirects to
  `/forgotPassword/signIn` (a nested path), not the bare `/signIn`.
  The sign-in form on that page is identical to the regular one and
  the success toast renders for ~3 seconds.
- **Rate limit.** Repeated `Reset` submissions within ~15 minutes
  produce `We have had an error` (Cognito `Attempt limit exceeded`).
  This article does not document that error because end users would
  not normally hit it; it is recorded here only as a test-environment
  note for future pipeline runs.

## Historical: 2026-06-01 morning re-capture pass — blocked (now resolved)

The earlier morning pass got past the Gmail-login wall but stopped at
a then-unknown blocker: the SpecterX reset request for
`TEST_RECIPIENT_EMAIL` did **not** deliver a verification email.

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

### Resolution

The admin provisioned `davidch@specterx.com` later the same day; the
v13 pass above completed end-to-end and the previously-missing
post-Reset screenshots were promoted into the article. Step-2 UI
strings observed live now match the codebase-sourced strings
(`general.json:22-29` for password rules and submit-button label;
`EnterCode` and `CreateNewPassword` components for the field
structure) verbatim, so no article wording changed.

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

- The activation-email flow for admin-invited new users was not
  captured. The codebase confirms that flow reaches the same
  `/forgotPassword` and `/confirmUser` components.
- The article does not document the admin-side reset path
  (`admin.specterx.com`); that is a different application and a
  different article scope.
