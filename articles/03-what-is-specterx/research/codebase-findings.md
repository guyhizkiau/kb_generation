# Codebase findings — What is SpecterX?

Sources scanned:
- `~/specterx-codebase/web-client/` (end-user React SPA — what senders and recipients see)
- `~/specterx-codebase/admin-web-client/` (admin / partner portal — what admins see)

Locale files: `web-client/src/content/general.json` (1,774 lines, single-file English) and `admin-web-client/client/src/i18n/config.ts` (812 lines, single-file English `resources`). There is no separate `en.json`; all canonical UI strings are in these two files.

## UI strings (canonical labels)

### Actors

- **Recipient** is the canonical UI term throughout. It appears in headings, role pickers, policy sections, and email subjects.
  - `web-client/src/content/general.json:190` → `"recipientPage"` (top-level namespace for the whole recipient flow)
  - `web-client/src/content/general.json:204` → `"{{sender}} shared a file with you"` (page heading / email subject)
  - `web-client/src/content/general.json:412` → `"recipientBlock"` and `"hiRecipient": "Hi {{recpEmail}}"`
  - `web-client/src/content/general.json:676` → policy section: `"otherSettings": "Recipient Experience"`
  - `web-client/src/content/general.json:685` → `"recipientSharing": "Recipient Sharing Permissions"`
  - `web-client/src/content/general.json:712` → `"recipientLanguage": "Recipient Language Preference"`
- **Sender** is the canonical word in user-facing copy but is NEVER a screen label — it appears only inside interpolated strings:
  - `web-client/src/content/general.json:204` → `"{{sender}} shared a file with you"`
  - `web-client/src/content/general.json:207` → `"From: {{sender}}"`
  - `web-client/src/content/general.json:330` → `"...keeps the sender's data secure."`
  - `web-client/src/content/general.json:376` → `"Please contact <1>{{senderEmail}}</1> to add your phone number..."`
  - `web-client/src/content/general.json:406` → `"Enter the password provided to you by the sender"`
  - `web-client/src/content/general.json:1254` → `"Encrypt files using a password set by the sender."`
  - Note: there is no sender-side persona label in the sender app. The web-client sidebar uses concrete object labels (My files, Shared with me, My workspaces) rather than calling the human a "sender."
- **Owner** is used as a near-synonym in some recipient-facing copy:
  - `web-client/src/content/general.json:311` → `"contact {{ownerEmail}} to request access"`
  - `web-client/src/content/general.json:312` → `"{{item}} owner"`
  - `web-client/src/content/general.json:249` → `"This hint was set by the file owner..."`

### "Policy" / security policy

- The canonical UI noun is **Policy** (and the section title **Policies**), not "security policy" or "access policy."
  - `web-client/src/content/general.json:614` → `"policyEditor": { "title": "Policies" }` (admin nav target)
  - `web-client/src/stores/AppStore/menuItems.ts:38` → sidebar entry `displayName: 'Policies'`
  - `admin-web-client/client/src/i18n/config.ts:34` → `policies: 'Policies'` (admin portal nav)
  - `admin-web-client/client/src/i18n/config.ts:248` → `policy: { policies: 'Policies', addPolicy: 'Add Policy' }`
- The phrase **"Security policy"** appears in exactly one recipient-facing pop-up:
  - `web-client/src/content/general.json:246` → `"policySettings": "Security policy for this file"` (the per-file info pop-up on the recipient page)
- The recipient-side actions block uses **"security policies"** in a generic explanation:
  - `web-client/src/content/general.json:320` → `"Due to conflicting security policies, this file is inaccessible"`
- During upload, the entry point is labelled **"Security Level"**, not policy:
  - `web-client/src/content/general.json:578` → `"title": "Set Security Level <1>(Optional)</1>"`
  - `web-client/src/content/general.json:1422` → file-info drawer field `"securityLevel": "Security Level"`
- Admin-side bucket labels for what a policy contains:
  - `admin-web-client/client/src/i18n/config.ts:432-436` → policy sections: `"Policy Configuration"`, `"Access Control"`, `"Data Protection"`, `"Recipient Experience"`
  - `web-client/src/content/general.json:673-676` → same four sections in the per-tenant policy editor

### "Recipient Page" / "SpecterX Viewer"

- Internally the file/folder is called `RecipientPage` (`web-client/src/components/MiniApps/RecipientPage/index.tsx:41`) but **the recipient never sees the words "Recipient Page" anywhere in the UI**. There is no tab title, heading, or breadcrumb labelled "Recipient Page." The page header instead shows the sender's name and the email subject (`recipientPage.greeting.subject`).
- The viewer's canonical product name is **"Secure Viewer"**, not "SpecterX Viewer":
  - `web-client/src/content/general.json:199` → recipient access button: `"viewer": "Secure Viewer"`
  - `web-client/src/content/general.json:1691` → browser-tab title: `"viewer": { "tabTitle": "Secure Viewer" }`
