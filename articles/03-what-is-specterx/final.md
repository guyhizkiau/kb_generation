---
title: What is SpecterX?
audience: everyone
estimated-reading-time: 4 min
last-validated: 2026-06-02
---

# What is SpecterX?

SpecterX is a data governance and secure collaboration platform. Your organisation uses it to share files, send email, and collaborate with people outside the company while keeping control of what happens next: who opens the content, on what terms, for how long, and whether to revoke access at any time. The protection is built into each file and travels with it across applications, devices, and storage systems, so the rules you set still apply long after the file leaves your inbox, your drive, or your repository.

## The problem SpecterX solves

Once a file leaves your computer as an attachment or a public link, you've lost track of it. Recipients can forward, save, or post it. Your access logs end at "sent."

SpecterX replaces the attachment with a protected link that stays governed by a policy you control. You can revoke access at any time, see who opened the file from where, and let the policy expire the link on schedule.

## What SpecterX protects

A single policy model applies wherever your organisation shares content:

- **Files shared from the web.** Upload or select a file in the SpecterX web platform, pick a policy, add recipients, and click Share. See [Sign in to SpecterX](../01-log-in-to-specterx/01-log-in-to-specterx.html) for how to reach the web platform.
- **Email and attachments.** The Outlook Add-in and Gmail Browser Extension add a SpecterX panel to your compose window. From there you apply a policy to attachments, the message body, or both, and set per-recipient permissions before sending. Server-side mail protection can apply policies automatically as messages leave your organisation, driven by your DLP signals.
- **Workspaces.** A Workspace is a persistent shared space with a parent policy, named members (Owner, Co-Owner, Contributor, Viewer), and a full audit trail. Use it to collaborate continuously with an external partner, request files from outside parties, or store ongoing project documents under policy. Files added to a Workspace inherit its policy. Workspaces are available when an administrator at the sending organisation has enabled them.
- **Files in cloud storage platforms.** Share-in-place connectors add SpecterX protection to files that *stay* in their original storage, such as Google Drive or SharePoint. No upload, no copy, no second source of truth.
- **Messages and files in workplace communication tools.** A chat connector for platforms such as Slack lets users send protected content into channels and direct messages under a SpecterX policy, so chat-borne data carries the same governance as anything you'd share by link or email.
- **Data exported from CRM platforms.** A browser extension and a reports connector wrap report exports from CRMs such as Salesforce in a SpecterX policy, so a CSV pulled from the CRM becomes a governed share instead of a loose download.

Every protected interaction produces an audit trail. From the same interface that sent the file, you can revoke access, change recipient permissions, or expire the link instantly.

## Core concepts

### Sender and recipient

A **sender** is a licensed SpecterX user at your organisation. A **recipient** is anyone the sender shares with. Recipients don't need a SpecterX account; they're set up automatically when the share is made and verify themselves per share. Inside a Workspace, the same relationship becomes a named role (Owner, Co-Owner, Contributor, or Viewer) that persists for as long as the Workspace does.

### Security policy

A **security policy** is a named set of rules that controls how a file can be accessed. Administrators define policies in advance, and the sender picks one from a dropdown at share time. A policy can require verification, restrict whether recipients can forward the file, block downloads, watermark content, encrypt files with a password or Rights Management, and set how many days the link stays active.

### Recipient experience

When a recipient clicks a SpecterX link, they land on a verification page. Verification is usually a 6-digit code sent to their email; depending on the policy, it can also be an SMS code or a personal secret the sender shares out of band. Once verified, the recipient opens the file in the **Secure Viewer**, an in-browser viewer that requires no install. Watermarks, downloads, and forwarding all follow the policy the sender picked at share time.

## How SpecterX fits with existing tools

SpecterX sits between an organisation's identity, storage, email, and security systems and the people it shares files with.

- **Identity.** SpecterX connects to the organisation's identity provider, such as Microsoft Entra ID, Google Workspace, or Okta, so senders sign in with credentials they already have. SAML 2.0, OAuth, and LDAP are all supported. Recipients don't need any of this; they verify per share.
- **Storage.** Workspaces can be backed by Amazon S3, SharePoint, or Google Cloud Storage, in which case files live in the organisation's own storage under SpecterX encryption. SpecterX provides its own managed storage as the default.
- **Mail.** The Outlook and Gmail integrations protect outbound email from inside the mail clients senders already use. A separate Mail Protection Server can apply policies at the gateway, automatically and at scale, optionally driven by DLP classification signals.
- **Data classification and DLP.** SpecterX plugs into the security stack the organisation already runs. Policies can trigger a DLP or threat-detection scan when a recipient accesses a file, and policy assignment can be driven by classification signals — Microsoft Purview sensitivity labels, custom DLP headers from Exchange Online, or third-party classifiers — so the right protection is applied automatically as files move.
- **Deployment.** SpecterX runs in SpecterX's cloud by default, with an On-Prem Gateway option for organisations that need to keep the deployment in their own environment.

## What SpecterX is NOT

- **Not a storage product.** SpecterX is the protection and access-control layer for files; the files themselves can live in SpecterX-managed storage or in your existing Amazon S3, SharePoint, or Google Cloud Storage when an administrator configures it. SpecterX adds governance to the storage you already have.
- **Not a defence against a determined insider.** SpecterX prevents accidental forwarding, unauthorised access, and uncontrolled distribution from the SpecterX surface. It doesn't stop someone who can already see a file from photographing the screen or transcribing it. Watermarks deter that; they don't block it.

## Related articles

- [Sign in to SpecterX](../01-log-in-to-specterx/01-log-in-to-specterx.html)
- [Set or reset your password](../02-set-or-reset-password/02-set-or-reset-password.html)

---

*Last reviewed 2026-06-02.*
