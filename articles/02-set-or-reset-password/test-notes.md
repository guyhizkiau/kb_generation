# Test notes — Set or reset your password

**Tester:** Playwright headless (Chromium) driven by `/tmp/run_test_reset.py`.
**Run date:** 2026-05-27.
**Tenant:** `https://app.specterx.com` (production).
**Account:** Guy's signed-in account (`SPECTERX_USERNAME`).

## Limitation acknowledged up front

Per `WORKFLOW.md §5.3`, submitting the **Reset** button on a real
account would trigger a real password-reset email for Guy and let his
next interactive sign-in fail. The test therefore covers the
**user-visible flow up to the email-sending step**, not the
post-submit screens. Step-2 UI strings are sourced from the codebase
(see `research/codebase-findings.md`).

### Why the end-to-end flow was not captured (re PR#4 review)

The blocker is the single shared test account (`SPECTERX_USERNAME` in
`~/.config/specterx-kb/.env`). Submitting **Reset** against that
account would:

1. Invalidate Guy's current password on the live production tenant.
2. Send the verification code to Guy's real inbox, where the pipeline
   has no programmatic read access — capturing the code requires a
   human to open the mail.
3. Force the next person who needs the test account (this article's
   future revalidation, article 03's drafting, etc.) to perform an
   interactive sign-in with a new password.

To capture the **Create New Password** screen and the post-submit
success state in a real session, the pipeline needs **either**:

- A dedicated disposable test account on a non-production tenant whose
  password can be reset freely, with mailbox access the pipeline can
  read (IMAP or a forwarder), **or**
- One-off written consent from Guy to reset his account's password as
  part of this article's capture pass.

Until one of those is available, step-2 UI strings continue to come
from the codebase (`general.json:22-29` for password rules and submit
button label; `EnterCode` and `CreateNewPassword` components for the
field structure) and `research/codebase-findings.md` for the success
toast text.

## Steps executed

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

- Action: **skipped** (would email Guy's account).
- Result: N/A.
- Coverage: step-2 UI strings sourced from
  `research/codebase-findings.md` and from `general.json` lines
  1089–1130. All five password-rule labels and exact submit-button
  text are verbatim from `general.json:22-29`.

## Glossary candidates surfaced

- **Reset password** (lower-case `p`, exact link text and page title).
- **Sign in with One Time Code** (alternative button on `/forgotPassword`,
  conditional).
- **Change Password** (step-2 submit, two capitals).
- **Verification code** (the 6-digit code sent by email; pick "code"
  in body prose).

## Known limitations

- Step-2 (`/forgotPassword` after submit) and the success toast were
  not captured because we don't want to actually reset Guy's password.
- The activation-email flow for admin-invited new users was not
  captured. The codebase confirms that flow reaches the same
  `/forgotPassword` and `/confirmUser` components.
- The article does not document the admin-side reset path
  (`admin.specterx.com`); that is a different application and a
  different article scope.
