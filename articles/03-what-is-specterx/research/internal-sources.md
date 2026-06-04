# Internal sources — What is SpecterX?

## What was searched

- `references/internal/` — **does not exist** at the path given in the
  prompt (`/home/ubuntu/kb_generation/references/internal/`). The
  `references/` tree only contains `competitors/`. No internal-source
  files live there. (Earlier articles' internal-sources.md notes
  document this gap: "`references/internal/` — confirmed empty.")
- `product/COMPONENT_TAXONOMY.md` — the canonical component taxonomy.
- `product/components-inventory.txt` — the flat inventory list.
- `component-records/` recursively — all sub-folders. Most artefacts are
  `.docx`/`.xlsx` (PRDs, EPICs, customer-facing exports) and could not
  be parsed inline. Folder structure and naming were used as evidence.
- `editorial/ARTICLES_PLAN.md` — authoritative editorial outline, which
  encodes the product team's canonical language for every component.
- `editorial/PUBLIC_KB_SCOPE.md` — KB scope rules.
- `canon/GLOSSARY.md`, `canon/DO_NOT_DOCUMENT.md`,
  `canon/COMPETITOR_PATTERNS.md` — canonical writing rules.
- `legacy-manuals/` — historical `.docx` user/operator manuals; folder
  layout used as evidence of which capabilities exist.

---

## Source: product/COMPONENT_TAXONOMY.md

**Provenance:** `product/COMPONENT_TAXONOMY.md`, lines 1–217
**Relevance:** The single canonical naming document for every SpecterX
component. Defines every umbrella term used in the article (Storage
Integration, Identity Integration, Mailflow Integration, Connector,
Share-in-Place Connector, SpecterX Viewer, Policy Protection, On-Prem
Gateway).

Key facts:
- SpecterX components are grouped under named umbrellas; each umbrella
  has a one-line "decision test" (lines 94–172). Component names are
  written as `<Umbrella> / <Component Name>` (line 19).
- **Storage Integration** sub-components: Amazon S3 Storage, SharePoint
  Storage, Google Cloud Storage (lines 27–31).
- **Identity Integration** sub-components: Okta Identity, Entra ID,
  Google Cloud Identity (lines 33–37). Defined as "silent
  admin-configured plumbing … if removed, things just silently get
  worse (no SSO, no DLP scanning, no classification labels)"
  (lines 100–103).
- **Mailflow Integration** sub-components: Outlook Classic Add-in,
  Outlook New Add-in, Gmail Browser Extension, Mail Protection Server
  (lines 52–57). Edge case note: users *do* see its effects (sharing
  flow inside Outlook), but the integration itself is admin-configured
  plumbing (line 104).
- **Share-in-Place Connector**: a Connector "where the user shares a
  file that *stays in its original storage location* — SpecterX adds
  protection and access control without moving or copying the file out"
  (lines 114–119). Sub-components: Google Drive Connector, SharePoint
  Connector (line 61–62).
- **SpecterX Viewer** is the umbrella; sub-components are SpecterX
  Office Viewer, SpecterX PDF Viewer, SpecterX WOPI Host (lines 73–77).
- **Policy Protection** is "a file-level security measure that admins
  enable through the policy management UI, applied automatically to
  files governed by that policy" (lines 160–166). Examples: Watermarking,
  Password, Rights Management.
- **Digital Signature** is explicitly NOT a Policy Protection —
  "Digital Signature is a standalone capability — users sign documents,
  it's not a toggle an admin turns on for a policy" (line 166).
  This is the canonical answer to "SpecterX is not a signature platform
  (except via the Digital Signature feature)".
- **On-Prem Gateway** is a separate deployment umbrella (lines 86–90,
  168–172) — SpecterX otherwise runs in SpecterX's cloud.

---

## Source: product/components-inventory.txt

**Provenance:** `product/components-inventory.txt`, lines 1–103
**Relevance:** Flat, alphabetical inventory list of every SpecterX
product component — confirms the article's first-class entities
(Workspaces, Recipient Page, Security Policies, etc.) by name.

Key facts:
- Line 81: **Security Policies** is a top-level component (canonical
  term for what the article calls "security policy").
- Line 73: **Recipient Page** is a top-level component (canonical term
  for what the recipient lands on).
- Line 103: **Workspaces** is a top-level component.
- Line 67: **Protected Messages** is a top-level component (the email
  protection product).
