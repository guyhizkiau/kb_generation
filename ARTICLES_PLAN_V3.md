# SpecterX Knowledge Base — Article Plan V3

**112 articles across 11 sections** · all planned (📋)

This document is the editorial plan for the SpecterX help center. Each article entry lists the title, audience, and the specific topics, questions, and tasks the article will cover. All articles are planned (📋); none are live yet. A "Deferred until shipped" watch-list at the end tracks features not yet in production.

---

## Section 1 — Get started

Audience: all users. Purpose: orient first-time users to the product and point them to the right section.

---

### 📋 What is SpecterX?

**Audience:** Everyone (new users, decision makers, recipients who just received a link)

**Topics to cover:**
- What problem SpecterX solves: protecting files and emails so the sender keeps control after sharing
- The two core actors: the **sender** (who shares) and the **recipient** (who receives a protected link)
- The three main use cases: (1) share a protected file from the web, (2) protect email and attachments from Outlook or Gmail, (3) collaborate securely in a Workspace
- What a "security policy" is: the controls that govern how a file can be accessed (verification, forwarding, download, expiry)
- What the recipient experiences: the Recipient Page, the SpecterX Viewer, verification steps
- What SpecterX does NOT do: it is not a storage product; it does not move your files; it is not a signature platform (except via the Digital Signature feature)
- How SpecterX relates to your identity provider, storage, and email infrastructure

---

### 📋 Log in to the SpecterX web platform

**Audience:** All users

**Topics to cover:**
- URL format for your organisation's SpecterX instance (e.g. `yourorg.specterx.com` or `staging-app.specterx.com`)
- SSO login via Entra ID / Okta / Google Cloud Identity — what the user sees, what they click
- Email/password login (for organisations not using SSO)
- What to do if your account is not yet provisioned
- Where to find your organisation's login URL (from your IT admin)
- What to do if SSO fails ("access denied", "not authorised" errors)

---

### 📋 Set or reset your password

**Audience:** All users (first-time sign-in and existing users)

**Topics to cover:**
- Creating a password for the first time (initial account setup for non-SSO users): the activation email, the "Create your password" link, password requirements
- How to trigger a password reset from the login page if you forget your password
- What the reset email looks like and where it comes from
- Link expiry: how long the activation or reset link is valid
- What to do if you use SSO (password reset is managed by your identity provider, not SpecterX)
- What to do if you do not receive the activation or reset email (spam, provisioning issues)
- Contacting your system administrator if self-service reset is disabled

---

## Section 2 — Share files

Audience: end users who want to share a file or folder from the SpecterX web platform.

---

### 📋 Securely share a file from the SpecterX Web Platform

**Topics to cover:**
- The Share files flow: upload → Add recipients → Select Policy → Share
- Recipient permission levels: Viewer, Contributor, Co-Owner
- Selecting a security policy from the dropdown
- Policies that require phone verification: entering the recipient's number
- Completing the share and sending the notification email
- Copying the protected link after sharing
- The Share & Permissions Drawer: who has access, the Parent policy setting
- Updating permissions and revoking access after sharing
- Recipient experience summary

---

### 📋 Share a folder

**Audience:** End users

**Topics to cover:**
- How sharing a folder differs from sharing a file: all files inside inherit the folder's policy
- The Share a folder flow from the Share files menu
- The parent policy and policy inheritance: new files uploaded to a shared folder automatically get the folder's policy
- Setting per-file policies that override the parent
- Recipient experience: what a recipient sees when they receive a shared folder link
- Folder permissions vs file permissions: can a recipient with Viewer access on the folder download individual files?
- What happens when you add a new file to an already-shared folder

---

### 📋 Set recipient permissions

**Audience:** End users

**Topics to cover:**
- The three permission levels and what each allows:
  - **Viewer**: read-only, cannot upload, cannot change policy
  - **Contributor**: can view, upload, and download (subject to policy)
  - **Co-Owner**: full access, including managing permissions and sub-shares
- How to set permission level at share time (the Contributor dropdown in the Share dialog)
- How permission level interacts with the active policy (e.g. a Contributor cannot download if the policy blocks download)
- Setting different permission levels for different recipients (multiple share steps)
- The relationship between permissions and the Share & Permissions Drawer

---

### 📋 Update permissions after sharing

**Audience:** End users

**Topics to cover:**
- How to open the Share & Permissions Drawer for a file (share icon in My Files)
- Changing a recipient's permission level from the drawer
- Adding a new recipient to an already-shared file
- Removing a recipient (the protected link stays active for remaining recipients)
- Changing the policy (Parent policy dropdown) after a file has been shared
- Whether changes take effect immediately for recipients who already have the link open

---

### 📋 Revoke access to a shared file

**Audience:** End users, admins

**Topics to cover:**
- The difference between removing a recipient and revoking all access
- How to fully disable a protected link so no one can access it
- What happens to recipients who attempt to open the link after revocation
- The audit log entry created when access is revoked
- Revoking access vs deleting the file
- Re-enabling access after revoking (is this possible?)

---

### 📋 Set how long a file stays accessible

**Audience:** End users, admins

**Topics to cover:**
- Where expiration is configured: in the security policy (Retention setting — expressed as a number of days after which the link automatically expires), not as a specific calendar date
- How automatic expiry works: the link stops working after the configured number of days
- What the recipient sees after the link has expired
- The difference between expiry and revocation
- Whether expiry applies to already-downloaded copies
- How data retention policies (e.g. "1 day retention") govern auto-expiry

---

### 📋 Request a digital signature

**Audience:** End users

**Topics to cover:**
- What the Digital Signature feature does in SpecterX (requesting signatures from recipients on a protected file)
- Initiating a signature request: selecting the file, adding signers, defining signature fields
- The signer experience: what the recipient sees and how they sign
- After signing: where the signed document is stored, how the sender gets notified
- Supported file types for digital signatures
- Link to digital signature limitations article in §11

---

## Section 3 — Receive files

Audience: recipients — external parties who have received a protected link and need to open the file.

---

### 📋 Tour the SpecterX Recipient Page

**Audience:** Recipients

**Topics to cover:**
- What the Recipient Page is: the landing page a recipient sees after clicking a protected SpecterX link
- Page layout overview: identity selection area, verification step, file preview summary, action buttons
- The identity confirmation step: selecting your email address when multiple aliases are detected
- The verification area: which method appears (email OTP, SMS/phone OTP, personal secret) and why it varies by share policy
- What "access denied" looks like on the Recipient Page and what to do (contact the sender)
- Post-verification state: the file becomes accessible in the SpecterX Viewer
- The "Send a file back" upload option (if enabled by the sender)
- Accessibility: keyboard navigation and screen-reader behaviour on the Recipient Page
- Link to troubleshooting if verification fails

**Related articles:** Open a SpecterX-protected file · Verify with an SMS code · Verify with a personal secret · What the SpecterX Viewer lets you do

---

### 📋 Open a SpecterX-protected file

**Audience:** Recipients (external, may not know SpecterX)

**Topics to cover:**
- What a SpecterX-protected email looks like (the notification email from the sender)
- How to click the protected link and what page you land on (the Recipient Page)
- Selecting your email address when prompted (aliases and group addresses)
- The default verification flow: **email OTP** — checking your inbox for the code, entering it on the Recipient Page
- The SpecterX Viewer: what it is, what you can do in it (view, zoom, download if permitted, forward if permitted, open in another app)
- What to do if the link says "access denied" (contact the sender)
- What to do if you do not receive the verification email (link to troubleshooting)
- Note about same-browser / same-device requirement for the verification link
- Brief intro to alternative verification methods with links to SMS and personal secret articles

**Related articles:** Tour the SpecterX Recipient Page · Verify with an SMS code · Verify with a personal secret · Download a protected file

---

### 📋 Verify with an SMS code

**Audience:** Recipients

**Topics to cover:**
- When SMS verification is required: the sender's policy mandates phone verification
- Entering the last four digits of your phone number to retrieve the SMS code
- Entering the OTP code from the SMS to access the file
- What to do if the SMS does not arrive (retry, check country support)
- What to do if your phone number is incorrect in the system (contact the sender)
- Countries and carriers where SMS delivery may be delayed or unavailable

**Related articles:** Tour the SpecterX Recipient Page · Open a SpecterX-protected file

---

### 📋 Verify with a personal secret

**Audience:** Recipients

**Topics to cover:**
- What a "personal secret" is: a password or passphrase the sender set during the share
- Entering the personal secret on the Recipient Page
- What to do if the secret is wrong: contact the sender for the correct value
- The difference between a personal secret and the "encrypt downloaded files with a password" feature (the personal secret is for access; the download password is for the downloaded copy)

**Related articles:** Tour the SpecterX Recipient Page · Open a SpecterX-protected file

---

### 📋 Download a protected file

**Audience:** Recipients

**Topics to cover:**
- When download is available: the Download button only appears in the SpecterX Viewer if the sender's policy permits it; if the button is absent, the file cannot be downloaded
- Clicking the Download button and what happens (browser download prompt or password prompt)
- Password-protected downloads: if the policy requires a download password, the recipient is prompted to enter it before the file is saved; the downloaded file is encrypted and requires the password to open in a local application
- RMS-protected downloads: if RMS is enabled, the downloaded file remains encrypted; the recipient must have the Microsoft RMS client (auto-installed with Office 365) and a Microsoft or Google account to open it
- File format: the downloaded file is in its original format (PDF, DOCX, etc.) — it is not wrapped in a container format
- What to do if the download button is not visible: the sender's policy may block downloads; contact the sender to ask them to adjust the policy or reshare with a download-permitted policy
- Limitations: downloading a file does not remove SpecterX tracking from the link; the sender's audit log still records the download event

**Related articles:** Open with Microsoft Office (desktop) · Open with Adobe Desktop · Encrypt downloaded files with a password · Protect downloaded files with Rights Management (RMS)

---

### 📋 Open with Adobe Desktop

**Audience:** Recipients

**Topics to cover:**
- Prerequisites: Adobe Acrobat Reader or Acrobat Pro installed; the SpecterX viewer plugin or the RMS client (if RMS-encrypted)
- How to click "Open with Adobe Desktop" in the SpecterX Viewer
- What the file looks like in Adobe after download/decryption
- Policy enforcement in Adobe: watermarks, restrictions on copying/printing (if RMS is enabled)
- Limitations: only available for supported file types (primarily PDF)
- What happens if you open the file on a device where Adobe is not installed

**Related articles:** Download a protected file · Open with Microsoft Edge

---

### 📋 Open with Microsoft Office (desktop)

**Audience:** Recipients

**Topics to cover:**
- Prerequisites: Microsoft 365 or Office installed; RMS client configured (for RMS-protected files)
- Downloading the file from the SpecterX Viewer and opening it in Office
- RMS-encrypted files: the rights management bar that appears in Office, showing restrictions
- What restrictions apply (edit, copy, print, screenshot) depending on policy
- What to do if Office cannot decrypt an RMS file (Azure RMS client not configured, expired access)
- Supported file types: DOCX, XLSX, PPTX

**Related articles:** Download a protected file · Open with Office Online

---

### 📋 Open with Microsoft Edge

**Audience:** Recipients

**Topics to cover:**
- What "Open with Microsoft Edge" means: opens a PDF or supported file in Microsoft Edge's built-in PDF reader directly from the SpecterX Viewer
- Prerequisites: Microsoft Edge installed (version 80 or later); RMS client if the file is RMS-encrypted
- How to select this option from the SpecterX Viewer's "Open with" menu
- What policy enforcement applies in Edge (watermarks are visible; RMS restrictions persist if enabled)
- Supported file types: primarily PDF; DOCX/XLSX/PPTX rendering depends on Edge's Office integration
- Limitations: once the file is open in Edge, SpecterX cannot track further actions (print, screenshot, save-as) unless RMS is also enabled
- What to do if Microsoft Edge is not installed (use the in-browser Viewer instead)