- However, the viewer is referenced as **"the SpecterX viewer"** in the recipient-side disclaimer:
  - `web-client/src/content/general.json:228` → `"While viewing files in the SpecterX viewer you can't copy or print it's content, as requested by the sharing organization."`
- The viewer button is just `"Viewer"` in admin / file-table contexts:
  - `web-client/src/content/general.json:1310` → context-menu: `"viewer": "Viewer"`
  - `web-client/src/content/general.json:1428` → info drawer button: `"viewer": "Viewer"`
- The action verbs the recipient sees:
  - `web-client/src/content/general.json:224` → `"openFilesSecurely": "Open file securely"`
  - `web-client/src/content/general.json:226` → `"viewFilesSecurely": "You are viewing securely"`

### "Workspace" / "Workspaces"

- Canonical singular = **Workspace**, plural = **workspaces** (lowercase plural is consistent in copy).
  - `web-client/src/content/general.json:93` → `"workspace": "Workspace"` (common noun)
  - `web-client/src/content/general.json:467` → `"titleWorkspace": "New workspace"`
  - `web-client/src/content/general.json:172` → `"noWorkspaces": "You haven't created any workspaces yet"`
  - `web-client/src/content/general.json:229` → recipient-side button: `"openWorkspacesSecurely": "Open workspace"`
- The sidebar nav uses **"My workspaces"** (lowercase `w`):
  - `web-client/src/stores/AppStore/menuItems.ts:26` → `displayName: 'My workspaces'`
  - `web-client/src/components/SideBar/SideBar.tsx:54` → same string, hard-coded
  - `web-client/src/components/SideBar/SidebarMenu/index.tsx:31` → menu item filtered by `ENABLE_WORKSPACE`
  - `web-client/src/components/SideBar/SidebarMenu/index.tsx:42` → `label: <strong>My workspaces</strong>`
- The sidebar trigger that opens the workspace creation drawer is labelled **"Request files"**:
  - `web-client/src/content/general.json:167` → `"requestFiles": "Request files"`
- There is no admin-portal vocabulary for "Workspace" — the concept is purely end-user.

### Email protection / Outlook / Gmail / "Protected email"

- **There is no Outlook integration and no Gmail integration in the codebase examined.** The two SPAs do not implement an email-protection feature.
  - The only "Outlook" string is a generic open-with target: `web-client/src/content/general.json:114` → `"outlook": "Outlook"` under `fileAccessApp` (alongside `googledrive`, `office365`, `viewer`, `salesforce`, `sharepoint`, `word`, `webdav`).
  - The only "Gmail" string in either app is an example placeholder: `admin-web-client/client/src/components/AppSidebar.tsx:242` → `"example_user@gmail.com"`.
  - The admin portal's integration catalog (`admin-web-client/client/src/data/integrations.ts:25-117`) lists exactly these integrations and no others:
    - Identity Provider: **Microsoft** (Entra ID / Azure AD), **Google** (Workspace), **Okta**
    - Storage: **Dedicated SharePoint Site**, **Google Cloud Storage**
    - Classification: **Microsoft Purview**
    - Connectors: **Slack**, **Salesforce**, **SharePoint Connector**
  - The admin `i18n/config.ts:497-512` settings page confirms the same list.
- The closest thing to "email protection" in the recipient UI is **encrypted email subject + body** for the recipient page, expressed as:
  - `web-client/src/content/general.json:206` → `"subjectEncrypted": "Subject of the e-mail is encrypted"`
  - `web-client/src/content/general.json:215` → `"messageEncrypted": "This message is encrypted."`
  - `web-client/src/content/general.json:1635` → sender-side toggle: `"encryptMessage": "Encrypt message"` + `"encryptMessageTooltip"` + `"allMessagesEncrypted": "All messages are encrypted in SpecterX"`
- The web-client AGENTS.md (`web-client/AGENTS.md:126`) does claim "integrations with Microsoft 365, Google Drive, Box, SharePoint, and Outlook" as a high-level product description, but no Outlook code path exists in this repo. See the contradiction section below.

### Verification step labels

