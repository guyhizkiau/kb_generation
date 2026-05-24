# SpecterX Knowledge Base — Article Plan

**101 articles across 11 sections** · 3 live (✅) · 98 planned (📋)

This document is the editorial plan for the SpecterX help center. Each article entry lists the title, audience, and the specific topics, questions, and tasks the article will cover. Articles marked ✅ are already written; articles marked 📋 are planned.

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

### 📋 Reset your password

**Audience:** All users

**Topics to cover:**
- How to trigger a password reset from the login page
- What the reset email looks like and where it comes from
- Link expiry: how long the reset link is valid
- What to do if you use SSO (password reset is managed by your identity provider, not SpecterX)
- What to do if you do not receive the reset email (spam, provisioning issues)
- Contacting your system administrator if self-service reset is disabled

---

### 📋 Supported file types & browsers

**Audience:** All users (also cross-linked from Reference section)

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

---

## Section 2 — Share files

Audience: end users who want to share a file or folder from the SpecterX web platform.

---

### ✅ Securely share a file from the SpecterX Web Platform *(POC article — live)*

**Topics covered:**
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

### 📋 Request files from recipients

**Audience:** End users, admins

**Topics to cover:**
- What "Request files" does: you generate a link that an external party uses to upload files into your SpecterX account
- When to use this (e.g. asking a client to return documents, collecting submissions)
- How to generate a request link from the web platform
- What the recipient sees: the upload page they land on after clicking the link
- Policy that applies to incoming files: what protection is applied to uploaded files
- Where uploaded files appear in your account (My Files or a Workspace)
- Link expiry and access control on request links
- The relationship to Workspaces: requesting files into a Workspace vs into My Files

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

### 📋 Set an expiration date on a shared file

**Audience:** End users, admins

**Topics to cover:**
- Where expiration is configured: in the security policy (Retention/Expiry setting) vs at share time
- How automatic expiry works: the link stops working after the configured period
- What the recipient sees after the link has expired
- The difference between expiry and revocation
- Whether expiry applies to already-downloaded copies
- How data retention policies (e.g. "1 day retention") relate to manual expiry

---

## Section 3 — Receive files

Audience: recipients — external parties who have received a protected link and need to open the file.

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

---

### 📋 Verify with a personal secret

**Audience:** Recipients

**Topics to cover:**
- What a "personal secret" is: a password or passphrase the sender set during the share
- Entering the personal secret on the Recipient Page
- What to do if the secret is wrong: contact the sender for the correct value
- The difference between a personal secret and the "encrypt downloaded files with a password" feature (the personal secret is for access; the download password is for the downloaded copy)

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

---

### 📋 Open with Microsoft Office (desktop)

**Audience:** Recipients

**Topics to cover:**
- Prerequisites: Microsoft 365 or Office installed; RMS client configured (for RMS-protected files)
- Downloading the file from the SpecterX Viewer and opening it in Office
- RMS-encrypted files: the Office IRM bar that appears, showing restrictions
- What restrictions apply (edit, copy, print, screenshot) depending on policy
- What to do if Office cannot decrypt an RMS file (Azure RMS client not configured, expired access)
- Supported file types: DOCX, XLSX, PPTX

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

---

### 📋 Send a file back to the sender

**Audience:** Recipients

**Topics to cover:**
- What "Send a file back" means: the recipient can upload a file to the sender's SpecterX using the return link in the notification email
- Finding the return link in the original notification email
- The upload flow: what the recipient sees, what file types are accepted
- Where the file appears in the sender's account
- Policy that applies to return files
- The difference between this and "Request files from recipients" (which the sender initiates)

---

## Section 4 — Manage workspaces

Audience: end users and collaborators who use SpecterX Workspaces for ongoing collaboration.

---

### 📋 Create and manage a workspace

**Audience:** End users (Collaborator or Admin)

**Topics to cover:**
- What a Workspace is: a secure, persistent collaboration space with a parent policy, folder structure, and shared access
- Creating a new workspace: name, parent policy, storage integration (if configured)
- The limitation that workspace names cannot be changed after creation
- Workspace settings: viewing the workspace's current parent policy, editing settings
- The sidebar tabs in a workspace: Files, Members, Policy, Audit
- The relationship between Workspaces and storage integrations (SharePoint, S3, GCS)
- Licensing requirement: Collaborator or Admin licence required to create a workspace

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

## Section 5 — Send protected email

Audience: users who send and receive protected email via the Outlook or Gmail connectors.

---

### 📋 Outlook Classic vs Outlook New — which should I use?

**Audience:** Users (and IT admins deciding which to deploy)

