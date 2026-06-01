---
title: What is SpecterX?
audience: everyone
estimated-reading-time: 3 min
last-validated: 2026-06-01
---

# What is SpecterX?

SpecterX is a platform for sharing files and emails with people outside your organization without losing control of what you send. You attach a security policy to the content. The policy stays with the file, so you decide who opens it, on what terms, and for how long, even after it leaves your inbox or your drive.

The product has two sides. If you work at an organization that uses SpecterX, you're a **sender**: you sign in, share files or protected email, and manage access afterwards. If you receive a SpecterX link from someone else, you're a **recipient**: you click the link, verify who you are, and view or download the file under whatever rules the sender set.

## The problem SpecterX solves

Once a file leaves your computer as an attachment or a public link, you've lost track of it. Recipients can forward, save, or post it. Your access logs end at "sent."

SpecterX replaces the attachment with a protected link that stays governed by a policy you control. You can revoke access at any time, and the policy expires the link on schedule.

## Core concepts

### Sender and recipient

A **sender** is a licensed SpecterX user at your organization. A **recipient** is anyone the sender shares with. Recipients don't need a SpecterX account; they're set up automatically when the share is made and verify themselves per share.

### Security policy

A **security policy** is a named set of rules that controls how a file can be accessed. Your administrators define policies in advance. When you share, you pick one from a dropdown. A policy can require verification, restrict whether recipients can forward the file, block downloads, watermark content, and set how many days the link stays active.

### Recipient experience

When a recipient clicks a SpecterX link, they land on a verification page. Verification is usually a 6-digit code sent to their email; depending on the policy, it can also be an SMS code or a personal secret the sender shares out of band. Once verified, the recipient opens the file in the **Secure Viewer**, an in-browser viewer that requires no install. Watermarks, downloads, and forwarding all follow the policy you picked at share time.

## What you can do with SpecterX

- **Share a file from the web.** Upload or select a file in the SpecterX web platform, pick a policy, add recipients, and click Share. See [Sign in to SpecterX](../01-log-in-to-specterx/01-log-in-to-specterx.html) for how to reach the web platform.
- **Send protected email from Outlook or Gmail.** The SpecterX Outlook Add-in and Gmail Extension add a panel to your compose window. From there you can apply a policy to attachments, the message body, or both, and set per-recipient permissions before sending.
- **Collaborate in a Workspace.** A Workspace is a persistent shared folder with a parent policy, named members, and an audit trail. Files added to a Workspace inherit its policy. Workspaces are available when your administrator has enabled them for your organization.

## What SpecterX is NOT

- **Not a storage product.** SpecterX protects files; it doesn't replace your storage. Workspaces can be backed by your existing Amazon S3, SharePoint, or Google Cloud Storage when an administrator configures it.
- **Not a file editor.** You view files in the Secure Viewer. You don't edit them inside SpecterX.
- **Not a signature platform**, except via the standalone **Digital Signature** capability for the specific case of signing a document.
- **Not a defense against a determined insider.** SpecterX prevents accidental forwarding, unauthorized access, and uncontrolled distribution. It doesn't stop someone who can already see a file from photographing the screen or transcribing it.

## How SpecterX fits with your existing tools

SpecterX sits between your existing identity, storage, and email systems and the people you share with. Your administrators connect it to your identity provider (Microsoft Entra ID, Google Workspace, or Okta) so signing in uses the credentials you already have. They can also connect storage (Amazon S3, SharePoint, or Google Cloud Storage), in which case Workspace files live in your own storage under SpecterX encryption. The Outlook and Gmail integrations protect outbound email from inside the mail clients you already use.

Recipients don't need any of this. Their access goes through the per-share verification step, with no account and no install required.

## Related articles

- [Sign in to SpecterX](../01-log-in-to-specterx/01-log-in-to-specterx.html)
- [Set or reset your password](../02-set-or-reset-password/02-set-or-reset-password.html)

---

*Last reviewed 2026-06-01.*