**Related articles:** Open with Adobe Desktop · Download a protected file

---

### 📋 Open with Office Online

**Audience:** Recipients

**Topics to cover:**
- What "Open with Office Online" means: opening the file in the SpecterX WOPI Host, which renders it using Microsoft Office Online
- No download required; the file stays under SpecterX protection
- How to access this option in the SpecterX Viewer
- What operations are available (view, edit — if permitted by policy)
- Supported file types: DOCX, XLSX, PPTX
- Known limitations: not all Office Online features are available; macros and complex formatting may not render

**Related articles:** Open with Microsoft Office (desktop) · Open with Google Drive

---

### 📋 Open with Google Drive

**Audience:** Recipients

**Topics to cover:**
- What "Open with Google Drive" means: the file is handed off to Google Docs/Sheets/Slides for viewing and editing
- Prerequisites: a Google account; Google Workspace access (optional)
- How to access this option from the SpecterX Viewer
- What policy enforcement applies after the file is in Google Drive
- Supported file types: DOCX (→ Google Docs), XLSX (→ Google Sheets), PPTX (→ Google Slides)
- Limitations: once the file is in Google Drive, SpecterX loses direct control over it (watermarking applies if RMS is enabled)

**Related articles:** Open with Office Online · Open with Microsoft Office (desktop)

---

### 📋 Send a file back to the sender

**Audience:** Recipients

**Topics to cover:**
- What "Send a file back" means: the recipient can upload a file to the sender's SpecterX using the return link in the notification email
- Finding the return link in the original notification email
- The upload flow: what the recipient sees, what file types are accepted
- Where the file appears in the sender's account
- Policy that applies to return files

**Related articles:** Tour the SpecterX Recipient Page

---

### 📋 What the SpecterX Viewer lets you do

**Audience:** Recipients

**Topics to cover:**
- What the SpecterX Viewer is: a browser-based document viewer that opens a protected file in the browser
- That it requires no plugins or software installation for supported file types
- Toolbar actions present in the Viewer (only document buttons confirmed to exist on the live product before publishing)
- Dynamic watermark display when watermarking is enabled by the sender's policy

> **Note to writer:** Many earlier draft bullets in this article (specific copy/print/screenshot restrictions, mobile-viewer behaviour, comparative claims about the downloaded copy) were unverified. Only document Viewer capabilities confirmed against the live product before publishing this article. Restrictions enforced by RMS belong in the RMS article, not here.

**Related articles:** Tour the SpecterX Recipient Page · Open a SpecterX-protected file · Download a protected file

---

## Section 4 — Work with Workspaces

Audience: end users and collaborators who use SpecterX Workspaces for secure collaboration.

---

### 📋 Create and manage a workspace
**Audience:** End users (Collaborator or Admin)

**Topics to cover:**
- What a Workspace is: a secure, persistent collaboration space with a parent policy, folder structure, and shared access
- Creating a new workspace: name, parent policy, storage integration (if configured)
- The limitation that workspace names cannot be changed after creation
- Workspace settings: viewing the workspace's current parent policy, editing settings
- The sidebar tabs in a workspace: Files, Members, Policy, Audit
- Storage routing: the files you upload to a workspace are stored in SpecterX-managed storage by default; if your admin has configured a storage integration, files are stored in your organisation's Amazon S3 bucket, SharePoint site, or Google Cloud Storage bucket instead — see "Connect Amazon S3 storage", "Connect SharePoint storage", and "Connect Google Cloud Storage" in §9
- Licensing requirement: Collaborator or Admin licence required to create a workspace
- If you navigate away before adding recipients, the workspace is created but has no members; it can be managed from the Workspaces list
- Parent policy inheritance: all files uploaded to a workspace automatically inherit the workspace's parent policy; file-level policy changes are temporary and revert to the parent policy when a new member accesses the workspace
- When the parent policy changes, all existing files adopt the new parent policy the next time a member accesses the workspace
- Known limitation (RMS conflict): re-uploading a previously RMS-encrypted file into an RMS-governed workspace will fail because the system attempts to re-encrypt; download the file, strip the prior protection, and re-upload

**Related articles:** Invite collaborators & set roles · Upload files to a workspace · Understand folder policy inheritance · Connect Amazon S3 storage · Connect SharePoint storage · Connect Google Cloud Storage

---

### 📋 Invite collaborators & set roles
**Audience:** Workspace owners and co-owners

**Topics to cover:**
- Who can invite users: workspace owners and co-owners
- Inviting internal users (already in your SpecterX org)
- Inviting external users (they are auto-provisioned at the moment of invitation)
- Assigning roles: Viewer, Contributor, Co-Owner
- What each role can do (link to User roles & permissions reference)
- Modifying or removing a collaborator after the workspace is created
- The "Manage Access" function in the workspace sidebar
- External users and licensing: external contributors are not charged for by SpecterX
- Workspace role capabilities at a glance:
  - **Owner**: manage parent policy; view all audit logs; delete any file; add/change member roles
  - **Co-Owner**: same as Owner except Co-Owners do not receive workspace activity notifications
  - **Contributor**: upload files; view and delete own files; see audit logs for own files
  - **Viewer**: view all files; cannot upload; cannot see audit logs
- Workspace groups: a workspace can be shared with a SpecterX group; individual role assignments override group-level role assignments
- File ownership is always the uploader's — Workspace Owners cannot delete another user's files via the Viewer permission path, but Owners and Co-Owners can delete any file through the management UI

---

### 📋 Upload files to a workspace

**Audience:** Contributors and workspace owners

**Topics to cover:**
- The drag-and-drop or file-picker upload in a workspace
- Policy inheritance: newly uploaded files inherit the workspace's parent policy by default
- Manually changing a file's policy after upload (and the automatic revert to parent policy if changed)
- Bulk uploads: behaviour with large batches
- Storage routing: where the file is actually stored (SpecterX storage, SharePoint, S3, or GCS depending on workspace configuration)
- File size limits

---

### 📋 Manage folders in a workspace

**Audience:** Contributors and workspace owners

**Topics to cover:**
- Creating a folder in a workspace
- Nesting folders and sub-folders
- How policy propagates: parent workspace policy → sub-folder → file
- Renaming and deleting folders
- The effect of deleting a folder on its files and shares
- Folder-level permissions: can you restrict a folder to a subset of workspace members?

---

### 📋 View workspace audit logs

**Audience:** Workspace owners, auditors

**Topics to cover:**
- How to access workspace-specific audit logs (the "View logs" button in the workspace)
- What events are logged: file views, uploads, downloads, permission changes, policy updates
- The difference between workspace-level and organisation-level audit logs
- Filtering the audit log within a workspace
- Who can see workspace audit logs (workspace owners, Co-Owners, and org Administrators — external contributors cannot)
- Cross-reference to the main audit logs article for export and advanced filtering

---

### 📋 Understand folder policy inheritance
**Audience:** End users, admins

**Topics to cover:**
- How the folder hierarchy works in SpecterX: the parent folder sets the baseline for all content below it
- Access inheritance: a user added at the parent folder automatically has access to all subfolders and files within it; this cannot be manually removed at the child level
- Policy inheritance order (highest priority first):
  1. Governance-locked policy (set by a Platform Governance Rule)
  2. Explicit policy set on the subfolder or file directly
  3. Parent folder's policy
- Adding access at the child level: subfolders and files can be shared with additional users who do not have parent-folder access
- Removing inherited access: you cannot remove a user's inherited access from a child object; to remove access, update the parent folder
- Partial access: a user may have access to the parent but be blocked from specific child objects by governance rules
- Retention logic: the **earliest** retention event wins — if a file's policy expires before the folder, the file expires first; if the folder expires before its contents, the folder expiry removes everything
- Policy change behaviour: when you change the parent folder's policy, SpecterX updates only items that currently inherit the parent policy by default; items with their own explicit policy are not overridden unless you choose to override all
- UI indicators: the folder drawer shows a summary if access, policy, or retention differs within the folder; use the detail view to drill down by user or by item

---

## Section 5 — Send protected email

Audience: users who send and receive protected email via the Outlook or Gmail connectors.

---

### 📋 Outlook Classic vs Outlook Add-in — which should I use?

**Audience:** Users (and IT admins deciding which to deploy)

**Topics to cover:**
- **Outlook Add-in**: works on Outlook for Web (OWA), Outlook for Desktop (Windows and Mac), and Outlook Mobile. Recommended for all new installations.
- **Outlook Classic Add-in**: Windows Outlook Desktop only. In maintenance mode — no new features are being added. Suitable only for organisations that cannot upgrade.
- Decision table: which scenarios require Classic vs which should use New
- How to check which version you have installed
- The conflict warning: if both are installed simultaneously, they will conflict — only one should be active
- How to migrate from Classic to New (uninstall Classic first)

---

### 📋 Get started with the SpecterX Outlook Add-in

**Audience:** End users, IT admins

**Topics to cover:**
- What the Outlook Add-in does: adds a SpecterX protection toggle to the Outlook compose window
- Platforms: Outlook for Web, Windows Desktop, Mac Desktop, and Outlook Mobile
- Links to all lifecycle articles: install, send, track, troubleshoot, uninstall
- Cross-reference to Outlook Classic disambiguation article
- Brief description of the recipient experience (what the person receiving the email sees)

---

### 📋 Set up the SpecterX Outlook Add-in
**Audience:** IT admins (for org-wide deployment), individual users (for self-installation)

**Topics to cover:**
- Prerequisites: Microsoft 365 subscription; Outlook version requirements
- Admin deployment via Microsoft 365 Admin Center (recommended for org-wide rollout)
- Group Policy / Intune deployment options
- Individual self-installation from the Microsoft AppSource
- Activating the add-in after installation (the activation flow, authenticating to SpecterX)
- Verifying the add-in is active (the SpecterX button appears in Outlook compose)
- Installation in Outlook for Web (OWA)
- Required manifest permission: `ReadWriteMailbox` — required to modify the email body and set custom properties; this permission level is needed for the on-send handler to inject SpecterX metadata
- Minimum Outlook requirement: Mailbox API version 1.13 or later
- Deployment documentation: after org-wide deployment, users access the add-in via "Show Add-in" in the Outlook ribbon; for OWA, users open it via the Apps menu

**Related articles:** Send a protected email with the Outlook Add-in · Troubleshoot the Outlook Add-in · Uninstall the Outlook Add-in · Outlook Classic vs Outlook Add-in — which should I use?

---

### 📋 Send a protected email with the Outlook Add-in
**Audience:** End users

**Topics to cover:**
- Opening a new email and locating the SpecterX button
- In Outlook Desktop: the "Virtru for Outlook" / "SpecterX" button in the ribbon
- In OWA: opening the Apps menu and clicking SpecterX
- Turning Virtru Protection On (the toggle and what turning it on does)
- The SpecterX side panel: what it shows (policy selector, recipient list, per-recipient permissions)
- Pinning the side panel for continued use
- Attaching files and adding the email body
- Adding a Personal Introduction (unprotected message that the recipient reads before verifying)
- Selecting a policy from the side panel
- Sending the email and what SpecterX does in the background
- The "Virtru is working on your request" modal
- Protecting the email body and subject line (the "Protect Email Content" checkbox)
- Protection modes: **Off** (no protection), **Attachments only** (body is unprotected), **Entire message** (body + attachments encrypted); same model as the Gmail connector
- Phone and password verification: if the selected policy requires phone or password verification, the task pane prompts for recipient phone numbers or passwords before allowing send; send is blocked until all recipients have the required detail entered
- Plain-text email limitation: if the email body is plain text (not HTML), body metadata injection is skipped — only attachment protection applies; the body will not be encrypted even when "Entire message" is selected
- What SpecterX does on send: the on-send handler injects a hidden base64-encoded metadata payload into the HTML body and (if configured) adds the SpecterX audit address to CC/BCC before the email leaves the client