**Topics to cover:**
- **Outlook New Add-in**: works on Outlook for Web (OWA), Outlook for Desktop (Windows and Mac), and Outlook Mobile. Recommended for all new installations.
- **Outlook Classic Add-in**: Windows Outlook Desktop only. In maintenance mode — no new features are being added. Suitable only for organisations that cannot upgrade.
- Decision table: which scenarios require Classic vs which should use New
- How to check which version you have installed
- The conflict warning: if both are installed simultaneously, they will conflict — only one should be active
- How to migrate from Classic to New (uninstall Classic first)

---

### 📋 Get started with the SpecterX Outlook New Add-in

**Audience:** End users, IT admins

**Topics to cover:**
- What the Outlook New Add-in does: adds a SpecterX protection toggle to the Outlook compose window
- Platforms: Outlook for Web, Windows Desktop, Mac Desktop, and Outlook Mobile
- Links to all lifecycle articles: install, send, track, troubleshoot, uninstall
- Cross-reference to Outlook Classic disambiguation article
- Brief description of the recipient experience (what the person receiving the email sees)

---

### 📋 Set up the SpecterX Outlook New Add-in

**Audience:** IT admins (for org-wide deployment), individual users (for self-installation)

**Topics to cover:**
- Prerequisites: Microsoft 365 subscription; Outlook version requirements
- Admin deployment via Microsoft 365 Admin Center (recommended for org-wide rollout)
- Group Policy / Intune deployment options
- Individual self-installation from the Microsoft AppSource
- Activating the add-in after installation (the activation flow, authenticating to SpecterX)
- Verifying the add-in is active (the SpecterX button appears in Outlook compose)
- Installation in Outlook for Web (OWA)

---

### 📋 Send a protected email with the Outlook New Add-in

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

---

### 📋 Track recipient activity in Outlook

**Audience:** End users

**Topics to cover:**
- Where to view recipient activity for emails sent from Outlook (the SpecterX side panel, "Sent" view or the web platform)
- What activity is logged: open, download, forward, link click
- The timestamp and per-recipient view
- How to revoke access to a sent email from within Outlook
- Cross-reference to the Domains Dashboard / Audit Logs for organisation-level reporting

---

### 📋 Troubleshoot the Outlook New Add-in

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

### 📋 Uninstall the Outlook New Add-in

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
- ⚠️ Maintenance mode notice: this add-in is for Windows Desktop only and no new features are being added. New installations should use the Outlook New Add-in.
- What the Classic Add-in does vs the New Add-in
- Links to its lifecycle articles
- Recommendation to migrate to the New Add-in

---

### 📋 Set up the SpecterX Outlook Classic Add-in

**Audience:** IT admins (Windows organisations that cannot upgrade)

**Topics to cover:**
- Prerequisites: Windows, Outlook Desktop (specific minimum version)
- Downloading the MSI installer
- Group Policy deployment for org-wide rollout
- Individual installation (double-click the MSI)
- Post-install activation
- The conflict warning: do not install alongside the New Add-in

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

## Section 6 — Connect to other apps

Audience: users and admins who want to protect files in Google Drive, SharePoint, Slack, or Salesforce without moving them.

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
- What the SharePoint Connector is: share-in-place for SharePoint libraries (distinct from SharePoint Storage integration)
- Prerequisites: SharePoint Online (Microsoft 365); admin access to register SpecterX as an Azure App
- Registering the SpecterX app in Azure Active Directory / Entra ID
- Configuring the connector in SpecterX Settings → Integrations → SharePoint Connector
- Site and library scoping: configuring which SharePoint sites SpecterX can access
- Testing the connection

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

---

### 📋 Troubleshoot the SharePoint Connector

**Audience:** IT admins

**Topics to cover:**
- Azure App registration errors
- Insufficient scope (missing SharePoint API permissions)
- "File not found" errors when protecting a SharePoint file
- Token refresh failures

---

### 📋 Set up the Slack Connector

**Audience:** IT admins

**Topics to cover:**
- What the Slack Connector is: send SpecterX-protected file links directly to Slack channels or DMs
- Prerequisites: a Slack workspace; Slack admin access to install the SpecterX Slack App
- Installing the SpecterX App from the Slack App Directory
- Configuring the connector in SpecterX Settings → Integrations → Slack
- Authorising the OAuth connection
- Testing the connection (sending a test file to a Slack channel)

---

### 📋 Send a protected file to Slack

**Audience:** End users

**Topics to cover:**
- Sharing a file to Slack from the SpecterX web UI (the Slack icon in the share toolbar)
- Choosing a Slack channel or DM recipient
- The protected link that appears in the Slack message (not an attachment — a SpecterX link)
- Policy selection
- What the Slack recipient sees and how they access the file
- Revoking access to a Slack-shared file

---

### 📋 Troubleshoot the Slack Connector

**Audience:** IT admins

