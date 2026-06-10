---
title: Securely share a file from the SpecterX web platform
audience: end-user
estimated-reading-time: 5 min
last-validated: 2026-06-08
specterx-build: live production tenant at app.specterx.com
---

# Securely share a file from the SpecterX web platform

To send a file to someone outside SpecterX, click **Share files** in the sidebar, upload the file, add the recipients, pick a security policy, and click **Share**. SpecterX creates a protected link and sends each recipient a notification email; the policy you choose controls what they can do once they open it.

## Before you start

You need:

- An active SpecterX session in your browser. If you haven't signed in yet, see [Sign in to SpecterX](../01-log-in-to-specterx/01-log-in-to-specterx.html).
- The file you want to share. It can be one you've already uploaded to **My Files**, or one from your computer that you upload as part of this flow.
- The email address of each recipient.
- A phone number for each recipient, in international format, if you plan to use a policy that requires SMS verification. Your administrator decides which policies require this.

## Steps

### 1. Open the Share Files drawer

In the left sidebar, click **Share files**.

The **Share Files** drawer opens on the right side of the page. It has an upload area at the top labeled **Choose a file or drag it here**, and a **Share with** section to its right. A two-step progress indicator at the top of the drawer shows **1 Add items and Recipients** → **2 Select Policy**.

![](screenshots/01-drawer-empty.png)

### 2. Add the file

Click or drag a file onto the **Choose a file or drag it here** area (files up to 30 GB are accepted). The file appears under **Uploaded files** with a progress bar. Wait until the upload finishes before continuing.

To share a file you've already uploaded to **My Files**, close the drawer, click the ► icon on the file's row to reopen the drawer with that file pre-loaded, and skip to step 3.

![](screenshots/02-file-uploaded.png)

### 3. Add a recipient

In the **Share with** section, type the recipient's email address in the field — the placeholder reads **Insert email address and click `Enter`** — then press **Enter**. The address appears as a chip below the field.

After you add the first recipient, additional options appear below the recipient list:

- **Notify recipients** checkbox (checked by default) — keeps the notification email on.
- **Add message** text area — attach an optional personal note to the notification.
- **Encrypt message** toggle — encrypts the note in transit.

Repeat for every recipient you want to add.

![](screenshots/03-recipient-added.png)

### 4. Set each recipient's permission level

A role dropdown appears to the right of each recipient chip; it defaults to **Contributor**. Open the dropdown and pick the level you want:

- **Viewer**. Can view the file only.
- **Contributor**. Can view and edit the file's content. This is the default.
- **Co-owner**. Can view, edit, reshare the file with new recipients, and read the file's audit log.

A recipient can't override the policy: if the policy blocks downloads, no role unlocks a download button.

### 5. Continue to the policy step

Click **Next** at the bottom of the drawer. SpecterX shows a **Setting up secure sharing** screen while it checks auto-protection rules, recipient/file blocks, and your available policy choices. This normally takes a few seconds.

![](screenshots/04-policy-step.png)

### 6. Pick a security policy

When the **Choose Policy** screen loads, a policy is pre-selected in the dropdown. The selected policy's key permissions appear on the right side of the screen — for example, **Allow recipients to forward**, **Verify email**, or **File will remain tracked and protected in Cloud applications**. The line below the dropdown reads **Will be assigned to {N} file(s)**.

Open the dropdown to pick a different policy if the pre-selected one doesn't match the sensitivity of your file. Your administrator defines the available options; the dropdown shows only those allowed for your account.

If a Platform Governance Rule applies to this share, the policy is already chosen and locked. You can review it but you can't change it.

If no policy fits the share, ask your administrator to add one. Don't pick a permissive policy as a fallback.

![](screenshots/05-policy-dropdown-open.png)

### 7. Enter any extra recipient details the policy needs

Some policies require an additional piece of information per recipient before SpecterX will create the link:

- **Phone (SMS) verification.** An **Add phone number** action appears next to each recipient. Click it and enter the recipient's phone number in international format, for example `+1 555 000 1234`.
- **Personal secret.** An **Add password** action appears next to each recipient. Click it and enter the secret you've agreed with the recipient out of band.

If any required detail is missing, a banner stays at the top of the drawer and **Share** stays disabled.

Skip this step if the policy you picked doesn't ask for either.

### 8. Send the share

Click **Share** at the bottom of the drawer. SpecterX sends each recipient a notification email with the protected link, then displays a **Shared successfully** confirmation screen. The confirmation includes a summary table:

- **Shared with** — each recipient's address and role.
- **Copy link** — a link icon next to each recipient's row.
- **Shared items** — the file name and the policy assigned to it.

![](screenshots/08-link-copied.png)

### 9. Copy the protected link

To send the link through another channel (a chat message, a calendar invite), click the **Copy link** icon in the recipient's row on the confirmation screen. SpecterX copies the link to your clipboard. The link is the same one the recipient received by email, and it's already governed by the policy you chose.

When you're finished, click **Done** to close the confirmation and return to **My Files**.

## After you share: managing access

To check who has access to a file you've already shared, or to change something after the share is live, click the ► icon on the file's row in **My Files**. The **Share & Permissions** panel opens showing the current recipients under **Who has access**.

From the panel you can:

- Change a recipient's role from the dropdown next to their email address.
- Add a new recipient under **Add New Recipients**.
- Revoke a recipient's access using the **Revoke** action on their row.
- Change the policy from the **Parent policy** dropdown.

Changes take effect the next time the recipient opens the protected link. Anyone with the file already open in the Secure Viewer won't see the change until they reload.

> ⚠ Verification incomplete: the Share & Permissions panel contents were partially obscured in the test screenshots. The options listed above reflect the expected behavior — please confirm all controls are visible and functional during review.

![](screenshots/10-permissions-drawer.png)

<!-- coverage decision: include this section as a short pointer; full drawer flows are owned by article 07-update-permissions when approved. -->

## What recipients experience

Each recipient receives an email from an `@specterx.com` sender with a link to the protected file. When they click the link they land on the **Recipient Page** and verify their identity, usually by entering a 6-digit code sent to their inbox. After verification, the file opens in the **Secure Viewer**.

Whether they can download, forward, or print the file depends on the policy you picked in step 6, not on the role you gave them.

Recipients don't need a SpecterX account; SpecterX provisions them automatically when you add them to the share.

## Troubleshooting

### The Share button stays disabled

One of the required pieces is missing. Look at the top of the drawer for the message it shows:

- **Please add files to share**. The upload didn't finish, or no file was added.
- **Please add recipients to share**. At least one recipient must be added.
- **Recipient wasn't added. Please click on "Add" button**. You typed an address but didn't press Enter to commit it.
- **Some files are still uploading. Please wait until they finish uploading**. Wait for the upload bar to finish.
- A missing phone number or password banner. The selected policy needs that detail for every recipient.

### "Invalid email address" appears as you type a recipient

The address isn't in `name@example.com` form. Check for typos, then press Enter again.

### "You have already shared this file with {recipient}"

The address is already on the file's recipient list. Click the ► icon on the file's row to review or change that recipient's access instead.

### A recipient says they didn't get the notification email

Ask them to check their spam or junk folder. The notification comes from an `@specterx.com` sender and may be routed through a transactional-email provider. If it still doesn't arrive after a few minutes, click the ► icon on the file's row, confirm the recipient's email address is correct, and remove and re-add the recipient if it needs correcting.

### A recipient sees "Access denied" on the Recipient Page

The address on the protected link may not match the address the recipient used to verify. Click the ► icon on the file's row, check the address on file, and correct it if needed. If the address is right but they still can't open the file, the policy may require a verification method the recipient hasn't completed (for example, a phone number that hasn't been entered for them).

## Related articles

- [Sign in to SpecterX](../01-log-in-to-specterx/01-log-in-to-specterx.html)
- [What is SpecterX?](../03-what-is-specterx/03-what-is-specterx.html)