---

### 📋 Troubleshoot the Outlook Add-in

**Audience:** IT admins and end users

**Topics to cover:**
- Add-in not appearing in Outlook: installation troubleshooting, clearing the cache
- Activation errors: "could not authenticate", SSO token issues
- The add-in appears but protection toggle does not work
- Conflicts with the Classic Add-in (only one should be installed)
- Cookie and pop-up requirements for OWA
- Delegated and shared mailboxes: known limitations and workarounds
- Printing secure emails from OWA
- Error messages with explanations and next steps

---

### 📋 Uninstall the Outlook Add-in

**Audience:** End users, IT admins

**Topics to cover:**
- Self-removal from Outlook for Web (manage add-ins)
- Removing from Outlook Desktop (Windows and Mac)
- IT admin removal via Microsoft 365 Admin Center
- What happens to previously sent emails after uninstallation (they remain protected)

---

### 📋 Get started with the SpecterX Outlook Classic Add-in

**Audience:** Existing Classic Add-in users (Windows only)

**Topics to cover:**
- Maintenance mode notice: this add-in is for Windows Desktop only and no new features are being added. New installations should use the Outlook Add-in.
- What the Classic Add-in does vs the Outlook Add-in
- Links to its lifecycle articles
- Recommendation to migrate to the Outlook Add-in

---

### 📋 Set up the SpecterX Outlook Classic Add-in

**Audience:** IT admins (Windows organisations that cannot upgrade)

**Topics to cover:**
- Prerequisites: Windows, Outlook Desktop (specific minimum version)
- Downloading the MSI installer
- Group Policy deployment for org-wide rollout
- Individual installation (double-click the MSI)
- Post-install activation
- The conflict warning: do not install alongside the Outlook Add-in

---

### 📋 Send a protected email with the Outlook Classic Add-in

**Audience:** End users on Windows Outlook Desktop

**Topics to cover:**
- The SpecterX "Enable Protection" button in the Outlook toolbar
- The SpecterX panel that opens on the right-hand side
- Setting per-recipient permissions
- Selecting a policy
- Phone verification: entering the recipient's phone number when required
- Protecting the email body ("Protect Email Content" checkbox)
- Sending and what the recipient experiences

---

### 📋 Get started with the SpecterX Gmail Extension

**Audience:** End users

**Topics to cover:**
- What the Gmail Extension does: adds a SpecterX protection section to the Gmail Compose window
- Chrome Extension — must be installed in Chrome or Chromium-based browser
- Links to lifecycle articles: install, send, troubleshoot
- Cross-reference to the Outlook disambiguation article
- Brief recipient experience overview

---

### 📋 Set up the SpecterX Gmail Extension

**Audience:** IT admins (Chrome policy deployment), individual users (self-install)

**Topics to cover:**
- Prerequisites: Chrome browser; Google Workspace or personal Gmail
- Self-installation from the Chrome Web Store
- Admin deployment via Chrome Enterprise policy (force-install for all users in a domain)
- Post-install activation: logging in to SpecterX from the extension
- Verifying the extension is active (the SpecterX Protection section appears in Compose)

---

### 📋 Send a protected email with the Gmail Extension

**Audience:** End users

**Topics to cover:**
- The SpecterX Protection section in the Gmail Compose window
- Choosing what to protect: Attachments only, or Entire message (body + attachments)
- Adding recipients in the To, CC, BCC fields
- Selecting a policy
- Assigning per-recipient permissions
- Sending and confirming protection was applied
- How to tell if a sent email is protected (the indicator in Gmail Sent view)

---

### 📋 Troubleshoot the Gmail Extension

**Audience:** IT admins and end users

**Topics to cover:**
- Extension not appearing in Gmail Compose: reinstallation, Chrome version check
- Activation errors
- The SpecterX Protection section appears but protection is not applied after sending
- Issues with group addresses / aliases
- Extension not visible after force-install (Chrome policy propagation delay)

---

## Section 6 — Connectors

Audience: users and admins who want to protect files through third-party apps. This section covers Share-in-Place Connectors (Google Drive, SharePoint), Messaging Connectors (Slack), and CRM (Salesforce report export and email protection).

---

### Share-in-Place Connectors

Connectors where the file stays in its original storage location — SpecterX adds protection and access control without moving or copying the file.

---

### 📋 Set up the Google Drive Connector

**Audience:** IT admins

**Topics to cover:**
- What the Google Drive Connector is: a share-in-place integration that applies SpecterX protection to files that remain in Google Drive
- Prerequisites: Google Workspace account; admin access to authorise the SpecterX app in Google Workspace
- Authorising SpecterX in the Google Admin Console (OAuth app allow-listing)
- Configuring the connector in SpecterX Settings → Integrations → Google Drive
- Testing the connection
- Per-user activation vs org-wide deployment

---

### 📋 Share a Google Drive file with SpecterX protection

**Audience:** End users

**Topics to cover:**
- Finding the SpecterX option in the Google Drive file context menu (or via the SpecterX web UI)
- Selecting the file to protect (the file stays in Google Drive, SpecterX does not copy it)
- Choosing recipients and a policy
- What the recipient experiences when they click the link (they go to the SpecterX Recipient Page, not directly to Drive)
- How the file owner sees protected shares in Google Drive
- Revoking access from within Google Drive vs from the SpecterX web platform

---

### 📋 Troubleshoot the Google Drive Connector

**Audience:** IT admins and end users

**Topics to cover:**
- Authentication errors when connecting SpecterX to Google Drive
- "Insufficient permissions" when trying to share a Drive file
- Files not appearing in the SpecterX file picker
- Recipient errors when accessing a Drive-backed protected link

---

### 📋 Set up the SharePoint Connector

**Audience:** IT admins

**Topics to cover:**
- What the SharePoint Connector is: share-in-place for SharePoint libraries — files stay in SharePoint, SpecterX adds protection at the access layer. **Distinct from SharePoint Storage integration** (§9), which routes SpecterX-managed file storage to a SharePoint site
- Prerequisites: SharePoint Online (Microsoft 365); admin access to register SpecterX as an Azure App
- Registering the SpecterX app in Azure Active Directory / Entra ID
- Configuring the connector in SpecterX Settings → Integrations → SharePoint Connector
- Site and library scoping: configuring which SharePoint sites SpecterX can access
- Testing the connection
- Deployment scope: the connector is deployed at the **site level** — once deployed to a site, it is available across the entire site; deployment cannot be scoped to individual libraries, folders, or files
- The four supported deployment patterns: All Users + All Sites / All Users + Some Sites / Some Users + All Sites / Some Users + Some Sites
- Licensing: deployment makes the "Share via SpecterX" command available but does not assign SpecterX licences; users are provisioned automatically on their first SpecterX share
- Who controls visibility: SharePoint permissions and optional audience targeting govern which users see the "Share via SpecterX" command — not SpecterX itself
- V1 scope limitation: the connector supports sharing individual files or multiple files selected together; sharing entire folders is **not** supported in V1

**Related articles:** Share a SharePoint file with SpecterX protection · Troubleshoot the SharePoint Connector · Connect SharePoint storage (§9) — disambiguation between the connector and the storage integration

---

### 📋 Share a SharePoint file with SpecterX protection
**Audience:** End users

**Topics to cover:**
- Finding the SpecterX share option for a SharePoint file
- The share-in-place model: the file stays in SharePoint, SpecterX wraps the access
- Policy selection and recipient permissions
- Recipient experience
- How protected SharePoint links behave when the SharePoint permissions change
- Revoking access
- Two-stage access model:
  - **Stage 1 (Authorization & Registration)**: the connector sends file metadata (including Purview sensitivity label if present) to SpecterX; if PAR allows the share, SpecterX generates the access link and records the file in My Files as "Uploaded to SPX"; the SharePoint file is **not** modified at this stage
  - **Stage 2 (Recipient access & protection)**: when an authorised recipient authenticates, SpecterX fetches the current version of the file from SharePoint, applies policy protections (encryption, watermarking, access restrictions), and delivers the governed copy; the SharePoint file remains the unmodified reference copy
- Live access: the recipient always receives the **current** version of the SharePoint file at the time of access — changes made in SharePoint after the share is created are reflected at next recipient access
- Inbound files (Send File Back): files uploaded by recipients via the "Send a file back" feature are stored in SpecterX dedicated storage, never written back to the customer's SharePoint environment
- PAR block behaviour: if Platform Governance Rules block the share, no link is created and nothing appears in My Files; a block message appears in real time in the SpecterX share workflow

---

### 📋 Troubleshoot the SharePoint Connector

**Audience:** IT admins

**Topics to cover:**
- Azure App registration errors
- Insufficient scope (missing SharePoint API permissions)
- "File not found" errors when protecting a SharePoint file
- Token refresh failures

---

### Messaging Connectors

Connectors where the destination is a chat or messaging platform.

---

### 📋 Set up the Slack Connector

**Audience:** IT admins

**Topics to cover:**
- What the Slack Connector is: protects files shared in Slack channels by replacing the native Slack file with a SpecterX-protected link (V1 supports channels only; DM support is planned)
- Prerequisites: a Slack workspace; Slack admin access to install the SpecterX Slack App
- Installing the SpecterX App from the Slack App Directory
- Configuring the connector in SpecterX Settings → Integrations → Slack
- Authorising the OAuth connection
- Testing the connection (sending a test file to a Slack channel)
- Required Slack permissions the app needs: read messages, download files, delete files (to remove the original after protection), and edit messages (to insert the SpecterX link)
- V1 enforcement scope: protection applies **only to channels** where the SpecterX app is installed; Direct Messages (DMs) are **not** supported in V1
- Channel installation: the connector is enabled per channel through the channel's integration menu; any channel member can enable it, provided the app has been authorised and published to the Slack workspace by an admin
- Enforcement boundary: if the SpecterX app is removed from a channel, protection stops for new uploads in that channel; files already processed remain protected and are not restored to native Slack files

---

### 📋 Send a protected file to Slack

**Audience:** End users

**Topics to cover:**
- Sharing a file to Slack from the SpecterX web UI (the Slack icon in the share toolbar)
- Choosing a Slack channel recipient
- The protected link that appears in the Slack message (not an attachment — a SpecterX link)
- Policy selection
- What the Slack recipient sees and how they access the file
- Revoking access to a Slack-shared file

---

### 📋 Send a protected file in a Slack channel
**Audience:** End users

**Topics to cover:**
- What happens when you upload a file to a Slack channel protected by SpecterX: SpecterX automatically intercepts the upload, removes the original Slack-hosted file, stores a protected copy, and replaces the Slack message with a SpecterX-protected link
- The user experience during processing: the message briefly shows "Processing [file name]" before the protected link replaces the original; processing typically completes within seconds but may take up to ~20 seconds
- What the SpecterX-protected link looks like in Slack: "The file in this message is protected by SpecterX." — no file preview or link unfurl is generated by Slack
- V1 limitation: the protected link does not display the original filename
- Recipient access: channel members at the time of upload are automatically provisioned as recipients; clicking the link takes them to the SpecterX Recipient Page for verification and viewing
- Policy applied: a single default protection policy is applied to all Slack-originated files; users cannot select a policy per-file in V1
- File ownership: the user who uploaded the file is the Data Owner; all channel members at upload time are recipients
- Managing Slack-protected files: permissions and audit history are managed in the SpecterX web UI (not in Slack); recipients can be added or removed from a Slack-protected file via the SpecterX web UI
- First-time use: the first time a user uploads a file to a protected channel, they receive a Slack DM from the SpecterX app explaining its role — this first upload serves as implicit app authorization
- Late joiners: users who join a channel after a file has been shared will be denied access to existing SpecterX-protected links; the original file owner receives a notification of the failed access attempt
- What SpecterX does **not** do in Slack: it does not protect message text, does not monitor DMs, and does not automatically apply to new channels — each channel must be enabled individually