- The recipient verification flow uses the namespace `recipientPage.OTPSteps` (`web-client/src/content/general.json:353-409`). Canonical labels:
  - `web-client/src/content/general.json:354` → `"enterEmailTitle": "Enter your email address"`
  - `web-client/src/content/general.json:355` → `"enterEmailDescription": "Enter the email address where you received the attachment. We'll send a verification code to confirm your email."`
  - `web-client/src/content/general.json:358` → button: `"sendCode": "Send code"`
  - `web-client/src/content/general.json:360` → `"verifyEmail": "Verify email"`
  - `web-client/src/content/general.json:361` → `"verifyPhone": "Verify phone"`
  - `web-client/src/content/general.json:362` → `"checkEmail": "Check your email"`
  - `web-client/src/content/general.json:363` → `"checkPhone": "Check your phone"`
  - `web-client/src/content/general.json:364` → `"willSendCodeTo": "We'll send 6-digit code to"`
  - `web-client/src/content/general.json:365` → `"enterCode": "Enter the 6-digit code below, which we've sent to <1>{{recipientEmail}}</1>"`
  - `web-client/src/content/general.json:408` → submit: `"verifyButtonText": "Verify"`
- Policy-level verification setting names (admin-controlled, recipient sees the effect):
  - `web-client/src/content/general.json:1196-1198` → `"requireEmailVerification": { "title": "Verify email", "explain": "A one-time code will be sent to the recipient's email number for verification." }` (the word "number" here is a known typo for "address")
  - `web-client/src/content/general.json:1192-1194` → `"requirePhoneVerification": { "title": "Verify phone number", "explain": "A one-time code will be sent to the recipient's phone for verification." }`
  - `web-client/src/content/general.json:1257-1259` → `"requirePasswordVerification": { "title": "Verify personal secret", "explain": "Recipients must enter a personal secret to access the data." }`
- Admin-portal policy section header for these settings: `admin-web-client/client/src/i18n/config.ts:442-443` → `"verification": "Verification Requirements"`, `"verificationDesc": "Select how recipients will verify their identity before accessing data."`

## Feature flags affecting this article

Feature toggles in the web-client are stage-based (per-tenant), defined in `web-client/src/config/env.ts` as fields on the `EnvConfig` interface, not Flagsmith flags. The relevant toggles:

- **`ENABLE_WORKSPACE`** (`web-client/src/config/env.ts:68`) — gates the entire Workspaces feature. **Default behaviour: OFF** — Workspaces only appears when the per-tenant config explicitly sets it.
  - Tenants with `ENABLE_WORKSPACE: true`: meuhedet (`env.ts:397`), amitim (`env.ts:509`), mvs (`env.ts:542`), one more around `env.ts:1078`
  - Tenants with explicit `ENABLE_WORKSPACE: false`: migdal (`env.ts:287`), two more around `env.ts:935, 955`
  - All other tenants (the majority, including base `prod` and `local`) leave it unset → falsy → Workspaces hidden
  - Sites it gates: sidebar item "My workspaces" (`SidebarMenu/index.tsx:31`), `WorkspacesPage` route, `WorkspaceDrawer` (`App.tsx:117-220`), the "Request files" sidebar button, and the workspaces fetch on app boot.
- **`ENABLE_SHARE_MESSAGE`** (`env.ts:75`) — gates the "Encrypt message" toggle on the share dialog (the closest thing to email/message protection). Enabled in staging (`env.ts:211`) and amitim (`env.ts:512`); off elsewhere.
- **`ENABLE_OPSWAT_FILE_SCANNING`** (`env.ts:72`) — gates the file-scan UI on upload. Dev only (`env.ts:167`).
- **`SHOW_SHARE_BACK_BUTTON`** (`env.ts:74`) — gates the recipient-page "Share a file back" button (dev / amitim / mvs only).
- **`ENABLE_IP_RESTRICTION`** (`env.ts:69`) — gates admin IP-restriction UI for several tenants.
- **`AUTOMATIC_OTP`** (`env.ts:89`) — defaults true; when false, the recipient must click "Get Code" rather than the OTP being auto-sent on page load. Set to `false` only for fireblocks and bulwarx.
- **`USE_SIMPLIFIED_PASSWORD_PROMPT`** (`env.ts:81`) — swaps in the simpler password prompt copy at `recipientPage.OTPSteps.simplifiedPasswordPrompt`.
- **No client-side feature flag exists for "Digital Signature."** The viewer has a `lock signatures` action (`general.json:1712-1717`) but it is always present in the viewer code; nothing gates it.
- **No client-side feature flag exists for "Outlook integration" or "Gmail integration"** because no such integration exists in either codebase. (The platform-level `AGENTS.md:200` does say feature flags are managed by **Flagsmith** at the backend, but no Flagsmith key is referenced from web-client or admin-web-client.)

## Recipient-side product references

