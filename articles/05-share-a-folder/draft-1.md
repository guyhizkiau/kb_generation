---
title: Share a folder
audience: end-user
estimated-reading-time: 5 min
---

# Share a folder

When you share a folder in SpecterX, every file inside inherits the folder's security policy — including files you add after the share is live. Open the **Share Files** drawer on the **My Files** page, switch it to folder mode, and complete the same policy-and-recipient flow you'd use for a single file.

## Before you start

You need:

- An active SpecterX session. If you haven't signed in yet, see [Sign in to SpecterX](../01-log-in-to-specterx/01-log-in-to-specterx.html).
- A folder to share. It can be an existing folder in **My Files** or a new one you upload from your computer.
- The email address of each recipient.
- A phone number for each recipient, in international format, if you plan to use a policy that requires SMS verification. Your administrator decides which policies require this.

## Steps

### 1. Open the Share Files drawer

On the **My Files** page, click **Share files**.

> Screenshot (close-up): the Share files button in the My Files page header

The **Share Files** drawer opens on the right side of the page with the **Add items and Recipients** step already showing.

> Screenshot (result): the Share Files drawer open in its default state

### 2. Switch to folder mode

At the top of the upload area, click the mode selector `<unknown label — verify in test>` to open the dropdown.

> Screenshot (close-up): the mode selector dropdown in the upload area, showing "Share a folder" and "Share a file" options

Click **Share a folder**.

> Screenshot (result): the upload area in folder mode with the dragger label reading "Choose a folder or drag it here"

### 3. Upload your folder

Drag your folder onto the dragger, or click **Upload a folder** to browse and select it from your computer. The folder and its contents upload. Wait for the upload to finish before continuing.

> Screenshot (result): the folder listed in the upload area with an upload progress indicator

If your folder is already in **My Files**, you don't need to start at step 1. Go to **My Files**, find the folder row, and click **Share** from the folder's context menu. The drawer opens with that folder pre-loaded. Continue from step 4.

### 4. Add recipients

In the **Share with** block, the recipient field shows the placeholder **Insert email address and click `Enter`**.

Type a recipient's email address and press **Enter**. The address moves into a recipient row below the field.

Repeat for every recipient you want to add.

> Screenshot (result): one or more recipients listed in the Share with block

Below the recipient list, the **Notify recipients** checkbox controls whether SpecterX sends each recipient a notification email when you click **Share**. The checkbox is selected by default. Clear it only if you plan to send the protected link yourself.

### 5. Set each recipient's role

Each recipient row has a role dropdown set to **Viewer** by default.

> Screenshot (close-up): the role dropdown on a recipient row, showing the Viewer, Contributor, and Co-owner options

Open the dropdown and select the role you want:

- **Viewer** — can view the folder's contents.
- **Contributor** — can view and edit content.
- **Co-owner** — can add, edit, and share content, and read the folder's audit logs.

> Screenshot (result): a recipient row with a role selected other than Viewer

A role doesn't override the policy: if the policy blocks downloads, even a Co-owner can't download files.

### 6. Continue to the policy step

Click **Next** at the bottom of the drawer.

> Screenshot (close-up): the Next button at the bottom of the drawer

SpecterX checks your organization's auto-protection rules and shows **Setting up secure sharing** briefly. When the check finishes, the **Select Policy** step appears.

> Screenshot (result): the Select Policy step in the Share Files drawer

### 7. Pick a security policy

From the **Choose Policy** dropdown, select the policy that fits the sensitivity of the folder. Your administrator defines the available policies.

> Screenshot (close-up): the Choose Policy dropdown open with available policies listed

If a Platform Governance Rule applies to this share, the policy is already chosen and the heading reads **Choose or Review Policy** instead. You can review the assigned policy but you can't change it.

### 8. Enter any extra recipient details the policy needs

Some policies require an additional piece of information per recipient:

- **Phone (SMS) verification** — an **Add phone number** action appears next to each recipient. Click it and enter the number in international format, for example `+1 555 000 1234`.
- **Personal secret** — an **Add password** action appears next to each recipient. Click it and enter the secret you've agreed with the recipient out of band.

Skip this step if the policy you picked doesn't require either.

### 9. Send the share

Click **Share**. The drawer moves to the **Confirm** step and shows **Shared successfully** along with a summary listing the folder, recipients, roles, and the policy applied.

> Screenshot (result): the Confirm step showing "Shared successfully" with the share summary table

If you left **Notify recipients** checked in step 4, each recipient receives a notification email with a link to the shared folder.

### 10. Copy the protected link

To send the link through a different channel, click **Copy link** on the **Confirm** step. SpecterX copies the link to your clipboard.

## Policy inheritance

The policy you pick in step 7 becomes the folder's **Parent policy**. Every file already inside the folder is governed by this policy. When you upload a new file to the folder later, SpecterX shows the banner **Users who have access to this folder will have access to the files you add** — the new file inherits the parent policy automatically.

You can see the parent policy in the folder's info drawer: go to **My Files**, open the folder's context menu, and click **View info**.

> Screenshot: the folder info drawer with the Parent policy field visible

If a specific file inside the folder needs a different policy, open that file's permissions drawer and change its policy directly. A file-level policy overrides the parent for that file only.

## After you share: the Permissions & Policy drawer

To check who has access or change something after the share is live, open the **Permissions & Policy** drawer.

1. In **My Files**, find the folder row. Look for the share icon at the right edge of the row.

> Screenshot (close-up): the share icon on the folder row in My Files

2. Click the share icon. The **Permissions & Policy** drawer opens.

> Screenshot (result): the Permissions & Policy drawer open

3. Click **Who has access** to see all current recipients.

> Screenshot (result): the Who has access view listing recipients with role dropdowns and Revoke actions

From this view you can:

- Change a recipient's role from the dropdown next to their email address.
- Add a new recipient using the **Add new recipient via email** field.
- Revoke a recipient's access by clicking **Revoke** on their row. A **Revocation Warning** modal asks you to confirm before access is removed.
- Change the folder's policy from the **Parent policy** dropdown.

Changes take effect the next time the recipient opens the folder link.

## What recipients experience

Each recipient receives an email from an `@specterx.com` sender with a link to the shared folder. When they click the link, they land on the **Recipient Page**, verify their identity, and then see an **Open folder** button. After clicking it, the folder's contents open in the Secure Viewer.

What recipients can do with files inside the folder depends on the policy you applied, not on their role.

Recipients don't need a SpecterX account. SpecterX provisions them automatically when you add them to the share.

## Troubleshooting

### The Share button stays disabled

One or more required pieces is missing. Check the banner at the top of the drawer:

- **Please add files to share** — the folder upload didn't finish, or nothing was added.
- **Please add recipients to share** — at least one recipient must be added.
- **Recipient wasn't added. Please click on "Add" button** — you typed an address but didn't press Enter to commit it.
- **Some files are still uploading. Please wait until they finish uploading** — wait for the upload to complete.
- A missing phone number or password banner — the selected policy requires that detail for every recipient.

### "You do not have permissions to share this file" appears

Your account doesn't have permission to share this folder. Contact your administrator.

### "We had an issue changing the permissions settings." appears

There was a problem saving a permission change in the **Permissions & Policy** drawer. Try again. If the error persists, reload the page and re-open the drawer.

### A recipient says they didn't get the notification email

Ask them to check their spam or junk folder. If it still doesn't arrive after a few minutes, open the **Permissions & Policy** drawer, confirm the recipient's email address is correct, and remove and re-add them with the right address if needed.

## Related articles

- [Securely share a file from the SpecterX web platform](../04-share-a-file/04-share-a-file.html)
- [Sign in to SpecterX](../01-log-in-to-specterx/01-log-in-to-specterx.html)