- Line 9: **Digital Signature** is a top-level component (standalone,
  not a Policy Protection — consistent with COMPONENT_TAXONOMY line 166).
- Lines 57, 59: **Outlook Classic Connector** and **Outlook New
  Connector** are both first-class. (Note the inventory uses
  "Connector"; the taxonomy uses "Add-in" — both are in use; the article
  should use whichever appears in the surface UI it depicts.)
- Line 25: **Gmail Connector** is the canonical inventory name (the
  taxonomy file in line 56 calls it "Gmail Browser Extension"; both are
  the same thing, see Extension/Add-in/Plugin table at taxonomy
  lines 127–138).
- Line 33: **Mail Protection Server** — the backend that intercepts
  outbound email. Line 37: **Mail Protection Service** is the SpecterX-
  hosted version.
- Lines 7, 41: **Authentication** and **Okta Identity Integration** are
  separate inventory entries — Authentication is the SpecterX surface;
  Okta/Entra/Google are the IdP integrations behind it.

---

## Source: editorial/ARTICLES_PLAN.md (the article 03 plan entry)

**Provenance:** `editorial/ARTICLES_PLAN.md`, lines 15–26
**Relevance:** This is the editorial brief for the article itself. It
fixes the canonical scope: the two actors, the three use cases, what a
security policy controls, what SpecterX is NOT, and the relationship to
identity / storage / email infrastructure.

Key facts:
- The two core actors are the **sender** (who shares) and the
  **recipient** (who receives a protected link) — line 21.
- The three main use cases are: (1) share a protected file from the
  web, (2) protect email and attachments from Outlook or Gmail,
  (3) collaborate securely in a Workspace — line 22.
- A "security policy" = "the controls that govern how a file can be
  accessed (verification, forwarding, download, expiry)" — line 23.
- The recipient experiences three named surfaces: the **Recipient
  Page**, the **SpecterX Viewer**, and **verification steps** — line 24.
- SpecterX is explicitly NOT: a storage product; a service that moves
  your files; a signature platform — except via the standalone Digital
  Signature feature — line 25.
- SpecterX relates to identity provider, storage, and email
  infrastructure as upstream/downstream systems — line 26.

---

## Source: editorial/ARTICLES_PLAN.md — Section 2 (Share files)

