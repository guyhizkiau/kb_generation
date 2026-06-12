# test-notes — 05-share-a-folder

Generated: 2026-06-12T14:14:28+00:00
Test attempt: 1
First failure: 00-dashboard

## Step 00-goto — ok

- backend: `browser`
- observation: title='SpecterX'; url=https://app.specterx.com/

## Step 00-email — ok

- backend: `browser`
- observation: title='Login - SpecterX'; url=https://app.specterx.com/signIn

## Step 00-password — ok

- backend: `browser`
- observation: title='Login - SpecterX'; url=https://app.specterx.com/signIn

## Step 00-signin — ok

- backend: `browser`
- observation: title='Login - SpecterX'; url=https://app.specterx.com/signIn

## Step 00-dashboard — FAIL

- backend: `browser`
- observation: timed out: Wait for My Files
- error: `Locator.wait_for: Timeout 15000ms exceeded.
Call log:
waiting for get_by_text("My Files").first to be visible
`
- > ⚠ couldn't verify this step.

## Step 01-share-files-closeup — FAIL

- backend: `browser`
- observation: timed out: Capture close-up of the Share files sidebar button before hovering
- error: `Locator.wait_for: Timeout 15000ms exceeded.
Call log:
waiting for get_by_role("button", name="Share files").first to be visible
`
- > ⚠ couldn't verify this step.

## Step 02-hover-share-files — FAIL

- backend: `browser`
- observation: timed out: Hover the Share files button to reveal the Share a folder / Share a file dropdown
- error: `Locator.hover: Timeout 15000ms exceeded.
Call log:
waiting for get_by_role("button", name="Share files").first
`
- > ⚠ couldn't verify this step.

## Step 03-wait-folder-option — FAIL

- backend: `browser`
- observation: timed out: Wait for the Share a folder option to appear in the dropdown
- error: `Locator.wait_for: Timeout 15000ms exceeded.
Call log:
waiting for get_by_role("button", name="Share a folder").first to be visible
`
- > ⚠ couldn't verify this step.

## Step 04-click-folder-option — FAIL

- backend: `browser`
- observation: timed out: Click Share a folder to open the Share Files drawer in folder mode
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
waiting for get_by_role("button", name="Share a folder").first
`
- > ⚠ couldn't verify this step.

## Step 05-upload-folder — skipped-cascade

- backend: `browser`
- observation: skipped — cascade abort after consecutive failures

## Step 06-wait-upload-complete — skipped-cascade

- backend: `browser`
- observation: skipped — cascade abort after consecutive failures

## Step 07-add-recipient — skipped-cascade

- backend: `browser`
- observation: skipped — cascade abort after consecutive failures

## Step 08-open-role-dropdown — skipped-cascade

- backend: `browser`
- observation: skipped — cascade abort after consecutive failures

## Step 09-select-contributor — skipped-cascade

- backend: `browser`
- observation: skipped — cascade abort after consecutive failures

## Step 10-next-button-closeup — skipped-cascade

- backend: `browser`
- observation: skipped — cascade abort after consecutive failures

## Step 11-click-next — skipped-cascade

- backend: `browser`
- observation: skipped — cascade abort after consecutive failures

## Step 12-wait-policy-loaded — skipped-cascade

- backend: `browser`
- observation: skipped — cascade abort after consecutive failures

## Step 13-policy-dropdown-closeup — skipped-cascade

- backend: `browser`
- observation: skipped — cascade abort after consecutive failures

## Step 14-open-policy-dropdown — skipped-cascade

- backend: `browser`
- observation: skipped — cascade abort after consecutive failures

## Step 15-select-default-policy — skipped-cascade

- backend: `browser`
- observation: skipped — cascade abort after consecutive failures

## Step 16-click-share — skipped-cascade

- backend: `browser`
- observation: skipped — cascade abort after consecutive failures

## Step 17-wait-success — skipped-cascade

- backend: `browser`
- observation: skipped — cascade abort after consecutive failures

## Step 18-copy-link — skipped-cascade

- backend: `browser`
- observation: skipped — cascade abort after consecutive failures

## Step 19-click-done — skipped-cascade

- backend: `browser`
- observation: skipped — cascade abort after consecutive failures

## Step 20-share-icon-closeup — skipped-cascade

- backend: `browser`
- observation: skipped — cascade abort after consecutive failures

## Step 21-click-share-icon — skipped-cascade

- backend: `browser`
- observation: skipped — cascade abort after consecutive failures

## Step 22-click-who-has-access — skipped-cascade

- backend: `browser`
- observation: skipped — cascade abort after consecutive failures

## Step C1-open-permissions — FAIL

- backend: `browser`
- observation: timed out: Open Who Has Access for the uploaded folder
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
waiting for locator("[data-testid=myFiles_WhoHasAccess]").first
`
- > ⚠ couldn't verify this step.

## Step C2-revoke-recipient — FAIL

- backend: `browser`
- observation: timed out: Revoke access for the test recipient
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
waiting for get_by_role("button", name="Remove").first
`
- > ⚠ couldn't verify this step.

## Step C3-delete-folder — FAIL

- backend: `browser`
- observation: timed out: Delete the uploaded test folder from My Files
- error: `Locator.click: Timeout 15000ms exceeded.
Call log:
waiting for get_by_role("button", name="Delete").first
`
- > ⚠ couldn't verify this step.
