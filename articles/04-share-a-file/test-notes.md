# test-notes — 04-share-a-file

Generated: 2026-06-08T13:23:28+00:00

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
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files; verify('My Files page is visible with the Share files button')=not-visible
- screenshot: `screenshots/00-dashboard.png`

## Step 01-open-drawer — ok

- backend: `browser`
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files; verify('The Share Files drawer is open with the empty upload area visible')=not-visible
- screenshot: `screenshots/01-drawer-empty.png`

## Step 02-upload-file — ok

- backend: `browser`
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files; verify('test-document.pdf appears as uploaded in the drawer')=not-visible
- screenshot: `screenshots/02-file-uploaded.png`

## Step 03-add-recipient — ok

- backend: `browser`
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files; verify('A recipient row appears in the Share with block with the test recipient email')=not-visible
- screenshot: `screenshots/03-recipient-added.png`

## Step 04-next-policy — ok

- backend: `browser`
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files; verify('The Select Policy step heading is visible')=not-visible
- screenshot: `screenshots/04-policy-step.png`

## Step 07-click-share — ok

- backend: `browser`
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files; verify('The Confirm step is visible with a Sharing Successful or shared-successfully message')=not-visible
- screenshot: `screenshots/07-sharing-success.png`

## Step 08-copy-link — ok

- backend: `browser`
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files; verify('The Copy Link button shows a copied state or remains visible')=not-visible
- screenshot: `screenshots/08-link-copied.png`

## Step 09-close-drawer — ok

- backend: `browser`
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files; verify('My Files shows the test-document.pdf row with a share indicator')=not-visible
- screenshot: `screenshots/09-my-files-after-share.png`

## Step 10-open-share-permissions-drawer — ok

- backend: `browser`
- observation: title='My Files - SpecterX'; url=https://app.specterx.com/my-files; verify('The Share & Permissions Drawer shows Who has access and lists the recipient')=not-visible
- screenshot: `screenshots/10-permissions-drawer.png`