The recipient (the person who clicks a share link without a SpecterX account) sees the product named in these specific places:

- Browser tab title on the viewer: `"Secure Viewer"` (`general.json:1691`)
- Recipient-page disclaimer when viewing inline: `"While viewing files in the SpecterX viewer you can't copy or print it's content, as requested by the sharing organization."` (`general.json:228`)
- Recipient-page error: `"SpecterX files are protected and may require additional authentication in your local software"` (`general.json:282`)
- Public footer (visible on the recipient page): `"Drop us a message at <1>{{email}}</1> or visit our website <3>www.specterx.com</3>"` (`general.json:186`)
- Email subject template: `"{{sender}} shared a file with you"` / `"...shared files with you"` (`general.json:204-205`)
- The `from` line: `"From: {{sender}}"` (`general.json:207`)
- Encrypted-message banner: `"All messages are encrypted in SpecterX"` (`general.json:1636`)
- Confidentiality notice on download: `"Confidentiality Notice"` + a generic legal blurb (`general.json:1732-1733`)
- Network-restriction error message: `"This file is protected by <1/>."` — `<1/>` is replaced by the SpecterX product logo (`general.json:336`)

The recipient page does **not** have a branded "Welcome to SpecterX" banner. The only "Welcome to SpecterX" string is on the sign-in / sign-up pages, which the recipient never sees unless they choose to log in:

- `general.json:1064` → sign-in pageTitle: `"Welcome to SpecterX"`
- `general.json:1081` → sign-up pageTitle: `"Welcome to SpecterX!"`
- `general.json:152-153` → "become licensed user" CTA inside the recipient page: title `"Start working with SpecterX"`, subtitle `"Manage, control and protect your data anywhere it travels.\nYour Data. Your Rules. Anywhere."` — this is the closest thing the product has to a one-line tagline.

## Adjacent flows worth knowing about

- **Verification methods are configured per policy, not per share.** A single policy can require any combination of email OTP, phone OTP, or "personal secret" (a sender-set password). Locations: `general.json:1188-1259` and `admin-web-client/client/src/i18n/config.ts:328-423`. The "personal secret" wording is unique to SpecterX and worth flagging in the article.
- **Recipient Sharing Permissions** (forwarding) — three options visible to the recipient indirectly: `"withAnyone": "Allow Sharing with Anyone"`, `"onlyInTheirDomain": "Restrict Sharing to Recipient's Domain"`, `"withNoOne": "Disable Further Sharing"` (`general.json:1183-1185`).
- **Policy Assignment Rules** — automated policy assignment by attributes is called "Platform Governance Rules" in the admin portal (`admin-web-client/client/src/i18n/config.ts:133`) and "Policy Assignment Rules" inside the rules sidebar (`config.ts:158`). The user-facing summary line: `"Platform Governance Rules automatically govern how files are shared in SpecterX."` (`config.ts:150`).
- **Three user roles in a share** — `viewer` ("Viewer / Can view content"), `editor` ("Contributor / Can edit content"), `coOwner` ("Co-owner / Can share content and read associated logs") (`general.json:1590-1626`). Note: the API key is `editor` but the UI label is **Contributor**.
- **Five Cognito groups** — `Externals, Auditors, Collaborators, Administrators, Viewers` (`general.json:119-125`). These are admin-side roles, not share roles.
- **Send-back flow** — recipients with permission can upload a file back through `"sendBack"` (`general.json:1757-1773`). Gated by `SHOW_SHARE_BACK_BUTTON`.
- **Become-licensed-user flow** — a recipient can be upsold into a licensed account from inside the recipient page (`becomeLicensedUserModal`, `general.json:151-156`).

## Anything that contradicts the plan entry

Based on the actor / use-case / integration framing the article plan implies:

- **"Outlook / Gmail email protection" use case is NOT in the product UI.** The plan's third use case appears to assume native Outlook and Gmail integrations. Evidence:
  - No Outlook component, route, locale namespace, or admin integration card exists in either codebase. The only "Outlook" string is a passive open-with target name (`general.json:114`).
  - The admin integration catalog (`integrations.ts:25-117`) is exhaustive — IdP, Storage, Classification, Connectors — and contains zero email-client integrations.
  - The "encrypt message" toggle on share + the encrypted recipient-page email view are SpecterX's own in-app email-like surface, served via the share link. That is the closest thing the product has to "protected email."
  - The web-client AGENTS.md narrative paragraph (`web-client/AGENTS.md:126`) does claim Outlook integration exists, but no code backs it up in this repo. If Outlook/Gmail add-ins exist, they live in a separate repository not scanned here. The article must either drop the use case, hedge it ("Outlook and Gmail add-ins are sold separately / not yet GA"), or be cross-checked with Guy.