**Provenance:** `editorial/ARTICLES_PLAN.md`, lines 59–164
**Relevance:** Canonical language for the web-share use case (use case
#1) and the meaning of "policy" at share time.

Key facts:
- The Share files flow is "upload → Add recipients → Select Policy →
  Share" (line 68).
- Recipient permission levels are three: **Viewer**, **Contributor**,
  **Co-Owner** (line 69).
- "Selecting a security policy from the dropdown" (line 70) — i.e. the
  policy is chosen *per share* from a pre-defined set, not authored
  per share.
- The **Share & Permissions Drawer** is the canonical name of the
  post-share access-management UI (lines 74, 116). Within it the
  policy field is called the **Parent policy** (line 120).
- Revocation is a first-class concept distinct from removing a single
  recipient (lines 130–135). Expiry is configured "in the security
  policy (Retention setting — expressed as a number of days)"
  (line 144) — confirming expiry as a policy control, not a
  per-share field.

---

## Source: editorial/ARTICLES_PLAN.md — Section 3 (Receive files)

**Provenance:** `editorial/ARTICLES_PLAN.md`, lines 167–367
**Relevance:** Canonical language for the recipient experience —
Recipient Page, verification, SpecterX Viewer.

Key facts:
- The **Recipient Page** = "the landing page a recipient sees after
  clicking a protected SpecterX link" (line 178). Layout: identity
  selection area, verification step, file preview summary, action
  buttons (line 179).
- Three verification methods are named: **email OTP** (default), **SMS
  /phone OTP**, **personal secret** (lines 180–181, 200, 211–237).
  Email OTP is the default.
- The **SpecterX Viewer** = "a browser-based document viewer that opens
  a protected file in the browser … requires no plugins or software
  installation for supported file types" (lines 359–360). Watermarking
  is dynamic and only displayed when the sender's policy enables it
  (line 362).
- The Viewer has "Open with…" hand-offs to external apps (Adobe
  Desktop, Microsoft Edge, Office Online, Native Office, Google
  Drive) — lines 258–336. These are **External Open-With** in the
  taxonomy (taxonomy lines 147–152): the file leaves SpecterX's
  rendering context.
- Send a file back is a recipient action; the recipient uploads a file
  to the sender via a return link in the notification email (lines
  339–351).

---

## Source: editorial/ARTICLES_PLAN.md — Section 4 (Workspaces)

**Provenance:** `editorial/ARTICLES_PLAN.md`, lines 370–476
**Relevance:** Canonical definition of a Workspace (use case #3).

Key facts:
- A **Workspace** = "a secure, persistent collaboration space with a
  parent policy, folder structure, and shared access" (line 380).
- Workspace creation parameters: name, parent policy, storage
  integration (line 381). Workspace names cannot be changed after
  creation (line 382).
- Workspace sidebar tabs: **Files, Members, Policy, Audit** (line 384).
- Workspace roles: **Owner**, **Co-Owner**, **Contributor**, **Viewer**
  (lines 409–412).
- Storage routing: workspace files are stored in SpecterX-managed
  storage by default; if an admin has configured a Storage Integration,
  files are stored in the org's Amazon S3 bucket, SharePoint site, or
  Google Cloud Storage bucket instead (line 385). This is the
  canonical citation for "SpecterX relates to your storage
  infrastructure."

---

## Source: editorial/ARTICLES_PLAN.md — Section 5 (Send protected email)

**Provenance:** `editorial/ARTICLES_PLAN.md`, lines 479–675
**Relevance:** Canonical language for the email use case (use case #2)
— Outlook and Gmail.

Key facts:
- The **Outlook Add-in** "works on Outlook for Web (OWA), Outlook for
  Desktop (Windows and Mac), and Outlook Mobile. Recommended for all
  new installations" (line 490).
- The **Outlook Classic Add-in** is "Windows Outlook Desktop only. In
  maintenance mode — no new features are being added" (line 491). Both
  should not be installed simultaneously (line 494).
- The Outlook Add-in adds a "SpecterX protection toggle to the Outlook
  compose window" (line 504). It exposes a side panel with a policy
  selector, recipient list, and per-recipient permissions (line 539).
- Email protection has three modes: **Off** (no protection),
  **Attachments only** (body unprotected), **Entire message** (body +
  attachments encrypted) (line 547). Same model in Gmail.
- The **Gmail Extension** = "a Chrome Extension that adds a SpecterX
  protection section to the Gmail Compose window" (lines 627, 654).
- Mail Protection Server / Mail Protection Service deliver
  server-side email protection independent of the user-installed
  add-ins (taxonomy line 57).

---

## Source: editorial/ARTICLES_PLAN.md — Section 7 (security policies)

**Provenance:** `editorial/ARTICLES_PLAN.md`, lines 900–1099
**Relevance:** Canonical definition of what a security policy contains
— the answer to the article's "what is a policy?" sub-question.

Key facts:
- The policy editor lives at `/policy-editor` (line 909).
- A policy is built from three named sections:
  - **Policy Configuration** — Restrict Policy to Specific Users
    toggle (line 911).
  - **Access Control** — Recipient Sharing Permissions
    (Allow Anyone / Restrict to Domain / Disable Sharing),
    Verification Requirements (Email OTP / Phone SMS / Personal Secret —
    combinable for MFA), Acknowledge Receipt (lines 912–914).
  - **Data Protection** — Protect and Track (always on), Block file
    download, Encrypt using a Password, Encrypt using Rights Management
    (RMS), Watermark (lines 915–919).
  - Plus Recipient Experience (language: English / Hebrew, line 920).
- Recipient Sharing Permissions ("forwarding") has three settings:
  Allow Sharing with Anyone, Restrict Sharing to Recipient's Domain,
  Disable Further Sharing (lines 948–950). This is the canonical
  control behind "forwarding" in the article brief.
- Expiry is the **Retention** setting in the policy, expressed in days
  (line 144).
- Download has its own toggle (Block file download, line 916).
- Verification, forwarding, download, expiry, and watermark are all
  controls on the policy — matching the article brief verbatim
  (line 23).
- **Platform Governance Rules** (PAR) are the org-wide layer on top of
  policies: condition → action (apply policy X, block share, notify
  admin) — lines 1048–1052. They are admin-configured automated rules
  for applying policies to files based on conditions.

---

## Source: editorial/ARTICLES_PLAN.md — Section 9 (integrations)

**Provenance:** `editorial/ARTICLES_PLAN.md`, lines 1235–1357
**Relevance:** Canonical citations for the "how SpecterX relates to
identity, storage, email infrastructure" sub-topic.

Key facts:
- **Identity integration** named sub-articles (lines 1243–1283):
  - Set up Entra ID authentication — SAML 2.0 for SSO, SCIM for
    provisioning.
  - Set up Okta authentication — SAML application in Okta + optional
    SCIM.
  - Set up Google Cloud Identity — SAML via Google Admin Console.
- **Storage integration** named sub-articles (lines 1286–1328):
  - Connect Amazon S3 — "SpecterX stores encrypted file data in your S3
    bucket instead of (or alongside) SpecterX-managed storage"
    (line 1293).
  - Connect SharePoint storage — dedicated SharePoint site, distinct
    from the SharePoint Connector (line 1308).
  - Connect Google Cloud Storage — Google Cloud Storage bucket
    (line 1322).
- **DLP mailflow integration** intercepts outbound email and applies
  protection based on DLP classification (line 1338).
- The S3/SharePoint/GCS storage integrations are the canonical citation
  for "SpecterX does not provide its own storage — it can sit on top of
  the storage you already use." (Note: SpecterX *does* have its own
  managed storage as the default — the integration is for organisations
  that prefer to keep files in their own buckets.)

---

## Source: editorial/ARTICLES_PLAN.md — "What SpecterX does and does not protect"

**Provenance:** `editorial/ARTICLES_PLAN.md`, lines 1772–1789
**Relevance:** Direct canonical answer to the "What SpecterX is NOT"
sub-question.

Key facts:
- **What SpecterX does protect** (lines 1777–1782):
  - Files shared via the web platform (tracking, policy enforcement,
    revocation).
  - Email attachments and body text (Outlook and Gmail connectors).
  - Files in Workspaces (access control, audit).
  - Files shared from Google Drive and SharePoint via the connectors
    (link-level protection — share-in-place).
  - Downloaded files (via RMS encryption, if enabled).
- **What SpecterX does NOT protect** (lines 1783–1788):
  - Screenshots of the SpecterX Viewer (no screen-capture blocking;
    only watermarking deters this).
  - Files downloaded without RMS, after a recipient opens them in a
    local app.
  - Data copied and pasted from the Viewer (unless RMS restricts copy).
  - Files the recipient already has outside of SpecterX.
  - The metadata of shared files (file names visible in audit logs but
    not classified).
- **Canonical "threat model" statement** (line 1789): "SpecterX
  protects against accidental forwarding, unauthorised access, and
  exfiltration from the SpecterX surface; it does not protect against
  a determined insider who copies content manually."

---

## Source: component-records/ folder layout

**Provenance:** `component-records/` directory tree (see `find` output
referenced in this research session).
**Relevance:** Confirms which components have PRD-stage source material
backing them. Where folders exist, the component is real and has
internal product records (all `.docx`; not parsed inline). Where they
don't, the component still exists in the inventory but has no PRD on
file.

Key facts (folder evidence — `.docx` contents not extracted):
- `component-records/user-facing-core/workspaces/project-workspaces-future-version/`
  contains five files including "Future Version_ Workspaces.docx",
  "PRD & User Stories_ Folder Behavior_.docx", "PRODUCT RECORD
  COMPONENT_ Workspace Existing (Requires QA Validation)_.docx",
  "RODUCT RECORD COMPONENT_ Workspace 2.0.docx". Confirms Workspace
  is a real, actively-evolving product area.
- `component-records/policy-controls/recipient-secure-link-experience/project-recipient-secure-link-experience-30/`
  contains "EPIC_ Recipient Link Experience 3.0.docx" and "Recipient
  Secure Link Experience 3.0_.docx". Confirms Recipient Page (= the
  "Recipient Secure Link Experience" surface) is a real product area
  with an in-flight v3.0 redesign — though the v3.0 redesign is
  explicitly NOT yet shipped (see `canon/DO_NOT_DOCUMENT.md` line 15:
  "Tour the redesigned SpecterX Recipient Page — Recipient Link
  Experience 3.0 redesign not yet shipped"). The article should
  describe the *current* Recipient Page, not the 3.0 redesign.
- `component-records/policy-controls/policy-configuration-console/`
  contains "Policy Assignment & Policy Availability — Operating
  Logic.docx". Confirms the policy-editor / policy-availability surface
  is a real product area.
- `component-records/policy-controls/password-protection/` —
  Password Policy Protection (the per-policy download-password toggle).
  This is NOT user-account passwords; see
  `articles/02-set-or-reset-password/research/internal-sources.md`
  for that distinction.
- `component-records/policy-controls/aip/` — contains a file titled
  "SpecterX File Protection through the File Lifecycle Overview"
  (`.docx`). The "AIP" folder name refers to Azure Information
  Protection / RMS, i.e. the Encrypt using Rights Management Policy
  Protection.
- `component-records/connectors/outlook-new/` — "PRD_ SpecterX
  Connector for Outlook New.docx". Confirms Outlook New is the
  canonical name of the actively-developed Outlook add-in.
- `component-records/connectors/sharepoint/` — has "prd-and-dev-
  documents", "project-sharepoint-connector-future-versions", and
  "sales-and-customer-facing-documentation" sub-folders.
- `component-records/connectors/slack-connector/` — confirms Slack
  Connector is real.
- `component-records/connectors/salesforce-connector/` — confirms
  Salesforce Reports / email connector is real.
- `component-records/platform-integrations/purview-integration/` —
  confirms Microsoft Purview classification integration is real.
- `component-records/admin-platform/platform-governance-rules/` —
  confirms PAR (Platform Governance Rules) is real and has substantial
  PRD material.
- `component-records/admin-platform/audit-logs/` — confirms Audit Logs
  is real.
- No folders for: **Authentication**, **Reset Password**, **Recipient
  Page** (only the v3.0 redesign project; nothing for the current
  Recipient Page), **Security Policies** (only the policy-availability
  operating-logic doc; no full PRD), **Mail Protection Server**,
  **Gmail Connector**, **SpecterX Viewer**, **On-Prem Gateway**,
  **Digital Signature**, **Storage Integration** (S3 / SharePoint /
  GCS — no PRD folders). For the article, this means component-records
  is NOT the primary citation for these areas; the taxonomy and the
  inventory are.

---

## Source: canon/GLOSSARY.md

**Provenance:** `canon/GLOSSARY.md`, lines 1–24
**Relevance:** Tenant URL convention — relevant if the article mentions
sign-in URLs.

Key facts:
- "Every SpecterX tenant has its own URL on the `specterx.com` domain.
  The canonical form is `https://<tenant>.specterx.com`" (lines 7–9).
- `https://app.specterx.com` is "the URL for one specific tenant
  (SpecterX's own production tenant), not a shared sign-in page"
  (lines 12–14).
- Do not document `app.specterx.com` as the default sign-in URL
  (lines 15–16).
- This is the canonical citation for any sentence about "your
  organisation's SpecterX URL."

---

## Source: canon/DO_NOT_DOCUMENT.md

**Provenance:** `canon/DO_NOT_DOCUMENT.md`, lines 1–38
**Relevance:** Skip-list of unshipped capabilities that must not be
described as current product behaviour.

Key facts that touch this article:
- Line 15: "Tour the redesigned SpecterX Recipient Page — Recipient
  Link Experience 3.0 redesign not yet shipped." → the article must
  describe the *current* Recipient Page only.
- Line 16: "Edit a protected file directly in SpecterX — in-platform
  file editing in planning; not shipped." → do not claim SpecterX is an
  editing platform.
- Line 17: "Request files without creating a workspace — standalone
  Request Files action still tied to Workspace creation in V1."
- Line 23: "Access multiple SpecterX tenants with single sign-on —
  multi-tenant SSO not yet shipped."
- Line 26: "Workspaces 2.0 redesign — planned redesign with additional
  capabilities; not yet shipped."

---

## Source: editorial/PUBLIC_KB_SCOPE.md

**Provenance:** `editorial/PUBLIC_KB_SCOPE.md`, lines 1–636
**Relevance:** General scope-and-style guide, not a source of
canonical product terms. Skim-relevant for two specific cues that
shape the article:

Key facts:
- Lines 130–138: the recipient is "the single most under-served
  audience in most enterprise security products' docs"; the
  article should describe the recipient experience as a first-class
  thing (matches the article brief).
- Lines 225–227: "Glossary of product-specific terms (Workspace,
  Policy, Parent Policy, Verification, Co-Owner, Contributor)" —
  the foundational article (this one) is the right place to introduce
  these terms once, so other articles can link back to it instead of
  re-explaining.
- Lines 437–446: "Deliberately NOT public" — confirms that this
  article must not describe internal architecture, microservice
  names, or specific bypass techniques.

---

## Source: legacy-manuals/ folder layout

**Provenance:** `legacy-manuals/` directory tree.
**Relevance:** Historical (.docx) customer/operator documentation,
imported from Google Drive. Not parsed inline (all `.docx`). Folder
naming corroborates the product surface inventory.

Key facts (folder evidence):
- `legacy-manuals/customer/` contains:
  - "SpecterX - Outlook Add-in Group Policy - English 1.0.docx",
    "SpecterX - Outlook Add-in Group Policy - English.docx",
    "SpecterX - Forcepoint Integration Manual.docx",
    "SpecterX for Slack_ Onboarding & User Guide.docx" — confirms
    Outlook, Forcepoint, and Slack as documented customer-facing
    integrations.
- `legacy-manuals/mailflow-and-workspaces/` contains "Integrating SPX
  within Mailflow Guide_.docx" and "SpecterX Workspaces Functions &
  Controls_.docx" — confirms Workspaces and Mail Protection / Mailflow
  as discrete product areas.
- `legacy-manuals/policy-control-guides/` contains "Onboarding Guide
  for Admins.docx", "Policy Configuration Guide - Draft 1.0.docx",
  "SpecterX Policy Control Guide_.docx" — confirms policy
  configuration is a discrete, admin-facing area.
- `legacy-manuals/operator/` contains "SpecterX Gateway -
  On-Premise Deployment Guide for Integrators v2.3.docx" (and v2.1 /
  v2.2 / v2.4) — confirms On-Prem Gateway is real.
- `legacy-manuals/misc/` contains:
  - "Capabilities of SpecterX Google Drive Connector.docx" —
    Google Drive Connector capability sheet.
  - "Capabilities of SpecterX Watermarking V.1.docx" — Watermarking
    capability sheet.
  - "SpecterX Outlook Classic Connector Technical & Integration
    Guide.docx" — confirms Outlook Classic Connector as a documented
    integration.
  - "SpecterX Salesforce Connector Capabilities.docx" — confirms
    Salesforce Connector.
  - "SpecterX Access Control Capabilities across Supported Applications
    & File Types - shared with Lexington.docx" — customer-shared
    capability matrix.
  - "SpecterX Sample Policies, Controls & User Experience - Oct.
    2025.docx" — customer-shared sample policy bundle. This is the
    canonical citation for "what example policies look like" if the
    article wants one, but the .docx was not parsed inline.

---

## Sub-topic coverage report

| Sub-topic                                             | Internal source coverage                                                                                                                                                                          |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "sender" and "recipient" as named roles               | Covered: `editorial/ARTICLES_PLAN.md` line 21.                                                                                                                                                    |
| "security policy" and its controls                    | Covered: `editorial/ARTICLES_PLAN.md` lines 23, 906–924; `components-inventory.txt` line 81. Controls = verification, forwarding (Recipient Sharing Permissions), download, expiry (Retention), watermark, password, RMS. |
| Recipient Page                                        | Covered: `components-inventory.txt` line 73; `ARTICLES_PLAN.md` lines 178–186.                                                                                                                    |
| SpecterX Viewer                                       | Covered: `COMPONENT_TAXONOMY.md` lines 73–77; `ARTICLES_PLAN.md` lines 354–366.                                                                                                                   |
| Workspace                                             | Covered: `components-inventory.txt` line 103; `ARTICLES_PLAN.md` lines 376–476; `component-records/user-facing-core/workspaces/` (folder evidence).                                               |
| Outlook & Gmail email protection                      | Covered: `COMPONENT_TAXONOMY.md` lines 52–57; `components-inventory.txt` lines 25, 57, 59; `ARTICLES_PLAN.md` lines 485–675.                                                                      |
| What SpecterX is NOT                                  | Covered: `ARTICLES_PLAN.md` lines 25, 1772–1789; `COMPONENT_TAXONOMY.md` line 166 (Digital Signature is not a Policy Protection); `canon/DO_NOT_DOCUMENT.md` lines 15–17.                          |
| Identity-provider integration                         | Covered: `COMPONENT_TAXONOMY.md` lines 33–37, 100–103; `ARTICLES_PLAN.md` lines 1243–1283.                                                                                                        |
| Storage-provider integration (S3/OneDrive/Drive/SharePoint) | Partial. `COMPONENT_TAXONOMY.md` lines 27–31 names Amazon S3, SharePoint, Google Cloud Storage. `ARTICLES_PLAN.md` lines 1288–1328 names the same three. **No internal source found** for OneDrive specifically; OneDrive is NOT in the canonical Storage Integration list. The Share-in-Place SharePoint Connector (separate from SharePoint Storage) is in `COMPONENT_TAXONOMY.md` line 62 and `ARTICLES_PLAN.md` line 729+. **No internal source found** for "Google Drive" as a storage integration — Google Drive is only a Share-in-Place Connector (line 61). |
| Email infrastructure integration                      | Covered: `COMPONENT_TAXONOMY.md` line 57 (Mail Protection Server); `components-inventory.txt` lines 33, 37 (Mail Protection Server, Mail Protection Service); `ARTICLES_PLAN.md` lines 1338–1345 (DLP Mailflow Integration).         |

---

## Synthesis — the canonical SpecterX answer

**What SpecterX is.** SpecterX is a file- and email-protection platform
that lets a *sender* share content with a *recipient* under controls
defined by a *security policy*. The platform exists in three product
surfaces that all enforce the same policy model: a web platform, mail
connectors for Outlook and Gmail, and Workspaces for ongoing
collaboration.

**The two actors.**
- **Sender** — the SpecterX-licensed user who shares a file, a folder,
  an email body + attachments, or a Workspace. (`ARTICLES_PLAN.md`
  line 21.)
- **Recipient** — anyone (internal or external) who receives a
  protected link. The recipient does not need a SpecterX account; they
  are auto-provisioned at the moment of share, and they reach the file
  through the Recipient Page. (`ARTICLES_PLAN.md` line 21, lines
  178–187; `COMPONENT_TAXONOMY.md` line 104 on user-facing surfaces.)

**The three main use cases.**
1. **Share a protected file from the web** — the user uploads or
   selects a file in the web platform, picks a security policy from the
   dropdown, adds recipients with permission levels (Viewer /
   Contributor / Co-Owner), and clicks Share. The Share & Permissions
   Drawer is the canonical post-share management UI.
   (`ARTICLES_PLAN.md` lines 65–164.)
2. **Protect email and attachments from Outlook or Gmail** — the user
   composes a normal email in Outlook (via the Outlook Add-in, or the
   maintenance-mode Outlook Classic Add-in) or Gmail (via the Gmail
   Browser Extension). A SpecterX side panel adds policy selection and
   per-recipient permissions. Protection mode is Off / Attachments only
   / Entire message. (`ARTICLES_PLAN.md` lines 485–675;
   `COMPONENT_TAXONOMY.md` lines 52–57.)
3. **Collaborate securely in a Workspace** — a Workspace is a
   persistent collaboration space with a parent policy, folder
   structure, named members (Owner / Co-Owner / Contributor / Viewer),
   and tabs for Files / Members / Policy / Audit. All files uploaded
   inherit the workspace's parent policy. (`ARTICLES_PLAN.md` lines
   376–414; `components-inventory.txt` line 103.)