---

### 📋 Troubleshoot the Slack Connector

**Audience:** IT admins

**Topics to cover:**
- App installation errors
- OAuth token expiry
- "Channel not found" errors
- The SpecterX Slack App was uninstalled and the connector needs to be re-authorised

---

### CRM

Connectors and integrations that protect data flowing through CRM systems — both report exports and CRM-originated email.

---

### 📋 Install the SpecterX Salesforce Browser Extension

**Audience:** Salesforce users (inside the browser)

**Topics to cover:**
- What the Salesforce Browser Extension is: a Chrome/Edge extension that adds SpecterX export protection to Salesforce
- Installing from the Chrome Web Store or Edge Add-ons store
- Activating the extension: logging in to SpecterX from the extension popup
- Verifying the extension is active inside Salesforce (the SpecterX button appears)

---

### 📋 Export and protect Salesforce reports

**Audience:** Salesforce users

**Topics to cover:**
- Running a Salesforce report and clicking the SpecterX "Protect Export" button
- Choosing a policy for the exported file
- What happens: the report is exported as an Excel or CSV file and wrapped with SpecterX protection
- Sharing the protected export link
- Use cases: protecting Salesforce reports shared with external partners, auditors, or board members
- Supported Salesforce report types

---

### 📋 Send protected emails from Salesforce

**Audience:** IT admins (who configure the integration), Salesforce users (who benefit from it)

**Topics to cover:**
- What this integration does: enables Salesforce to automatically send SpecterX-protected emails via the SpecterX API — no manual per-email action required from the sender
- How it works: Salesforce includes SpecterX API parameters in an outbound API call; SpecterX applies the specified policy and delivers the protected email to the recipient
- Two protection scopes:
  - **Attachments** (default): protects attached files only; the email body is sent unprotected
  - **All**: protects both the email body and all attachments
- Policy selection: the SpecterX policy is specified as a parameter in the Salesforce API call; policy enforcement is handled entirely by SpecterX, not by Salesforce
- Prerequisites: SpecterX API credentials configured; the API integration set up by your Salesforce admin; SpecterX tenant with Mail Protection enabled
- Recipient experience: recipients receive the standard SpecterX notification email and go through the normal Recipient Page verification flow — identical to any other SpecterX-protected share
- What SpecterX does not control in this flow: Salesforce's decision about which emails to protect and when to trigger the API call — that logic lives in Salesforce

**Related articles:** Export and protect Salesforce reports · Tour the SpecterX Recipient Page

---

## Section 7 — Configure security policies

Audience: administrators who create and manage security policies.

---

### 📋 Configure a security policy

**Topics to cover:**
- Opening the Policies page (`/policy-editor`)
- Creating a new policy and naming it
- Policy Configuration: Restrict Policy to Specific Users toggle
- Access Control: Recipient Sharing Permissions (Allow Anyone / Restrict to Domain / Disable Sharing)
- Access Control: Verification Requirements (Email OTP / Phone SMS / Personal Secret — combinable for MFA)
- Access Control: Acknowledge Receipt toggle
- Data Protection: Protect and Track (always on)
- Data Protection: Block file download
- Data Protection: Encrypt using a Password (supported formats, mutual exclusivity with Block)
- Data Protection: Encrypt using Rights Management (RMS) (requires Azure RMS / Entra ID)
- Data Protection: Watermark
- Recipient Experience: language (English / Hebrew)
- Saving with Apply; Duplicating; Deleting (not the Default policy)
- Policy examples table (standard, external partner, highly sensitive, board package)

---

### 📋 Apply a policy when sharing — files, folders, workspaces & email

**Audience:** End users (all sender roles)

**Topics to cover:**
- **From the web platform** (Share files dialog): the policy dropdown in Step 2 of the share flow
- **From a Workspace**: the Parent policy setting in workspace settings; how newly uploaded files inherit the workspace policy
- **From a folder share**: setting or changing a policy on a shared folder
- **From Outlook** (Outlook Add-in): the policy selector in the SpecterX side panel
- **From Gmail Extension**: the policy selector in the Compose protection section
- How to know which policy to choose: guidance on matching policy to data sensitivity
- What to do when no suitable policy exists (ask your admin to create one)
- Cross-reference links to the policy configuration admin article and to individual policy-protection articles

---

### 📋 Control who can reshare your files

**Audience:** Admins (who configure the policy), end users (who understand the effect)

**Topics to cover:**
- The Recipient Sharing Permissions setting in the Access Control section of a policy
- **Allow Sharing with Anyone**: recipients can forward the link to any email. When to use this.
- **Restrict Sharing to Recipient's Domain**: recipients can only forward to addresses at the same domain as theirs. Use case: partner NDA sharing.
- **Disable Further Sharing**: recipients cannot forward. The forward/share button is hidden in the SpecterX Viewer. Use case: highly sensitive data, board packages.
- How forwarded links inherit the original policy (they are NOT copies; they are the same link with the same controls)
- What happens when a restricted recipient tries to forward to an out-of-domain address

---

### 📋 Require identity verification before opening a file

**Audience:** Admins (configure), end users (understand)

**Topics to cover:**
- The three verification methods and when to use each:
  - **Email OTP**: most common, no pre-registration needed. Recipient gets a code in their inbox.
  - **Phone (SMS/call) OTP**: stronger second factor. Sender must enter recipient's phone number at share time.
  - **Personal Secret**: sender defines a passphrase at share time; recipient must enter it.
- Combining methods for multi-factor access (Email + Phone, Email + Secret, etc.)
- The Acknowledge Receipt toggle: what it does (the recipient must confirm identity before the file opens)
- How verification interacts with SSO (Google/Microsoft SSO can satisfy email verification automatically)
- Cross-reference to the recipient-side articles for SMS and personal secret flows

---

### 📋 Add a watermark to protected files

**Audience:** Admins

**Topics to cover:**
- What dynamic watermarking does: overlays the recipient's email address and access timestamp on every page
- Enabling the Watermark toggle in the Data Protection section of a policy
- What the watermark looks like in the SpecterX Viewer (position, font, tiling)
- Customising watermark text and position (admin-configurable)
- Whether watermarking applies to downloaded copies (only if RMS is also enabled)
- Supported file types (link to watermarking limitations article in §11)
- Use cases: deterring unauthorised screenshot distribution, creating an audit trail of who accessed the file

**Related articles:** Watermarking — supported formats & limitations · Policy controls reference · What SpecterX does and does not protect

---

### 📋 Prevent recipients from downloading files

**Audience:** Admins

**Topics to cover:**
- Enabling the **Block file download** toggle
- What the recipient sees: the download button is hidden in the SpecterX Viewer
- This does not prevent screenshots — for that, combine with RMS encryption
- Interactions: Block download and Encrypt with Password are mutually exclusive
- Use cases: presentations and reports where you want view-only access
- Limitations: link to block-download limitations article in §11

**Related articles:** Block download — scope & limitations · Protect downloaded files with Rights Management (RMS) · Policy controls reference · What SpecterX does and does not protect

---

### 📋 Encrypt downloaded files with a password
**Audience:** Admins

**Topics to cover:**
- What password encryption does: downloaded copies require a password to open (using native Office/PDF password protection)
- Enabling the **Encrypt using a Password** toggle
- At share time: the sender is prompted to set a password for downloaded copies
- At download time: the recipient downloads a password-protected file and must enter the password to open it
- Supported formats: .pdf, .docx, .xlsx, .pptx
- The difference between this and the personal secret (personal secret = access to the SpecterX link; download password = opening the downloaded file)
- Mutual exclusivity with Block file download
- Link to password encryption limitations article in §11
- Unified password model: each recipient has a single protection password that applies to both link authentication (when required by policy) and file-level download encryption
- Password change behaviour: if the password is changed (by a collaborator or admin), it takes effect immediately for all active links; previously downloaded encrypted files remain encrypted with the **prior** password and are not re-encrypted
- Admin password reset: a tenant admin can reset or reassign a recipient's protection password through the SpecterX web UI; this also updates all active links for that recipient
- Exclusivity constraint: password-protected downloads cannot be combined with RMS encryption, watermarking, or viewer-only enforcement — these controls are mutually exclusive at the file-level protection layer
- Scope limitation: password authentication at link level is limited to direct, single-recipient access and cannot be combined with allow-forwarding or domain-based access models

**Related articles:** Password encryption — supported formats & limitations · Verify with a personal secret · Protect downloaded files with Rights Management (RMS) · Policy controls reference

---

### 📋 Protect downloaded files with Rights Management (RMS)

**Audience:** Admins

**Topics to cover:**
- What Microsoft RMS encryption does: encrypts the file using Azure Rights Management so it can only be opened by authorised users, on authorised devices, with the RMS client
- Enabling the **Encrypt using Rights Management** toggle
- Prerequisites: an active rights management configuration in the SpecterX tenant (configured via Entra ID)
- What the recipient needs to open an RMS-encrypted file: the Microsoft RMS client (installed automatically with Office 365); a Microsoft account (or Entra ID account)
- Permission enforcement in RMS: copy, print, screenshot restrictions
- The difference between RMS encryption and password encryption
- When to use RMS: regulated industries where files may leave the SpecterX ecosystem
- Link to RMS requirements & limitations article in §11

**Related articles:** How Rights Management (RMS) protection works · Rights Management (RMS) — requirements & limitations · Encrypt downloaded files with a password · Policy controls reference

---

### 📋 Configure Platform Governance Rules
**Audience:** Admins

**Topics to cover:**
- What Platform Governance Rules are: organisation-wide automated rules that apply policies to files based on conditions (content type, classification label, sender group, destination domain)
- Rule structure: condition → action (apply policy X, block share, notify admin)
- Creating a rule in the SpecterX admin UI
- Rule priorities: when multiple rules match, which one applies
- The relationship between Governance Rules and DLP integrations (rules can be triggered by DLP classifications from Purview or a DLP mailflow integration)
- Common rule patterns: "If a file is labelled Confidential, apply HIPAA policy"; "If a file is shared to an external domain, require phone verification"
- Single rule template with variable actions: every rule uses the same creation form; the selected **action** determines the rule type — Exception, Block, or Policy Assignment — and controls how the rule is evaluated and labelled in the UI
- Fixed evaluation order (always applied in this sequence):
  1. **Exception rules** — if a matching exception is found, PAR steps aside entirely; the user proceeds with their manually selected policy; exceptions are not ordered relative to each other
  2. **Block rules** — block matching recipients or files; unmatched recipients and files continue; block rules are not ordered relative to each other
  3. **Policy Assignment rules** — evaluated top-to-bottom; the **first** matching rule determines the policy for the entire share; the assigned policy is **locked** and cannot be changed by the user
- Rule conditions (V1): **From** (sender identity or group), **To** (recipient identity, domain, or "all external"), **Classification** (Microsoft Purview sensitivity label) — a rule must define at least one condition; all enabled conditions must match for the rule to trigger
- PAR coverage in V1: applies to the SpecterX WebUI, SharePoint Connector, and Mail Connector (attachments only); **not** applied to Workspaces, Slack Connector, or Salesforce Connector in V1
- Policy locking: when PAR assigns a policy, the policy dropdown is locked in the UI; users cannot change the policy unless the rule is removed or the triggering conditions no longer apply
- Group targeting: rules can target SpecterX groups; if any member of a group triggers a block condition, the block applies to the group as a whole when the recipient is defined as the group
- New Share Drawer UX: when PAR evaluates a new share, results appear in the share drawer before the share is finalised — Pane 1 collects files and recipients; Pane 2 shows the PAR evaluation result (locked policy, blocked recipients, blocked files); Pane 3 shows the post-share summary
- Backend notifications: for email-based shares and SharePoint shares where PAR acts after the user has submitted, the sender receives an email notification listing which policies were assigned and which files or recipients were blocked
- Known V1 limitation — domain-forwarding + user blocking: block rules cannot enforce **user-level** blacklisting when domain-based forwarding policies are used on RMS-protected files; blocking in this scenario applies at the domain level

