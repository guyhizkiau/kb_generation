# test-notes — 04-share-a-file

Generated: 2026-06-07T14:13:21+00:00

## Step 01 — FAIL

- backend: `browser`
- observation: timed out: On the My Files page, click the Share files button to open the Share files dialog
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_text("the Share files button in the top area of the My Files page").first
`
- > ⚠ couldn't verify this step.

## Step 02 — FAIL

- backend: `browser`
- observation: error: Upload test-document.pdf using the file picker inside the Share files dialog and wait for the upload to complete
- error: `ValueError("unknown action type: 'file_upload'")`
- > ⚠ couldn't verify this step.

## Step 03 — FAIL

- backend: `browser`
- observation: error: In the Add recipients field, type a recipient email address and confirm it by pressing Enter or clicking Add
- error: `ValueError("unknown action type: 'type'")`
- > ⚠ couldn't verify this step.

## Step 04 — FAIL

- backend: `browser`
- observation: error: Open the permission level dropdown next to testrecipient@example.com and select Viewer
- error: `ValueError("unknown action type: 'select'")`
- > ⚠ couldn't verify this step.

## Step 05 — FAIL

- backend: `browser`
- observation: error: Open the policy dropdown in the Share files dialog and select any available security policy
- error: `ValueError("unknown action type: 'select'")`
- > ⚠ couldn't verify this step.

## Step 06 — FAIL

- backend: `browser`
- observation: error: If the selected policy requires phone verification, a phone number field appears next to the recipient — enter a phone number in international format; skip this step if no phone number field appears
- error: `ValueError("unknown action type: 'type'")`
- > ⚠ couldn't verify this step.

## Step 07 — FAIL

- backend: `browser`
- observation: timed out: Click the Share button to create the protected link and send the notification email to the recipient
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_text("the Share (or Confirm) primary action button at the bottom o").first
`
- > ⚠ couldn't verify this step.

## Step 08 — FAIL

- backend: `browser`
- observation: timed out: On the share confirmation screen, click the Copy link button to copy the protected link to the clipboard
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_text("the Copy link button on the share confirmation screen — the").first
`
- > ⚠ couldn't verify this step.

## Step 09 — FAIL

- backend: `browser`
- observation: error: Close or dismiss the Share files dialog and return to the My Files page; confirm test-document.pdf appears in the file list with a share icon visible next to its name
- error: `ValueError("unknown action type: 'navigate'")`
- > ⚠ couldn't verify this step.

## Step 10 — FAIL

- backend: `browser`
- observation: timed out: Click the share icon next to test-document.pdf in the My Files list to open the Share & Permissions Drawer
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
  - waiting for get_by_text("the share icon (sharing indicator) immediately next to test-").first
`
- > ⚠ couldn't verify this step.