**What a security policy is.** A security policy is a named, reusable
bundle of controls authored in the policy editor (`/policy-editor`)
and selected at share time from a dropdown. Its sections are:

- **Policy Configuration** — restrict who can use this policy.
- **Access Control** — Recipient Sharing Permissions (Allow Anyone /
  Restrict to Domain / Disable Sharing — the "forwarding" control);
  Verification Requirements (Email OTP / Phone SMS / Personal Secret,
  combinable for MFA — the "verification" control); Acknowledge
  Receipt.
- **Data Protection** — Protect and Track (always on); Block file
  download (the "download" control); Encrypt using a Password; Encrypt
  using Rights Management (RMS); Watermark.
- **Retention** — number of days after which the link expires (the
  "expiry" control).

(`ARTICLES_PLAN.md` lines 906–924, 144, 948–950;
`components-inventory.txt` line 81;
`COMPONENT_TAXONOMY.md` lines 160–166.)

Above the per-share policy layer sits **Platform Governance Rules**
(PAR) — admin-configured, organisation-wide rules that apply, override,
or block policies automatically based on conditions like sender, recipient
domain, or Purview sensitivity label. (`ARTICLES_PLAN.md` lines
1045–1099.)

**What the recipient experiences.**
- The **Recipient Page** — the landing page after clicking a protected
  link; layout includes identity selection, verification step, file
  preview summary, and action buttons. (`ARTICLES_PLAN.md` line 179;
  `components-inventory.txt` line 73.)