**Related articles:** Understand Platform Governance Rule audit events · Target a Platform Governance Rule at specific user groups · Understand default policies and policy availability · Configure Microsoft Purview classification (§9) · Map Microsoft Purview sensitivity labels to SpecterX policies (§9)

---

### 📋 Understand Platform Governance Rule audit events
**Audience:** Admins, auditors, compliance officers

**Topics to cover:**
- Overview: PAR produces two categories of audit events — **enforcement events** (triggered when a rule fires during a share) and **configuration events** (triggered when the published ruleset changes)
- **Enforcement audit events** — the operations recorded during share flows:
  - `Upload`: file uploaded into the share drawer; logged per file with default policy, empty Rule column
  - `Recipient Added`: sender has added recipients and clicked Next (triggering PAR evaluation); records the proposed recipient state before PAR acts
  - `Share Evaluation Request`: explicitly records that PAR evaluated the share; always logged for every evaluated share regardless of outcome
  - `Rules Suggest Block` (WebUI only): logged when a block fires and is shown to the sender in Pane 2, even if the sender later abandons the share
  - `Exception Rule Triggered`: logged when an exception rule fired (records that no enforcement action was taken)
  - `Rule Suggests Policy` (WebUI only): logged when policy assignment fires before the share is sent; records the proposed policy, not the final committed state
  - `Set Policy`: logged only if the sender manually changed the policy from the upload-event default; not logged if PAR set the policy
  - `Permissions Added`: logged when access is provisioned (after PAR evaluation); the Rule column lists the Policy Assignment Rule name if the policy is locked
  - `Policy Unlocked`: logged when a previously locked policy becomes unlocked (rule deleted or triggering condition removed)
  - `Permissions Removed`: logged when access is revoked (existing event, no change with PAR)
- **Backend variants** (email, SharePoint, My Files re-share): use the same operations as above but do not surface PAR results in real time to the sender; the sequence is Share Evaluation Request → Rule triggers (Policy, Block, Exception) → Permissions Added
- **Configuration audit events** — the operations recorded when the ruleset changes:
  - Rule activated (toggled on)
  - Active rule edited and saved (republished)
  - Rule deactivated (toggled off)
  - Policy Assignment rules reordered
  - Each entry records: tenant, rule identifier, action taken, timestamp, resulting published ruleset state
- Audit log columns relevant to PAR: **Operation**, **Rule** (Rule name if triggered), **Policy** (policy name; locked state inferred when Rule column is populated alongside Permissions Added)
- What is **not** logged: share cancellations (inferable from block events); draft rule edits; UI navigation; native app opens of downloaded files
- Where to find PAR audit events: the organisation-level Audit Logs page (`/audits`); PAR events appear in the same log as all other platform events; filter by Operation type to isolate PAR-specific operations

---

### 📋 Target a Platform Governance Rule at specific user groups
**Audience:** Admins

**Topics to cover:**
- What group targeting in PAR does: instead of listing individual sender or recipient email addresses, a rule can reference a SpecterX **group** as a condition — any member of the group satisfies the condition
- How to reference a group in a rule condition: selecting the group from the **From** (sender) or **To** (recipient) field in the rule configuration form
- The "all external" and "all public domains" shorthand: a rule can target all senders or all recipients outside the organisation without listing individual addresses or groups
- How group evaluation works at rule-fire time: PAR evaluates rules **per recipient**; a group condition matches if any member of the group is a party to the share
- Block and group interaction: if a block rule targets a specific individual and that individual is a member of a group that also has an exception rule, the block takes priority over the exception for that individual when the individual is the defined recipient or the sender is the group member
- Exception rules and groups: when an exception rule references a group, PAR steps aside for all members of the group across all senders and recipient conditions specified in that rule
- Policy Assignment rules and groups: a Policy Assignment rule that targets a specific group as sender will fire whenever any member of that group initiates a share matching the other conditions
- Group membership visibility: SpecterX group membership is managed in the Users & Groups admin pane; Workspace permissions lists show the group name, not the individual members — audit logs record permission events by group name
- Known limitation: if a recipient belongs to a group where some members are missing required details (e.g. phone numbers for SMS verification), the entire group share is blocked until all required details are entered

---

### 📋 Understand default policies and policy availability
**Audience:** Admins

**Topics to cover:**
- The **tenant default policy**: every tenant must have a default policy; it is the fallback applied when no other policy is assigned and the pre-selected option in the share dialog; it cannot be restricted to specific users; it must remain available to all licensed internal users
- **Unrestricted policies**: available for manual selection by all licensed internal users
- **Restricted policies**: visible only to specifically assigned users or members of assigned SpecterX groups; other users do not see these policies in the share dialog or policy selector
- How to restrict a policy: enable the "Restrict Policy to Specific Users" toggle in the policy editor and assign users or groups
- Manual assignment vs system assignment:
  - **Manual**: users can only select policies they have been granted access to
  - **System**: Platform Governance Rules and Workspace parent policy inheritance can apply **any** policy to any share, regardless of whether the user has manual access to that policy
- Policy persistence after restriction changes: if a file has already been assigned a restricted policy (via PAR or Workspace), the assignment remains valid and the file continues to be governed by that policy — even if the user would not be permitted to manually select it; if the user changes away from the restricted policy, they cannot manually switch back
- Administrative restriction changes: making a previously unrestricted policy restricted does not break existing file assignments; users without access can no longer manually apply that policy to new shares
- Workspace policy inheritance and restricted policies: a Workspace parent policy may be a restricted policy; uploaders who are not authorised for that policy can still have it applied to their uploaded files through inheritance — the platform assigns it, not the user
- Implications for PAR: PAR-assigned policies are system assignments and bypass manual availability restrictions entirely; a rule can assign "Extremely Sensitive" to any user's share even if that user cannot manually select that policy

---

### 📋 How Rights Management (RMS) protection works

**Audience:** Admins, end users, compliance officers

**Topics to cover:**
- What SpecterX RMS protection does: embeds encryption and access controls directly into the file at the native format level (Microsoft Office and PDF), so protection persists wherever the file travels — email, cloud storage, or physical transfer
- How it differs from link-based protection: RMS protection is enforced in the file itself; a recipient who downloads the file must still authenticate before opening it in a local application
- Supported file types: .doc, .docm, .docx, .dot, .dotm, .dotx, .pdf, .pptm, .pptx, .xls, .xlsb, .xlsx, .xlsm, and the full family of Office Open XML formats (link to Supported file types reference in §11)
- Supported applications for viewing protected files: SpecterX Web Viewer; Google Docs; Microsoft 365 web; Microsoft Office 2013 and above (Word, Excel, PowerPoint, Visio); Microsoft Edge 80+; Adobe Reader DC (version 2019.021.20047 or later)
- Supported applications for **editing** protected files: Microsoft Office 2013 and above; Microsoft Edge 80+; Adobe Reader DC
- Permission roles enforced in downloaded copies:
  - **Viewer**: can view content; cannot copy, edit, print, or export
  - **Contributor / Co-Owner**: can edit, copy, save changes, and create a protected duplicate; cannot print or export
- Identity verification for locally opened files: recipients open the file with their existing Microsoft or Google account (the account that matches the shared email address); no SpecterX-specific credentials are needed; domain-wide access allows other users in the same authorised domain to open the file without an OTP
- What RMS protection does **not** prevent: printing is restricted but screenshots of the screen are not technically blocked; a determined user with physical access to the screen can still photograph or record the display
- Pre-requisite: enabling RMS encryption in SpecterX requires an active rights management configuration in the tenant (configured via Entra ID); contact your admin if the toggle is greyed out
- Known conflict — Workspace re-upload: if a file that is already RMS-encrypted is re-uploaded into a Workspace governed by an RMS policy, the upload will fail because the system attempts to re-encrypt an already-encrypted file; strip the prior encryption before re-uploading
- Known conflict — Workspace policy mismatch: if an RMS-protected file is uploaded into a non-RMS Workspace, the UI shows the Workspace policy but backend enforcement continues to apply the original RMS controls

**Related articles:** Protect downloaded files with Rights Management (RMS) · Rights Management (RMS) — requirements & limitations · Encrypt downloaded files with a password · What SpecterX does and does not protect

---

### 📋 Protect email message content

**Audience:** End users sending from Outlook or Gmail

**Topics to cover:**
- What "protect email message content" means: encrypting the email body and subject line in addition to attachments
- How to enable it in the Outlook Add-in (the "Protect Email Content" checkbox in the side panel)
- How to enable it in the Gmail Extension (the "Entire message" option in the SpecterX protection section)
- What the recipient sees: the email body appears in the SpecterX Secure Reader, not in their inbox
- Use cases: emails containing sensitive information in the body text (e.g. PHI, financial data)
- Known limitations: some email clients do not render the protection indicator correctly

---

## Section 8 — Manage your organisation

Audience: administrators and auditors.

---

### 📋 Manage users & groups

**Audience:** Administrators

**Topics to cover:**
- Opening the Users page (`/users-editor`) — two tabs: Users and Groups
- Adding a new user (individual invitation, or bulk via CSV)
- Assigning a role: Collaborators, Administrators, Auditors (link to User roles & permissions reference in §11)
- Editing a user's role after creation
- Removing a user (what happens to their shared files and workspaces)
- Creating and managing Groups (used with "Restrict Policy to Specific Users")
- The difference between internal users (in your SpecterX org) and external users (auto-provisioned recipients)
- Syncing users from your identity provider (link to Entra ID / Okta / Google Cloud Identity articles in §9)

---

### 📋 Review audit logs

**Topics to cover:**
- Opening Audit Logs (`/audits`)
- The audit log table: Operation, File Name, Affected users columns
- Filtering: by User, by Operation type, by File Name, by File ID
- Clearing filters
- Exporting to CSV (what additional columns appear in the CSV: Timestamp, File ID, IP address, Policy)

**Related articles:** Audit log event reference · Review usage dashboards · Track recipient activity & engagement

---

### 📋 Review usage dashboards

**Topics to cover:**
- Opening the Domains Dashboard (`/domains-dashboard`)
- The two donut charts: Shares per domain and Files sharing per domain
- The per-domain breakdown table: shares sent and files shared
- Interpreting patterns: normal vs anomalous sharing by domain
- Cross-reference to the Recipient Activity & Engagement dashboard for per-recipient drill-down

**Related articles:** Track recipient activity & engagement · Review audit logs

---

### 📋 Track recipient activity & engagement

**Audience:** Administrators, compliance officers

**Topics to cover:**
- The Recipient Activity & Engagement dashboard (distinct from the Domains Dashboard)
- Per-recipient drill-down: which recipients are actively engaging, which have not opened files
- Time-based views: activity over the past 7/30/90 days
- File-level activity: how many times a specific file has been opened
- Using recipient activity data for sales/legal follow-up (e.g. confirming a contract has been reviewed)
- Exporting recipient activity data
- The difference between the Recipient Activity dashboard and the Audit Log (dashboard = aggregated trends; audit log = individual events)

---

## Section 9 — Set up integrations

Audience: IT administrators and system integrators.

---

### Identity integration

#### 📋 Set up Entra ID authentication

**Audience:** IT admins

