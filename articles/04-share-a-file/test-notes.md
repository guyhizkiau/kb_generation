# test-notes — 04-share-a-file

Generated: 2026-06-09T12:32:16+00:00

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

## Step 00-dashboard — ok

- backend: `browser`
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files; verify('My Files page is visible')=not-visible
- screenshot: `screenshots/00-dashboard.png`

## Step 01-open-drawer — ok

- backend: `browser`
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files; verify('The Share Files drawer is open')=not-visible
- screenshot: `screenshots/01-drawer-empty.png`

## Step 02-upload-file — ok

- backend: `browser`
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files; verify('test-document.pdf appears in the drawer')=not-visible
- screenshot: `screenshots/02-file-uploaded.png`

## Step 03-add-recipient — ok

- backend: `browser`
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files; verify('Recipient row is visible with the test email')=not-visible
- screenshot: `screenshots/03-recipient-added.png`

## Step 04-next-policy — ok

- backend: `browser`
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files

## Step 04a-wait-policy-loaded — ok

- backend: `browser`
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files; verify('Share button is visible — rules have finished applying')=not-visible
- screenshot: `screenshots/04-policy-step.png`

## Step 05-open-policy-dropdown — ok

- backend: `browser`
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files; verify('Policy dropdown is open with options visible')=not-visible
- screenshot: `screenshots/05-policy-dropdown-open.png`

## Step 06-select-default-policy — ok

- backend: `browser`
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files; verify('Policy is selected and Share button is still visible')=not-visible
- screenshot: `screenshots/06-policy-selected.png`

## Step 07-click-share — ok

- backend: `browser`
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files

## Step 07a-wait-sharing-success — ok

- backend: `browser`
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files; verify('Shared successfully screen is visible — loading is complete')=not-visible
- screenshot: `screenshots/07-sharing-success.png`

## Step 08-copy-link — ok

- backend: `browser`
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files; verify('Copy link action is triggered')=not-visible
- screenshot: `screenshots/08-link-copied.png`

## Step 09-close-drawer — ok

- backend: `browser`
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files; verify('My Files is visible with test-document.pdf in the list')=not-visible
- screenshot: `screenshots/09-my-files-after-share.png`

## Step 09a-share-icon-close-up — ok

- backend: `browser`
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files; verify('Share icon is visible on the file row')=not-visible
- screenshot: `screenshots/09-share-icon.png`

## Step 10-open-share-permissions-drawer — ok

- backend: `browser`
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files; verify('Share & Permissions Drawer shows Who has access')=not-visible
- screenshot: `screenshots/10-permissions-drawer.png`