- A **verification step** — email OTP by default; phone SMS OTP or a
  personal secret if the policy requires them; SSO can satisfy email
  verification automatically. (`ARTICLES_PLAN.md` lines 200, 211–237,
  967.)
- The **SpecterX Viewer** — a browser-based document viewer that
  renders the file in the browser with no plugins; dynamic watermarks
  appear when the policy enables them; the recipient can download,
  forward, or open in an external app only if the policy permits.
  (`ARTICLES_PLAN.md` lines 359–366; `COMPONENT_TAXONOMY.md` lines
  73–77.)

**What SpecterX is NOT.**
- **Not a storage product.** SpecterX has its own managed storage by
  default, but the canonical integration story is that customers can
  point Workspaces at their existing Amazon S3 / SharePoint /
  Google Cloud Storage — SpecterX is the protection and access layer,
  not the place where the files live. (`ARTICLES_PLAN.md` lines 25,
  385, 1288–1328.)
- **Not a file editor.** No in-platform editing in V1.
  (`canon/DO_NOT_DOCUMENT.md` line 16.)
- **Not a signature platform** — except via the standalone Digital
  Signature feature, which is a single, scoped capability, not the
  platform's core business. (`ARTICLES_PLAN.md` line 25;
  `COMPONENT_TAXONOMY.md` line 166;
  `components-inventory.txt` line 9.)