**Topics to cover:**
- Prerequisites: Microsoft Entra ID (formerly Azure AD) tenant; Global Admin or Application Admin role
- Registering the SpecterX app in Entra ID
- Configuring SAML 2.0 for SSO: Entity ID, Reply URL, SAML signing certificate
- Configuring SCIM for user provisioning (auto-creating and deactivating users in SpecterX when they are added or removed in Entra ID)
- Mapping Entra ID groups to SpecterX roles
- Testing the SSO flow
- Troubleshooting common errors (SAML assertion mismatch, SCIM provisioning failures)

---

#### 📋 Set up Okta authentication

**Audience:** IT admins

**Topics to cover:**
- Prerequisites: Okta org; admin access
- Creating a new SAML application in Okta for SpecterX
- Configuring the SSO settings in SpecterX to match the Okta app
- Optional: Okta SCIM provisioning for automated user sync
- Testing the login flow
- Common Okta-specific errors

---

#### 📋 Set up Google Cloud Identity

**Audience:** IT admins

**Topics to cover:**
- Prerequisites: Google Workspace or Google Cloud Identity account; Super Admin or Group Admin role
- Setting up Google as the SAML identity provider for SpecterX
- Configuring the SAML app in Google Admin Console
- Optional: SCIM provisioning via Google
- Testing the Google SSO flow
- Cross-reference: the Gmail Extension also requires Google authentication

---

### Storage integration

#### 📋 Connect Amazon S3 storage

**Audience:** IT admins

**Topics to cover:**
- What the S3 storage integration does: SpecterX stores encrypted file data in your S3 bucket instead of (or alongside) SpecterX-managed storage
- Prerequisites: AWS account; S3 bucket created; IAM role or access key with appropriate S3 permissions
- Configuring the S3 bucket in SpecterX Settings → Integrations
- The bucket naming and region requirements
- Encryption: how SpecterX encrypts data before writing to S3
- Testing the connection (uploading a test file)
- What happens if the S3 bucket is unreachable

---

#### 📋 Connect SharePoint storage

**Audience:** IT admins

**Topics to cover:**
- What SharePoint Storage integration does: SpecterX stores files in a dedicated SharePoint site/document library (different from the SharePoint Connector which does share-in-place)
- Prerequisites: SharePoint Online (Microsoft 365); admin access to authorise SpecterX
- Registering the SpecterX app in Azure / Entra ID with SharePoint API permissions
- Configuring the dedicated SharePoint site in SpecterX Settings
- Testing the connection
- Cross-reference: distinction between this and the SharePoint Connector (§6)

---

#### 📋 Connect Google Cloud Storage

**Audience:** IT admins

**Topics to cover:**
- What GCS storage integration does: SpecterX stores file data in a Google Cloud Storage bucket
- Prerequisites: GCP project; GCS bucket; Service Account with Storage Object Admin permissions
- Creating the Service Account and downloading the JSON key
- Configuring the GCS bucket in SpecterX Settings → Integrations
- Bucket region and storage class recommendations
- Testing the connection

---

### Security & classification integration

#### 📋 Configure DLP mailflow integration

**Audience:** IT admins / security engineers

**Topics to cover:**
- What the DLP Mailflow Integration does: SpecterX intercepts outbound email from your mail server (e.g. Exchange Online) and applies protection automatically based on DLP classification signals
- Supported mail protection scenarios: Microsoft Purview labels trigger SpecterX policies; custom DLP headers trigger SpecterX policies
- The two deployment modes: hosted (SpecterX cloud intercepts) and on-prem (via the SpecterX Gateway)
- Configuring the mail routing rule in Exchange Online / Google Workspace to forward through SpecterX
- Mapping DLP sensitivity labels to SpecterX policies
- Testing with a sample email

**Related articles:** Configure Platform Governance Rules · Map Microsoft Purview sensitivity labels to SpecterX policies · Route outbound email through SpecterX Mail Protection for Microsoft Purview

---

#### 📋 Configure DLP WebUI integration

**Audience:** IT admins / security engineers

**Topics to cover:**
- What DLP WebUI Integration does: integrates DLP classification into the SpecterX web interface so that files tagged by DLP automatically get protected
- Supported DLP products (Microsoft Purview, third-party products)
- Configuration: connecting the DLP API to SpecterX
- How automatic policy application works when a file is uploaded to SpecterX and classified by DLP
- Cross-reference to Governance Rules (§7) which can act on DLP classifications

---

#### 📋 Configure Opswat CDR integration

**Audience:** IT admins / security engineers

**Topics to cover:**
- What Opswat CDR (Content Disarm and Reconstruction) does: sanitises files to remove embedded macros, scripts, and active content before they are stored in SpecterX
- Prerequisites: Opswat MetaDefender appliance or cloud API key
- Configuring the CDR endpoint in SpecterX Settings → Integrations → Opswat
- What happens to a file after CDR: the sanitised copy is stored; the original is discarded
- Performance and size considerations
- Which file types support CDR (Office documents, PDFs)

---

#### 📋 Configure Microsoft Purview classification
**Audience:** IT admins / compliance officers

**Topics to cover:**
- What the Purview integration does: imports your organisation's Microsoft Purview sensitivity label taxonomy into SpecterX so that labels can be used as conditions in Platform Governance Rules; when a PAR rule matches on a sensitivity label, the rule assigns the corresponding SpecterX policy automatically
- Prerequisites: Microsoft 365 E3/E5 with Purview; SpecterX admin
- Connecting SpecterX to the Microsoft Purview classification pipeline
- Label-to-policy mapping: which Purview label maps to which SpecterX policy
- How the mapping works in the mailflow integration vs the WebUI integration
- Testing the label→policy mapping with a labelled document
- Updating the mapping when new Purview labels are created
- Prerequisites for label resolution: before SpecterX can resolve Purview label IDs to human-readable label names (required for policy matching and audit recording), an admin must **import the organisation's Purview Label Taxonomy** via SpecterX Settings → Classification & Governance → Microsoft Purview; without this import, sensitivity labels cannot be evaluated by PAR rules
- Three label ingestion paths — labels reach SpecterX in different ways depending on the flow:
  1. **Mail flow**: labels are read from email headers and attachment metadata during mail processing
  2. **Direct file upload**: labels are read from file-level metadata when SpecterX ingests the file
  3. **SharePoint Connector**: SharePoint provides the file metadata package (including labels) when the connector share flow initiates; SpecterX reads the label from this package
- Labels are optional and additive: if a file has no Purview label, SpecterX proceeds normally; the absence of a label cannot be used as a PAR condition; classification is only recorded and acted on when present
- Trust boundary: only labels originating from the integrated tenant are treated as authoritative for policy evaluation; labels embedded by external organisations are ignored
- Label capture is point-in-time: SpecterX captures the label at the moment of file metadata ingestion; subsequent label changes in Purview are not automatically reflected in SpecterX unless the file is re-ingested through a supported path
- Audit log recording: when a sensitivity label is present and captured, it is recorded with the share and enforcement record; this data is available via the Audit Logs API and Syslog integration; it is not displayed in the Audit Logs UI in V1

**Related articles:** Map Microsoft Purview sensitivity labels to SpecterX policies · Configure Platform Governance Rules · Configure DLP mailflow integration

---

### Connect to your organisation's mail flow

#### 📋 Set up Mail Protection for Exchange Online

**Audience:** IT admins / mail server admins

**Topics to cover:**
- What the Mail Protection Service does for Exchange Online: a SpecterX cloud service intercepts and protects outgoing mail
- The connector architecture: Exchange Online transport rule → SpecterX Mail Protection Service → delivery
- Creating the connector in Exchange Online Admin Center
- Configuring the SpecterX Mail Protection Service credentials in the SpecterX admin UI
- Policy assignment: how SpecterX decides which policy to apply (Governance Rules, DLP labels, default policy)
- TLS configuration and certificate requirements
- Testing with a sample outbound email
- Monitoring the mail protection flow

---

#### 📋 Set up Mail Protection for Google Workspace

**Audience:** IT admins

**Topics to cover:**
- The Google Workspace routing rule that forwards outbound mail through the SpecterX Mail Protection Service
- Gmail routing settings: creating the outbound content-compliance rule
- Configuring the SpecterX endpoint in Google Workspace Admin Console
- Policy assignment logic
- Testing and monitoring

---

#### 📋 Set up Mail Protection for Cisco SEG

**Audience:** IT admins / security architects

**Topics to cover:**
- Configuring Cisco Secure Email Gateway to route through the SpecterX Mail Protection Service
- The Cisco SEG content filter or custom header rule that triggers SpecterX
- Authentication between Cisco SEG and the SpecterX service
- Policy assignment
- Testing and monitoring log analysis

---

#### 📋 Route outbound email through SpecterX Mail Protection for Microsoft Purview
**Audience:** IT admins / compliance officers

**Topics to cover:**
- What this integration does: Microsoft Purview DLP policies identify emails containing sensitive data and redirect them to the SpecterX Mail Protection Cloud Service for protection — instead of quarantining or blocking the email
- How it differs from the standalone Mail Protection setup: this flow uses Purview's classification engine as the trigger; SpecterX acts as the protection and delivery layer
- Pre-requisites: Exchange Online with Microsoft Purview DLP configured; an existing DLP policy that tags sensitive information; a SpecterX tenant with the Mail Protection Service endpoint
- Configuration steps (overview — link to vendor docs for Purview-side steps):
  1. Create a SpecterX Mail Protection Service contact in Exchange Online PowerShell (`New-MailContact` with the SpecterX MPS external address)
  2. Edit the target DLP rule in Microsoft Purview → Actions section: add a **Set headers** action with `X-DLP-RULE: <Detection Name>` (maps to a SpecterX policy) and `X-SPX-MPS: <Your SpecterX tenant ID>`
  3. Add a **Redirect the message to specific users** action, selecting the SpecterX Mail Protection Service contact
  4. Save and activate the DLP rule
- What happens after configuration: emails matching the DLP rule are redirected to SpecterX; SpecterX protects the email and its attachments and delivers them to the external recipient; the quarantine action is replaced with SpecterX protection
- The `X-DLP-RULE` header value: this detection name is used by SpecterX to match the email to a specific SpecterX policy — it must correspond to a detection name you configure in SpecterX's DLP label-to-policy mapping
- Email message body: SpecterX protects the **attachments**; the message body itself is not blocked — only attachment access may be modified or restricted
- Repeat for each DLP rule: the configuration must be applied to each Purview DLP rule you want to integrate with SpecterX; rules not configured continue to use their existing Purview action (quarantine, block, etc.)
- Support contact: for configuration assistance, contact support@specterx.com

---

#### 📋 Map Microsoft Purview sensitivity labels to SpecterX policies
**Audience:** IT admins / compliance officers

**Topics to cover:**
- What label-to-policy mapping does: associates a Microsoft Purview sensitivity label with a specific SpecterX security policy so that SpecterX automatically applies the right level of protection when it detects a labelled file or email
- Pre-requisites: the Purview integration must be configured in SpecterX (Settings → Classification & Governance → Microsoft Purview) and connected; the Purview Label Taxonomy must be imported into SpecterX so label IDs can be resolved to display names
- How to import the Label Taxonomy: use the SpecterX Purview Configuration Tool (recommended) — a guided PowerShell script that connects to your Entra ID tenant, validates permissions, and generates the handoff JSON including label metadata; or configure manually via Azure App Registration (link to the Azure portal — this is third-party setup; SpecterX support can guide the handoff)
- Setting up the label mapping in SpecterX: navigate to Settings → Classification & Governance → Microsoft Purview → Label Mapping; select a Purview label name and assign the corresponding SpecterX policy
- Using label mappings in Platform Governance Rules: once labels are mapped, a PAR rule can reference a sensitivity label as a **Classification** condition; if the condition matches, the rule's policy assignment or block action is applied
- What happens when a labelled file is shared: SpecterX captures the label at the point of file metadata ingestion (upload, SharePoint share, or mailflow processing); the label is matched against PAR rules; if a rule references that label, the rule's action is applied; the label is recorded in the audit log
- What happens when no label is present: SpecterX does not require a label to proceed; shares without labels are evaluated against PAR rules that do not include a Classification condition; the absence of a label does not block sharing
- Label name resolution: SpecterX receives labels as Unique IDs from Purview; the imported taxonomy is required to resolve these to human-readable names for policy evaluation and audit display
- Keeping the taxonomy up to date: if your organisation adds new Purview labels, re-run the import step to include the new labels in SpecterX; existing mappings for unchanged labels are not affected

