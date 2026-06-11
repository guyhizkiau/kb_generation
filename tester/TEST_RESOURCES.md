# tester/TEST_RESOURCES.md — shared test accounts and inboxes

Resources the pipeline uses when a flow needs to actually receive a
verification email, SMS, or password-reset link — i.e. flows where
hitting the **data owner** account would block the operator.

**Credential values are NOT stored in this repo.** Configure accounts in
Ghostwriter **Settings** (`#/settings`) or edit
`~/.config/specterx-kb/test-config.json` (mode 600, gitignored). Legacy
env vars in `~/.config/specterx-kb/.env` still work as fallbacks when a
config field is empty.

## Config roles (test-config.json → `users.*`)

Each role has three fields:

| Field | Purpose |
| ----- | ------- |
| `email` | SpecterX login address (same as the mailbox for Workspace accounts) |
| `email_password` | **Primary credential** — Gmail/Workspace mailbox password; used to read verification emails and reset SpecterX passwords |
| `specterx_password` | **Optional** SpecterX app login. When empty, the tester bootstraps one automatically via the reset-password flow before the plan runs |

| Role key | Purpose | Typical `value_ref` keys |
| -------- | ------- | ------------------------ |
| `data_owner` | Primary SpecterX login for upload/share tests | `users.data_owner.email`, `users.data_owner.specterx_password` |
| `recipient` | Share recipient, password-reset E2E | `users.recipient.email` |

Add custom roles in Settings when a flow needs another login. Reference them
with `value_ref`: `users.<role>.email` / `users.<role>.specterx_password`.
Legacy `users.<role>.password` still resolves to `specterx_password`.

### Auto-bootstrap (empty SpecterX password)

When a test plan references `users.<role>.specterx_password` and that field
is empty, `tester/runner.py` runs the reset-password flow before executing
steps:

1. Submit `/forgotPassword` for the role's email.
2. Log into Gmail via Playwright and read the 6-digit verification code.
3. Set a generated password on the **Create New Password** screen.
4. Persist it to `test-config.json` so later runs log in directly.

Requires `email` + `email_password` for that role. If Gmail blocks automated
login, the article is BLOCKED with a clear reason — fill the SpecterX
password manually in Settings or log into Gmail once in the VM browser profile.

### Dedicated password-reset / verification-recipient account

Use the configured **`recipient`** role — **not** `data_owner` — whenever
the test plan needs to:

- Trigger a real password-reset email and read the verification code.
- Click an activation / confirm-user link end-to-end.
- Capture the **Create New Password** and post-submit screens for
  `02-set-or-reset-password` (the limitation called out in that
  article's `test-notes.md` § "Limitation acknowledged up front"
  resolves once the test runner reads the inbox via Gmail).

Resetting the recipient account does **not** lock out the data owner's
working account.

### Provisioning prerequisite (learned the hard way on PR #4)

A Google Workspace mailbox for the recipient is **not enough**. The address
must also be invited as an active SpecterX user in the target tenant before
the password-reset flow will work end-to-end. SpecterX is no-enumeration: if
you click **Reset password** for an address that has a mailbox but no
SpecterX user, the UI silently looks identical to a successful submission
and no verification email is ever sent.

When introducing a new test recipient:

1. Ask the admin to invite the address in the SpecterX admin portal
   (Users → invite).
2. Wait for the activation email to arrive in that mailbox.
3. Click the activation link, set the initial password, and verify
   sign-in works once before kicking off the E2E test plan.
4. Only then can the test runner trigger **Reset password** end-to-end
   and expect a verification email.

If a future article's E2E run produces zero reset emails for the
recipient and the SpecterX UI looks normal, the most likely cause is
that the recipient was de-provisioned or never provisioned in the
target tenant. Re-run step 1 before debugging Playwright or Gmail.

## Upload file names (`files.*` in test-config.json)

Configure in Ghostwriter **Settings**:

| Field | Placeholder | Use |
| ----- | ----------- | --- |
| `files.default` | `{{files.default}}` | Single-file upload steps |
| `files.list` | individual names | Multi-select uploads |
| `files.folder` | `{{files.folder}}` | Whole-folder upload |
| `files.folder_files` | — | Contents generated under the folder |

The tester creates missing fixtures under `tester/fixtures/` at run start.

## Ad-hoc throwaway recipient mailboxes — Mailinator

For one-off external-recipient flows (share-to-external, recipient
verification, multi-recipient sharing) where the only requirement is a
real mailbox that can receive mail:

- Use `https://www.mailinator.com/` — public inboxes, no signup, anyone
  with the address can read.
- Pick an address like `specterx-kb-<slug>-<short-uuid>@mailinator.com`
  per test run so inboxes do not collide across articles.
- **Do not send anything containing customer data or production
  secrets** — mailinator inboxes are world-readable by design.

## Dedicated test phone number (for SMS verification flows)

| Field      | Value                                         |
| ---------- | --------------------------------------------- |
| Number     | `+447413464978`                               |
| Env handle | env var `TEST_RECIPIENT_PHONE`                |

Used when a flow needs to send and read an SMS verification code (e.g.
MFA setup, phone-based recipient verification).

### Reading SMS messages via Quackr.io

The number is a Quackr.io receive-only number. Read inbound messages
with:

```
curl -X GET "$QUACKR_API_URL?phoneNumber=$TEST_RECIPIENT_PHONE" \
  -H "x-api-key: $QUACKR_API_KEY"
```

Env vars:

- `QUACKR_API_URL` — base endpoint (e.g. `https://api.quackr.io/receive-sms`)
- `QUACKR_API_KEY` — Quackr.io API key

Response shape (truncated example):

```json
{
  "success": true,
  "data": {
    "messages": [
      { "sender": "Telegram", "message": "Your verification code is: 12345", "timestamp": 1709000000000 },
      { "sender": "Tinder",   "message": "Your code is: 854177",             "timestamp": 1709000060000 }
    ]
  }
}
```

Sort by `timestamp` desc and take the most recent message from the
expected sender. SMS arrival can lag the trigger by 10–60 s — pollers
should retry rather than reading the inbox once.

## Hard rules

- Never paste passwords, API keys, or env values into markdown, drafts,
  screenshots, commit messages, or PR descriptions.
- Do not include configured recipient emails in committed screenshots —
  redact per `tester/sensitive-terms.txt` (configured emails are included
  automatically in screenshot review).
- Mailinator inboxes are public — never send anything sensitive to one.