- **"SpecterX Viewer" is not the canonical product name.** The viewer is called **Secure Viewer** in the recipient-facing tab title and access button. The phrase "SpecterX viewer" only appears once, lowercase-v, inside a disclaimer sentence (`general.json:228`). Article should use "Secure Viewer" as the canonical proper-noun product name and reserve "SpecterX viewer" for descriptive prose.
- **"Recipient Page" is internal jargon.** It is the React component name (`RecipientPage/index.tsx`) and i18n namespace (`recipientPage`), but it has no visible label, tab title, or heading the recipient sees. Article must either describe it functionally ("the page recipients land on after clicking a share link") or call it the **share link page**, but not present "Recipient Page" as a UI proper noun.
- **"Security policy" is not the canonical noun.** The product calls it **Policy** (admin nav, file table column, settings drawer), **Security Level** (on upload), or **security policy** (lowercase, once, in the per-file pop-up). The article should use "policy" as the primary term and footnote "security policy" / "security level" as synonyms.
- **The actor model is sender ↔ recipient, but only "recipient" is a UI label.** The sender side calls itself nothing — there is no "Sender Dashboard" or "Sender" persona label. The sender just uses My files / Shared with me / My workspaces. If the article frames the two-actor model, it should make clear that "sender" is descriptive, not a UI surface.
- **Workspaces is per-tenant opt-in, not a generally available feature.** With `ENABLE_WORKSPACE` defaulting to off in the base `prod` and `local` configs and explicitly off for tenants like migdal, the feature is **not** universally visible. The article must include a "available in your tenant when enabled" caveat or describe Workspaces under a feature-availability note.
- **No "Digital Signature" feature flag exists in the client.** The viewer has a `lock signatures` UI affordance but nothing in the client gates a "digital signature" capability. If the plan promises a Digital Signature module, it's either a server-side / Flagsmith concern (`AGENTS.md:200` mentions Flagsmith but no key is referenced in the SPAs) or a separate product line. Worth checking with Guy.
- **Identity provider integrations are Microsoft Entra ID / Google Workspace / Okta** (`integrations.ts:25-55`) — phrased as SSO, not generic "identity" linking. Storage integrations are **Dedicated SharePoint Site** and **Google Cloud Storage** (note GCS is the canonical naming, not "Google Drive" — Google Drive appears only as a runtime open-with target, `general.json:108`). The article should not call SharePoint a storage "connector" — `SharePoint Connector` is a distinct, separate integration (`integrations.ts:107-116`).

## Recently modified (last 90 days)

Both repos are active. Notable changes affecting article topics:

- **web-client** — last 90 days touched (`git log --since="90 days ago" --name-only`):
  - `src/components/MiniApps/RecipientPage/**` (multiple files including `RecipientPageContent.tsx`, `LinkView/index.tsx`, `MessageView/EmailViewer/HTMLEmailWrapper/HTMLEmailWrapper.tsx`, `FilesCarousel/FileView/ErrorView/index.tsx`, the index, the scss module)
  - `src/components/MiniApps/Common/OTPAuthSteps/index.tsx` and `waitForHumanInteraction.ts` (verification flow tweaks)
  - `src/components/MiniApps/Common/ErrorResult/NetworkRestrictionExplain/` (new component — corporate-network-block error UX)
  - `src/content/general.json` and `general_hebrew.json` (locale updates — the OTP and verification strings are recent)
  - Recent commits include `SPX-5995 - AIP files on Iphone` (2026-05-22), `SPX-6014: remove sign up option from logic page` (2026-05-21 — so the sign-up flow may be hidden in some tenants), `SPX-5994 - UI Issues Part 2` (2026-05-21), and `SPX-5976 - content overlap` (2026-05-20).
- **admin-web-client** — last 90 days:
  - The entire repo is recent — the admin portal as it stands today (post-rewrite) has been built up in this window. Notably `client/src/components/AppSidebar.tsx`, the i18n config, `data/integrations.ts`, audit logs (`AuditsFilters.tsx`, `AuditsTable.tsx`, `auditConstants.ts`), the policies editor (`Policies.tsx`, `PolicyRules.tsx`), and the settings/integrations page (`Settings.tsx`) were all touched.
  - Recent commits include `fix(ci): use shared resolveBranchProps()` (2026-05-17) and several version bumps through 2026-05-05 to 2026-05-17. The functional admin portal is younger than 90 days.

In short: the recipient flow has been heavily refactored very recently — any screenshot or string in the article should be taken from the current main branch, not memory.