**Related articles:** Configure Microsoft Purview classification · Configure Platform Governance Rules · Route outbound email through SpecterX Mail Protection for Microsoft Purview

---

## Section 10 — Deploy on-premises

Audience: system integrators and IT admins deploying the SpecterX Gateway in a customer's own infrastructure.

---

### 📋 About the SpecterX Gateway

**Audience:** IT architects, integrators

**Topics to cover:**
- What the SpecterX Gateway is: a self-contained SpecterX service that runs on-premises (or in a private cloud), providing full SpecterX functionality without routing data through SpecterX's cloud
- Why organisations use the on-prem Gateway: data residency requirements, air-gapped environments, regulated industries
- The deployment model: the Gateway connects to the SpecterX cloud for licensing and policy sync, but file data stays on-premises
- High-level architecture diagram: users → on-prem Gateway → on-prem storage → SpecterX cloud (licensing only)
- What the Gateway does and does not include (mail protection, file sharing, viewer)
- Licensing requirements

---

### 📋 Check prerequisites for the SpecterX Gateway

**Audience:** IT admins

**Topics to cover:**
- Hardware requirements: CPU, RAM, disk
- Operating System: supported Linux distributions and Windows Server versions
- Network: ports that must be open (inbound and outbound), DNS requirements
- TLS certificate requirements
- Database requirements (if any)
- Connection to SpecterX cloud: what the Gateway must reach and on which ports
- Identity provider: must be configured before the Gateway is installed
- Storage: where file data will be stored (local disk, NAS, S3-compatible)

---

### 📋 Install the SpecterX Gateway

**Audience:** IT admins / integrators

**Topics to cover:**
- Downloading the Gateway installer (MSI for Windows, DEB/RPM for Linux, Docker image)
- Running the installer and following the prompts
- First-boot configuration wizard: entering the SpecterX tenant key, configuring the Gateway URL, setting up storage
- Connecting to the SpecterX cloud for licence activation
- Starting and stopping the Gateway service
- Verifying the installation (accessing the Gateway admin UI, checking the heartbeat)

---

### 📋 Configure the SpecterX Gateway after installation

**Audience:** IT admins

**Topics to cover:**
- The Gateway admin UI: overview of settings
- Connecting the Gateway to your identity provider (SSO for Gateway users)
- Configuring the mail protection endpoint (if using on-prem mail protection)
- Network proxy settings
- TLS certificate upload and renewal
- Enabling/disabling features on the Gateway (viewer, mail protection, API)
- Back-up and recovery configuration

---

### 📋 Set up the Gateway Storage Connector

**Audience:** IT admins

**Topics to cover:**
- What the Storage Connector does: routes file data through your on-premises storage instead of cloud storage
- Supported storage backends: local filesystem, SMB/NFS share, S3-compatible object storage, SharePoint
- Configuring the storage endpoint in the Gateway admin UI
- Authentication to the storage backend (credentials, IAM role)
- Testing write and read operations
- Storage quotas and monitoring

---

### 📋 Integrate the Gateway with Active Directory

**Audience:** IT admins in Windows-domain environments

**Topics to cover:**
- Using on-premises Active Directory as the identity provider for Gateway users (via LDAP or ADFS)
- Configuring the LDAP connection in the Gateway admin UI
- Mapping AD groups to SpecterX roles (Collaborators, Administrators, Auditors)
- User sync frequency
- Testing login with an AD account
- The difference between AD integration and Entra ID integration (cloud vs on-premises)

---

### 📋 SpecterX Gateway — reference & supported headers

**Audience:** IT admins, integrators

**Topics to cover:**
- Full reference of Gateway configuration file parameters
- Environment variables supported for containerised deployment
- Supported mail headers for the Mail Protection service (which headers trigger SpecterX policies, which are passed through)
- Log file locations and log level configuration
- REST API endpoints exposed by the Gateway (health check, metrics)
- Software Bill of Materials (SBOM) location
- Gateway version compatibility matrix with the SpecterX cloud service

---

## Section 11 — Reference & limitations

Audience: all users and admins. Purpose: canonical reference for supported formats, known limits, compliance, and release notes.

---

### Capability limits

#### 📋 Supported file types & browsers

**Audience:** All users (cross-linked from across the KB)

**Topics to cover:**
- File types that can be **uploaded and shared** via SpecterX (all common document, image, and archive formats)
- File types that support **in-browser viewing** in the SpecterX Viewer
- File types that support **watermarking** (PDF, DOCX, XLSX, PPTX — link to watermarking limitations article)
- File types that support **password encryption on download** (PDF, DOCX, XLSX, PPTX)
- File types that support **Rights Management (RMS) encryption** (link to RMS article)
- File types that support **digital signatures**
- Supported **web browsers** for the sender (Chrome, Firefox, Edge, Safari — versions)
- Supported **web browsers** for the recipient Secure Reader
- Mobile browser support

**Related articles:** Watermarking — supported formats & limitations · Password encryption — supported formats & limitations · Rights Management (RMS) — requirements & limitations · Digital Signature — supported formats & limitations

---

#### 📋 User roles & permissions reference
**Audience:** Admins, compliance officers

**Topics to cover:**
- Reference table of all three organisation-level roles and their capabilities:

| Capability | Collaborator | Administrator | Auditor |
|---|---|---|---|
| Upload and share files | ✅ | ✅ | ❌ |
| Create workspaces | ✅ | ✅ | ❌ |
| Manage policies | ❌ | ✅ | ❌ |
| Manage users | ❌ | ✅ | ❌ |
| View audit logs | ❌ | ✅ | ✅ |
| View Domains Dashboard | ❌ | ✅ | ✅ |
| Delete files | Own files only | All files | ❌ |

- How roles interact with workspace-level permissions (a Collaborator can be a Co-Owner inside a workspace)
- External users: what auto-provisioned recipients can and cannot do
- How to change a user's role (link to Manage users & groups)
- Workspace-level roles reference table:

| Capability | Owner | Co-Owner | Contributor | Viewer |
|---|---|---|---|---|
| Manage parent policy | ✅ | ✅ | ❌ | ❌ |
| View all audit logs | ✅ | ✅ | Own files only | ❌ |
| Delete any file | ✅ | ✅ | Own files only | ❌ |
| Add/change member roles | ✅ | ✅ | ❌ | ❌ |
| Upload files | ✅ | ✅ | ✅ | ❌ |
| View all files | ✅ | ✅ | ✅ | ✅ |
| Receive activity notifications | ✅ | ❌ | ❌ | ❌ |

- Workspace Co-Owner note: Co-Owners have the same management capabilities as Owners with one exception — Co-Owners do not receive workspace activity notifications (file uploaded, access attempt blocked, etc.)
- External users in Workspaces: external contributors are not billed by SpecterX; they can be assigned Viewer, Contributor, or Co-Owner roles within a workspace

---

#### 📋 Watermarking — supported formats & limitations

**Audience:** Admins

