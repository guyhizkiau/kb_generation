# tester/TEST_RESOURCES.md — shared test accounts and inboxes

Resources the pipeline uses when a flow needs to actually receive a
verification email, SMS, or password-reset link — i.e. flows where
hitting `SPECTERX_USERNAME` (Guy's working account) would block him.

**Credential values are NOT stored in this repo.** Names below refer to
keys in `~/.config/specterx-kb/.env` (mode 600, gitignored). Source: PR #4
review on `02-set-or-reset-password`.

## Dedicated password-reset / verification-recipient account

| Field          | Value                                             |
| -------------- | ------------------------------------------------- |
| SpecterX email | `davidch@specterx.com`                            |
| Gmail mailbox  | same address — log into Gmail to read messages    |
| Gmail password | env var `TEST_RECIPIENT_GMAIL_PASSWORD`           |
| SpecterX login | same env var (Gmail and SpecterX share the password) |
| Env handle     | env var `TEST_RECIPIENT_EMAIL`                    |

Use this account — **not** `SPECTERX_USERNAME` — whenever the test plan
needs to:

- Trigger a real password-reset email and read the verification code.
- Click an activation / confirm-user link end-to-end.
- Capture the **Create New Password** and post-submit screens for
  `02-set-or-reset-password` (the limitation called out in that
  article's `test-notes.md` § "Limitation acknowledged up front"
  resolves once the test runner reads the inbox via Gmail).

Resetting `davidch@specterx.com` does **not** lock out Guy's working
account.

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

- Never paste any of the values stored in env vars (Gmail password,
  Quackr API key) into a markdown file, draft, screenshot, commit
  message, or PR description. They live in `~/.config/specterx-kb/.env`
  only.
- Do not include `davidch@specterx.com` in committed screenshots either
  — redact per `tester/sensitive-terms.txt` (add the address to that
  list if it is not already covered).
- Mailinator inboxes are public — never send anything sensitive to one.
