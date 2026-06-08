---
title: Securely share a file from the SpecterX web platform
audience: end-user
estimated-reading-time: 5 min
---

# Securely share a file from the SpecterX web platform

When you share a file from SpecterX, the platform creates a protected link and sends a notification email to each recipient. The security policy you choose controls what recipients can do with the file.

## Before you start

You need:

- A SpecterX account and an active session. See [Sign in to SpecterX](../01-log-in-to-specterx/01-log-in-to-specterx.html) if you aren't yet signed in.
- The file you want to share.
- The email address of each recipient.
- If the security policy you intend to use requires phone (SMS) verification: each recipient's phone number in international format.

## Steps

### 1. Open the Share files dialog

On the **My Files** page, click **Share files**.

### 2. Upload your file

Drag your file into the upload area, or click the area to open a file picker and select the file. Wait for the upload progress indicator to finish before continuing.

### 3. Add a recipient

In the **Add recipients** field, type the recipient's email address and press **Enter** or click **Add**.

### 4. Set the recipient's permission level

Next to the recipient's email address, open the permission dropdown and choose one of the three levels:

- **Viewer**: can open and read the file. They can't upload files or change permissions.
- **Contributor**: can open, read, and upload files. Download access depends on the policy.
- **Co-Owner**: full access. They can view, upload, download, manage permissions, and reshare.

Repeat steps 3 and 4 for each additional recipient.

### 5. Select a security policy

Open the policy dropdown and select the policy that matches the sensitivity of your file. Your administrator defines the available policies.

If no suitable policy exists, contact your administrator and ask them to create one.

### 6. Enter phone numbers (phone-verification policies only)

If the selected policy requires phone (SMS) verification, a phone number field appears next to each recipient. Enter the recipient's phone number in international format, for example `+1 555 000 1234`.

The **Share** button stays inactive until every recipient with a required phone-number field has a number entered.

Skip this step if no phone number fields appear.

### 7. Complete the share

Click **Share**. SpecterX creates the protected link and sends a notification email to each recipient.

### 8. Copy the protected link

After the share is created, SpecterX shows a confirmation. Click **Copy link** to copy the protected link to your clipboard.

You can paste the link and send it directly if needed, though recipients have already received the notification email.

## After you share: the Share & Permissions Drawer

To review or change access for a file you've already shared:

1. In **My Files**, click the share icon next to the file's name.

2. The Share & Permissions Drawer opens on the right side of the page. It lists every recipient, their current permission level, and a **Parent policy** dropdown showing the policy applied to the file.

From the drawer you can:

- Change a recipient's permission level using the dropdown next to their name.
- Add a new recipient by typing their email address in the **Add recipient** field at the top of the drawer.
- Remove a recipient by clicking the remove control next to their row.
- Change the policy governing the file using the **Parent policy** dropdown.

All changes take effect immediately for anyone who opens the link from that point on.

## What recipients experience

Each recipient receives an email with a link to the protected file. When they click the link they land on the SpecterX Recipient Page and are prompted to verify their identity, usually by entering a 6-digit code sent to their inbox. After verification, the file opens in the SpecterX Viewer. The policy you selected at share time determines what the recipient can do in the Viewer: download, forward, or print the file.

## Troubleshooting

### The recipient didn't receive the notification email

Ask the recipient to check their spam or junk folder. The notification comes from an `@specterx.com` sender and may be routed through a transactional-email provider. If it still doesn't arrive after a few minutes, open the Share & Permissions Drawer and confirm the recipient's email address is correct. Remove and re-add the recipient if the address needs correcting.

### The phone number field isn't accepting the number

Enter the number in international format starting with the country code, for example `+44 7700 900000`. Remove spaces, hyphens, or parentheses if the field rejects the format.

### The Share button is grayed out or inactive

All required fields must be filled before the share can proceed. If the selected policy requires phone verification, enter a phone number for every recipient. Also confirm that at least one recipient has been added and that a policy is selected.

### A recipient sees "Access denied"

The email address on the protected link may not match the address the recipient used. Open the Share & Permissions Drawer, verify the address on file, and correct it if needed. If the address is correct, the recipient's access may have been revoked. See [Revoke access to a shared file](#).

## What's next

- [Share a folder](#): apply a single policy to all files in a folder at once
- [Set recipient permissions](#): understand in detail what each permission level allows
- [Update permissions after sharing](#): add, change, or remove recipients after the share is live
- [Revoke access to a shared file](#): disable a protected link for one recipient or for everyone