**Topics to cover:**
- Supported file types: PDF, DOCX, XLSX, PPTX (currently — same as DocSend's stated limitation)
- **Important callout:** Download-only files and URL uploads cannot be watermarked
- Watermarking applies to the SpecterX Viewer only; if the recipient downloads a file, the watermark appears only if RMS encryption is also enabled
- Dynamic watermark fields: email address, IP address, account name, date, time
- Position, rotation, font colour, transparency, tile options
- Size and character limits for watermark text
- Known limitations: very large PDFs may experience slower rendering with watermarks enabled; watermarks do not appear in printed output unless RMS is also enabled

---

#### 📋 Password encryption — supported formats & limitations

**Audience:** Admins

**Topics to cover:**
- Supported file types: .pdf, .docx, .xlsx, .pptx
- **Important callout:** Password encryption is not available when Block file download is enabled
- The encryption standard used (AES-256 or native Office encryption)
- Password length and complexity requirements (if any)
- What happens when a recipient opens a password-encrypted file in a viewer that does not support the encryption (e.g. a mobile PDF reader)
- Known limitation: .xlsx macros may be disabled after encryption

---

#### 📋 Rights Management (RMS) — requirements & limitations

**Audience:** Admins

**Topics to cover:**
- **Important callout:** RMS requires an active Azure RMS or Entra ID configuration in the SpecterX tenant — contact your admin if the toggle is greyed out
- Supported file types: .pdf, .docx, .xlsx, .pptx
- What the recipient needs to open an RMS file: the Microsoft RMS client (installed automatically with Office 365); a Microsoft account or Entra ID account
- RMS and non-Microsoft recipients: they can view the file in the SpecterX Viewer but cannot open it locally without the RMS client
- Copy, print, screenshot enforcement: these restrictions depend on the RMS policy, not SpecterX directly
- Known limitation: RMS-encrypted files cannot be re-encrypted with a different RMS key without being decrypted first
- RMS + Watermarking: watermarks are applied at the RMS layer and are visible in both the Viewer and downloaded copies

---

#### 📋 Block download — scope & limitations

**Audience:** Admins

**Topics to cover:**
- **Important callout:** Block download hides the download button in the SpecterX Viewer. It does not prevent browser-level "Save image as" on individual pages, and it does not prevent screen recording.
- What it does prevent: the one-click "Download file" action in the SpecterX Viewer
- Interaction with other settings: Block download and Encrypt with Password are mutually exclusive; Block download and RMS encryption can be combined
- Mobile behaviour: how Block download appears in the SpecterX Viewer on mobile browsers
- Known limitation: if the recipient opens the file in a third-party viewer (e.g. Office Online), the download button in that viewer is not controlled by SpecterX unless RMS is also enabled
- For full enforcement against downloading, the recommended combination is Block download + Watermark + RMS

---

#### 📋 Digital Signature — supported formats & limitations

**Audience:** Admins, end users

**Topics to cover:**
- Supported file types for digital signatures in SpecterX
- Known limitations: the number of signers, the complexity of signing fields
- The relationship between digital signatures and the SpecterX Viewer (can a recipient sign inside the Viewer?)
- Compliance: what standards the SpecterX digital signature meets (eIDAS, ESIGN, etc.)
- What happens to the signature if the file is modified after signing

---

#### 📋 Authentication methods reference

**Audience:** Admins

**Topics to cover:**
- Comparison table of the four verification methods:

| Method | How it works | When to use | Setup required |
|---|---|---|---|
| Email OTP | Code sent to recipient's inbox | General external sharing | None |
| Phone SMS | Code sent by SMS/call to registered number | High-sensitivity, when email alone is insufficient | Sender enters phone number at share time |
| Personal Secret | Password set by sender | High-sensitivity, controlled distribution | Sender sets password at share time |
| Google/Microsoft SSO | Recipient authenticates with their Google or Microsoft account | Internal or partner sharing with known accounts | Recipient has a Google or Microsoft account |

- Combining methods for MFA
- Countries where SMS may be unreliable (link to carrier information)
- How SSO counts as email verification (if the recipient authenticates with their Microsoft account, the email step is satisfied)

---

#### 📋 Policy controls reference

**Audience:** Admins, documentation writers

**Topics to cover:**
- Complete reference table of every toggle and option in the policy editor:

| Control | Section | Type | Default | Description |
|---|---|---|---|---|
| Restrict Policy to Specific Users | Policy Configuration | Toggle | Off | Limits who can apply this policy |
| Recipient Sharing Permissions | Access Control | Radio | Allow Anyone | Controls how recipients can forward |
| Email verification | Access Control | Toggle | Off | Requires email OTP |
| Phone verification | Access Control | Toggle | Off | Requires SMS/call OTP |
| Personal secret | Access Control | Toggle | Off | Requires a sender-defined passphrase |
| Acknowledge receipt | Access Control | Toggle | Off | Recipient must confirm identity before file opens |
| Protect and Track | Data Protection | Toggle | On (locked) | All access logged |
| Block file download | Data Protection | Toggle | Off | Hides download button |
| Encrypt with Password | Data Protection | Toggle | Off | Downloaded copies require a password |
| Encrypt with RMS | Data Protection | Toggle | Off | Azure RMS encryption on downloads |
| Watermark | Data Protection | Toggle | Off | Dynamic watermark in the Viewer |
| Language | Recipient Experience | Radio | English | Language for the Recipient Page |

- Which controls are mutually exclusive
- Which controls require a separate integration (RMS requires Azure RMS)

---

#### 📋 What SpecterX does and does not protect

**Audience:** All users, compliance teams, prospective customers

**Topics to cover:**
- **What SpecterX does protect:**
  - Files shared via the web platform (tracking, policy enforcement, revocation)
  - Email attachments and body text (via Outlook and Gmail connectors)
  - Files in Workspaces (access control, audit)
  - Files shared from Google Drive and SharePoint via the connectors (link-level protection)
  - Downloaded files (via RMS encryption, if enabled)
- **What SpecterX does NOT protect:**
  - Screenshots of the SpecterX Viewer (no screen-capture blocking; only watermarking deters this)
  - Files downloaded without RMS, after a recipient opens them in a local app
  - Data copied and pasted from the Viewer (unless RMS restricts copy)
  - Files the recipient already has outside of SpecterX
  - The metadata of shared files (file names are visible in audit logs but not classified)
- Clear "threat model" statement: SpecterX protects against accidental forwarding, unauthorised access, and exfiltration from the SpecterX surface; it does not protect against a determined insider who copies content manually

---

#### 📋 Audit log event reference
**Audience:** Admins, auditors, compliance officers

**Topics to cover:**
- Audit log structure: columns in every log entry — **Timestamp**, **Operation**, **File Name**, **Policy**, **Rule**, **App**, **User IP**, **File ID**
- Column behaviour notes: columns are often blank when not relevant; a single entry covers one file with potentially multiple recipients; entries are not grouped into "events" — each file action is a separate row
- The **Rule** column: populated only when a Platform Governance Rule evaluation resulted in an action, or when a policy is in a locked state due to a rule
- The **App** column: records the originating application when shares are created from a connector (e.g. "Slack", SharePoint); blank for WebUI shares
- Share-flow operation reference table:

| Operation | When logged | Key columns |
|---|---|---|
| Upload | File uploaded to share drawer or My Files | File Name, Policy (default), File ID |
| Recipient Added | Sender adds recipients and clicks Next (triggers PAR evaluation) | User, File, Affected Users, File ID |
| Share Evaluation Request | PAR evaluated the share (always logged) | User, File, Affected Users |
| Rules Suggest Block | Block rule fired and result shown to sender (WebUI new share only) | User, File, Affected Users (blocked), Rule |
| Exception Rule Triggered | Exception rule matched; no enforcement taken | User, File, Affected Users, Rule |
| Rule Suggests Policy | Policy Assignment rule matched; pre-send proposal (WebUI new share only) | User, File, Affected Users, Policy, Rule |
| Set Policy | User manually changed the policy from the default | User, File, Affected Users, Policy |
| Permissions Added | Access provisioned (final committed share state after PAR) | User, File, Affected Users, Policy, Rule (if PAR locked) |
| Permissions Removed | Access revoked | User, File |
| Policy Unlocked | PAR-locked policy became unlocked (rule deleted or conditions removed) | User, File |

- Share-flow events for email and SharePoint connectors use the same operations as WebUI flows, but PAR evaluation results appear as backend operations (no real-time UI presentation to sender)
- PAR configuration operation reference:

| Operation | When logged |
|---|---|
| Rule activated | Admin toggles a rule from Off to On |
| Rule republished | Admin edits and saves an active rule |
| Rule deactivated | Admin toggles a rule from On to Off |
| Rules reordered | Admin reorders Policy Assignment rules in the active ruleset |
- Events that are **not** logged: share cancellations (infer from block events), draft rule edits, UI navigation, native app opens of downloaded password-protected files
- Accessing audit data: the Audit Logs page (`/audits`) — filter by Operation, User, File Name, or File ID; export to CSV for the full column set; Purview sensitivity label data is available via the Audit Logs API and Syslog integration (not in the UI in V1)

**Related articles:** Review audit logs · Configure Platform Governance Rules · Understand Platform Governance Rule audit events

---

### Compliance

#### 📋 HIPAA compliance with SpecterX

**Audience:** Healthcare IT, compliance officers

**Topics to cover:**
- How SpecterX protects PHI: encryption in transit and at rest, access controls, audit logs
- The Business Associate Agreement (BAA): how to request one from SpecterX
- HIPAA-specific policy recommendations: phone verification + disable forwarding + watermark + audit logging
- The HIPAA-ready policy template in SpecterX
- How SpecterX supports the HIPAA Minimum Necessary principle
- Breach notification: how SpecterX audit logs support breach investigation
- Cross-reference: what SpecterX does NOT protect (screenshots, local copies after download without RMS)

---

#### 📋 GDPR & data residency

**Audience:** EU organisations, DPOs

**Topics to cover:**
- Where SpecterX stores data by default (cloud region)
- Data residency options: EU-hosted tenants, S3/GCS/SharePoint storage in a specific region
- Data subjects and the right to erasure: how to delete a user's data from SpecterX
- Data retention settings: how to configure automatic data deletion
- Processor vs Controller: SpecterX's role as a Data Processor; your organisation as the Controller
- The DPA (Data Processing Agreement): how to request one
- Cross-reference to the Storage integration articles for configuring an EU-based storage bucket

---

#### 📋 SOC 2 & security certifications

**Audience:** Security and procurement teams

**Topics to cover:**
- SpecterX's current SOC 2 Type II status
- How to request the SOC 2 report (NDA required)
- Other certifications held (ISO 27001, etc.)
- SpecterX's encryption standards (AES-256 at rest, TLS 1.2+ in transit)
- Third-party pen testing schedule
- Vulnerability disclosure process

---

### Release notes

#### 📋 Release notes — Outlook Add-in

Per-version change log for the Outlook Add-in (and Classic Add-in where applicable). Each entry: version number, release date, new features, bug fixes, known issues.

---

#### 📋 Release notes — Gmail Extension

Per-version change log for the SpecterX Gmail Extension (Chrome). Each entry: version number, release date, new features, bug fixes, known issues.

---

#### 📋 Release notes — SpecterX Web Platform

Per-version change log for the SpecterX web platform and API. Each entry: version/date, new features, changes, deprecations, known issues.

---

#### 📋 Release notes — SpecterX Gateway

Per-version change log for the SpecterX on-premises Gateway. Each entry: version number, release date, new features, compatibility notes, upgrade steps, known issues.

---

## Deferred until shipped

The entries below correspond to source documents reviewed during the V2 research pass that describe **unshipped, planned, or outdated** features. Each entry is excluded from the live article plan until the feature reaches General Availability. The candidate article title is the planned first article once it ships.

| Source doc (short name) | Why deferred | Candidate article title when shipped |
|---|---|---|
| PAR Future Versions record (V2+ PAR features) | Describes planned V2 PAR capabilities including email body encryption triggered by a rule, planned removal of test mode, and future PAR configuration auditing — none shipped in V1 | Configure email body encryption via a Platform Governance Rule |
| Outdated PRD — Lock Policies | Lock Policies described in older PRD; superseded by PAR policy-locking behaviour shipped in V1; separate "Lock Policies" product feature not shipped | Lock a policy so users cannot override it |
| Outdated PRD — Enforcement Across All Channels | Describes future state of PAR enforcement extended to Workspaces, Slack, and Salesforce — not shipped in V1 | Extend governance rules to Workspaces and Slack |
| Outdated PRD — Transport Rules for MPS | Older approach to Mail Protection Service via transport rules; superseded by current Mail Protection architecture | (No new article — covered by existing MPS setup articles once updated) |
| Outdated PRD — Policy Assignment Rules (original) | Superseded by V1 PAR PRD | (No new article — content absorbed into V1 articles) |
| Recipient Link Experience 3.0 (EPIC + PRD) | Planned redesign of the Recipient Page and Viewer UX — not yet shipped | Tour the redesigned SpecterX Recipient Page |
| Project Editing (editing planning docs) | File editing capability in the SpecterX platform is in planning; not shipped | Edit a protected file directly in SpecterX |
| PRD — Establishing Request Files as Independent Action | Current "Request Files" flow is tied to Workspace creation; this PRD describes decoupling it as a standalone action — planning stage | Request files without creating a workspace |
| PRD — Folder Permission Standardization | Proposes new permission model and UX for folders (the "Proposed" folder model doc); not yet shipped | Manage folder-level permissions |
| PRD — Upload Flow Planning | Redesigned file upload flow — planning stage | (Enhance existing share-a-file article when shipped) |
| PRD — Epic Lifecycle Management Q2 2026 | File lifecycle management enhancements planned for Q2 2026 | Manage file lifecycle and automatic expiry policies |
| UX & Permission Overhaul Planning notes | Broader platform UX redesign in planning | (Multiple existing articles will need updating when shipped) |
| File Lifecycle Management Progressive Story Planning | Roadmap planning for progressive lifecycle management | (Updates to existing file lifecycle articles when shipped) |
| PRD — SSO Multi-Tenant Access | Planned SSO capability for users who need to access multiple SpecterX tenants from a single login | Access multiple SpecterX tenants with single sign-on |
| PRD — Group Management through IDP Sync (current + future versions) | IDP-synced group management not yet shipped in V1 | Sync groups from your identity provider to SpecterX |
| Project — Notifications Sent via Customer Domain | Planned feature to send SpecterX notification emails from the customer's own domain — not yet shipped | Send SpecterX notifications from your organisation's email domain |
| Project — Off-boarding Tier 1 Support planning | Internal support transition planning — not a customer-facing article | (Internal only — no public KB article) |
| Workspaces 2.0 / Future Version record | Planned Workspaces redesign with additional capabilities — not yet shipped | (Updates to existing Workspace articles when shipped) |
| SharePoint Connector Future Versions record | Future SharePoint Connector capabilities (e.g. folder sharing, inbound to SharePoint) — not yet in V1 | Share a SharePoint folder with SpecterX protection |
| Slack Connector Future Versions record | Planned Slack enhancements (PAR integration, filename display in link, DM support) — not yet in V1 | Send a protected file in a Slack Direct Message |
| Audit Logs Future Versions (folder title of share-flow events doc) | The share-flow events doc is the current shipped state (V1); any future versions of audit log features are deferred | (Updates to the Audit log event reference article when shipped) |
| Track recipient activity in Outlook (planned feature) | In-Outlook activity tracking from the add-in side panel is not yet shipped in V1 | Track recipient activity directly from Outlook |
| PAR test mode (planned feature) | Rule testing via the PAR configuration console is not shipped in V1 | Test a Platform Governance Rule before activating it |
| Configure notifications (planned feature) | Notification configuration UI does not exist in V1 | Configure sender, recipient, and admin notifications |
| Request files from recipients (planned feature) | Request Files as a standalone action separate from Workspace creation is not yet shipped | Request files from recipients without creating a workspace |

---

*Last updated May 2026 · 112 articles across 11 sections*