- **Not a defence against determined-insider exfiltration.** SpecterX
  protects against accidental forwarding, unauthorised access, and
  exfiltration from the SpecterX surface; it does not prevent screen
  capture, manual transcription, or copy of an already-downloaded file
  outside RMS. (`ARTICLES_PLAN.md` line 1789.)
- **Not a CRM, not an identity provider, not a mail server.** Each is
  an upstream system SpecterX integrates with — see below.

**How SpecterX relates to upstream systems.**
- **Identity providers** — SpecterX authenticates senders via Okta,
  Entra ID, or Google Cloud Identity (SAML 2.0 SSO; SCIM for
  provisioning). The IdP owns the user's password and MFA; SpecterX
  trusts the assertion. (`COMPONENT_TAXONOMY.md` lines 33–37;
  `ARTICLES_PLAN.md` lines 1243–1283.) Recipients do not require an
  IdP — they authenticate per-share via the Recipient Page.
- **Storage providers** — Workspaces can be backed by Amazon S3,
  SharePoint, or Google Cloud Storage; files are written to the
  customer's bucket / site under SpecterX encryption.
  (`COMPONENT_TAXONOMY.md` lines 27–31; `ARTICLES_PLAN.md` lines
  1288–1328.) Separately, the **Share-in-Place Connectors** for Google
  Drive and SharePoint let users share files that *stay* in Drive /
  SharePoint, with SpecterX adding protection at the access layer
  without moving the file. (`COMPONENT_TAXONOMY.md` lines 61–62,
  114–119.)
