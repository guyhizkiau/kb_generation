# Scenario — cluster 02-share-files

This is the test-world setup for the seven share-files articles in this
cluster. The cluster runs against the production tenant at
`app.specterx.com`.

## Articles in this cluster

1. `04-share-a-file` — Securely share a file from the SpecterX web platform
2. `05-share-a-folder` — Share a folder
3. `06-set-recipient-permissions` — Set recipient permissions
4. `07-update-permissions` — Update permissions after sharing
5. `08-revoke-access` — Revoke access to a shared file
6. `09-set-file-expiry` — Set how long a file stays accessible
7. `10-request-a-digital-signature` — Request a digital signature

## Target environment

- Hostname: `app.specterx.com`
- Account: `guy@specterx.com` (credentials in `~/.config/specterx-kb/.env`
  as `SPECTERX_USERNAME` and `SPECTERX_PASSWORD`)
- Test recipient: `TEST_RECIPIENT_EMAIL` (from `~/.config/specterx-kb/.env`);
  the pipeline can read the recipient's Gmail inbox for verification codes
  using `TEST_RECIPIENT_GMAIL_PASSWORD`

## Baseline state before each article's test

Start from a **logged-in** browser session as `guy@specterx.com`, on the
My Files page (`/my-files`). The tester should have a small test file
available to upload (e.g. a sample PDF from `tester/fixtures/`).

- For articles that require a pre-existing share (07, 08, 09), the tester
  runs article 04 first to create the share, or uses an existing shared
  file from a prior test run.
- After each test: delete any test files uploaded during the run to keep
  the account clean. Do not delete files shared with the test recipient
  before confirming the article's screenshots are captured.

## Article-specific constraints

### 04-share-a-file

- Upload a fresh test file during the test; do not reuse a file that is
  already shared.
- Recipient: use `TEST_RECIPIENT_EMAIL`.
- Capture screenshots of: (1) the Share dialog open on the file, (2) the
  policy selector, (3) the post-share confirmation.
- Do not surface real recipient email addresses in screenshots — redact
  per `tester/sensitive-terms.txt`.

### 05-share-a-folder

- Create a temporary test folder and upload at least one file to it before
  testing the share flow.
- Clean up the folder after screenshots are captured.

### 06-set-recipient-permissions

- Demonstrate all three permission levels (Viewer, Contributor, Co-Owner)
  in screenshots or step descriptions.
- Can reuse a file from article 04's share if still present.

### 07-update-permissions

- Requires a pre-existing share to modify. Use the file from article 04,
  or share a fresh file first.
- Show: changing a permission level, adding a second recipient, removing a
  recipient.

### 08-revoke-access

- Use a dedicated test share created just for this article so that
  revocation does not break other articles' test state.
- Capture the Recipient Page "access denied" state after revocation.

### 09-set-file-expiry

- Policy-level expiry is configured in the policy editor, not at share
  time. If no expiry-enabled policy exists on the test tenant, note it
  in the test output and describe from product documentation.
- Do not change production policies without Guy's consent — if required,
  ask before running.

### 10-request-a-digital-signature

- Only run if the Digital Signature feature is available on the test
  tenant. If not available or gated behind a plan upgrade, mark the test
  as `validation: skipped` and describe from product documentation.