**Topics to cover:**
- App installation errors
- OAuth token expiry
- "Channel not found" errors
- The SpecterX Slack App was uninstalled and the connector needs to be re-authorised

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

## Section 7 — Configure security policies

Audience: administrators who create and manage security policies.

---

### ✅ Configure a security policy *(POC article — live)*

**Topics covered:**
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
- **From Outlook** (New Add-in): the policy selector in the SpecterX side panel
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

---

### 📋 Protect downloaded files with Rights Management (RMS)

**Audience:** Admins

**Topics to cover:**
- What Microsoft RMS encryption does: encrypts the file using Azure Rights Management so it can only be opened by authorised users, on authorised devices, with the RMS client
- Enabling the **Encrypt using Information Rights Management** toggle
- Prerequisites: an active Azure RMS / Entra ID configuration in the SpecterX tenant
- What the recipient needs to open an RMS-encrypted file: the Microsoft RMS client, a Microsoft account (or Entra ID account)
- Permission enforcement in RMS: copy, print, screenshot restrictions
- The difference between RMS encryption and password encryption
- When to use RMS: regulated industries where files may leave the SpecterX ecosystem
- Link to RMS requirements & limitations article in §11

---

### 📋 Apply a digital signature

**Audience:** End users, admins

**Topics to cover:**
- What the Digital Signature feature does in SpecterX (requesting signatures from recipients)
- How it differs from Watermarking (signature is an active agreement; watermark is a passive deterrent)
- Initiating a signature request: selecting the file, adding signers, defining signature fields
- The signer experience: what the recipient sees and how they sign
- After signing: where the signed document is stored, how the sender gets notified
- Supported file types for digital signatures
- Link to digital signature limitations article in §11

---

### 📋 Configure Platform Governance Rules

**Audience:** Admins

**Topics to cover:**
- What Platform Governance Rules are: organisation-wide automated rules that apply policies to files based on conditions (content type, classification label, sender group, destination domain)
- Rule structure: condition → action (apply policy X, block share, notify admin)
- Creating a rule in the SpecterX admin UI
- Rule priorities: when multiple rules match, which one applies
- Testing a rule before activating it
- The relationship between Governance Rules and DLP integrations (rules can be triggered by DLP classifications from Purview or a DLP mailflow integration)
- Common rule patterns: "If a file is labelled Confidential, apply HIPAA policy"; "If a file is shared to an external domain, require phone verification"

---

### 📋 Protect email message content

**Audience:** End users sending from Outlook or Gmail

**Topics to cover:**
- What "protect email message content" means: encrypting the email body and subject line in addition to attachments
- How to enable it in the Outlook New Add-in (the "Protect Email Content" checkbox in the side panel)
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

### ✅ Review audit logs & usage dashboards *(POC article — live)*

**Topics covered:**
- Opening Audit Logs (`/audits`)
- The audit log table: Operation, File Name, Affected users columns
- Filtering: by User, by Operation type, by File Name, by File ID
- Clearing filters
- Exporting to CSV (what additional columns appear in the CSV: Timestamp, File ID, IP address, Policy)
- Opening the Domains Dashboard (`/domains-dashboard`)
- The two donut charts: Shares per domain and Files sharing per domain
- The per-domain breakdown table: shares sent and files shared
- Interpreting patterns: normal vs anomalous sharing by domain

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

### 📋 Configure notifications

**Audience:** Administrators, end users

**Topics to cover:**
- Types of notifications SpecterX sends:
  - Sender notifications: when a recipient opens, downloads, or forwards a file
  - Admin notifications: policy violations, governance rule triggers
  - Recipient notifications: the original share email, reminder emails
- Where to configure notifications in the admin UI
- Per-user notification preferences
- Email notification templates: can they be customised?
- Configuring webhook or Slack notifications for security events

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
- What the Purview integration does: Microsoft Purview sensitivity labels trigger corresponding SpecterX policies automatically
- Prerequisites: Microsoft 365 E3/E5 with Purview; SpecterX admin
- Connecting SpecterX to the Microsoft Purview classification pipeline
- Label-to-policy mapping: which Purview label maps to which SpecterX policy
- How the mapping works in the mailflow integration vs the WebUI integration
- Testing the label→policy mapping with a labelled document
- Updating the mapping when new Purview labels are created

---

### Mail Protection service

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

See §1 "Get started" for the full content outline. The §11 version is the canonical reference; the §1 version links here.

---

#### 📋 User roles & permissions reference

**Audience:** Admins, compliance officers

**Topics to cover:**
- Reference table of all three roles and their capabilities:

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

Per-version change log for the Outlook New Add-in (and Classic Add-in where applicable). Each entry: version number, release date, new features, bug fixes, known issues.

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

*Generated from `kb/articles.json` · Last updated May 2026 · 101 articles planned*