- **Email infrastructure** — the Outlook Add-in, Outlook Classic
  Add-in, and Gmail Browser Extension are client-side; the **Mail
  Protection Server** (and its cloud counterpart, **Mail Protection
  Service**) is server-side plumbing that intercepts outbound email and
  applies policy automatically, optionally driven by DLP signals.
  (`COMPONENT_TAXONOMY.md` lines 52–57;
  `components-inventory.txt` lines 33, 37; `ARTICLES_PLAN.md` lines
  1338–1345.)

**Gaps flagged for future work.**
- There is no `component-records/` PRD folder for the **Recipient
  Page** as it exists today (only the v3.0 redesign project, which is
  unshipped). The article describes the *current* Recipient Page from
  the inventory + ARTICLES_PLAN; if a PRD for the current surface
  exists elsewhere it has not been imported into the repo.
- No internal-source folder for **SpecterX Viewer**, **Digital
  Signature**, **Mail Protection Server**, **Gmail Connector**, or any
  of the three **Storage Integrations** under
  `component-records/`. Canonical names and behaviours come from
  `COMPONENT_TAXONOMY.md` and `ARTICLES_PLAN.md` only.
- The .docx artefacts in `component-records/` and `legacy-manuals/`
  were not parsed inline; folder names and file titles were used as
  presence-evidence only. Where a deeper claim is needed in the
  article, the relevant .docx should be opened and quoted directly.
- `references/internal/` does not exist in the repo. Where the
  pipeline prompt expects `references/internal/`, the canonical
  internal sources are `product/`, `component-records/`, `editorial/`,
  `canon/`, and `legacy-manuals/`.
