# UI glossary — What is SpecterX?
# Sourced from: codebase recon (web-client locales + admin-web-client i18n)
# Captured: 2026-06-01

This article is an overview piece, not a procedural one. It does not
walk the reader through a specific UI flow, so a fresh UI capture pass
is not required. The canonical labels referenced in the article body
are pulled from the codebase recon (see
`../codebase-findings.md`) and from the product taxonomy (see
`../internal-sources.md`).

## Canonical UI labels referenced in the article

### Top-level vocabulary

- **Recipient** — UI-visible noun for the person receiving a share.
  Source: `web-client/src/content/general.json:190, 204, 412, 676`.
- **Sender** — only appears in interpolated copy
  (`"{{sender}} shared a file with you"`), never as a screen heading
  or persona label. Use descriptively in prose.
  Source: `web-client/src/content/general.json:204, 207, 330`.
- **Policy** / **Policies** — canonical noun for the security-policy
  concept.
  Sources: `web-client/src/content/general.json:614`,
  `web-client/src/stores/AppStore/menuItems.ts:38`,
  `admin-web-client/client/src/i18n/config.ts:34`.
- **Security policy** — descriptive variant that appears in exactly
  one place: the per-file pop-up on the recipient page (`"Security
  policy for this file"`).
  Source: `web-client/src/content/general.json:246`.
  Use "security policy" in the article body the first time the
  concept is introduced; thereafter use "policy" interchangeably.
- **Workspace** / **Workspaces** — canonical.
  Sources: `web-client/src/content/general.json:93, 167, 467`,
  `web-client/src/stores/AppStore/menuItems.ts:26`.
  Note: gated by per-tenant flag `ENABLE_WORKSPACE`. The article
  must caveat availability.
- **Secure Viewer** — recipient-facing UI label for the in-browser
  document viewer.
  Sources: `web-client/src/content/general.json:199, 1691`.
- **SpecterX Viewer** — taxonomy / product-name form of the same
  thing. Use this in overview prose; mention "Secure Viewer" as the
  button label.
  Source: `product/COMPONENT_TAXONOMY.md:73-77`.

### Recipient-side experience

- **Recipient Page** is internal jargon (component folder name,
  i18n namespace). The recipient never sees the phrase. Describe
  the surface as "the page recipients land on after clicking a
  protected link" rather than using "Recipient Page" as a proper
  noun.
  Source: `web-client/src/components/MiniApps/RecipientPage/index.tsx`.
- **Verify email** / **Verify phone number** / **Verify personal
  secret** — the three policy-driven verification options.
  Sources: `web-client/src/content/general.json:1196-1198,
  1192-1194, 1257-1259`.

### Use case 2 — Outlook and Gmail

The Outlook and Gmail add-ins are not present in the two scanned
SPAs (web-client and admin-web-client). They ship as separate
extensions. The article describes them at concept level, naming:

- **Outlook Add-in** (modern) and **Outlook Classic Add-in**
  (Windows desktop, maintenance mode).
  Sources: `product/COMPONENT_TAXONOMY.md:52-57`,
  `editorial/ARTICLES_PLAN.md:490-494`,
  `legacy-manuals/customer/SpecterX - Outlook Add-in Group Policy*`,
  `component-records/connectors/outlook-new/`.
- **Gmail Browser Extension** / **Gmail Extension**.
  Sources: `product/COMPONENT_TAXONOMY.md:56`,
  `product/components-inventory.txt:25`,
  `editorial/ARTICLES_PLAN.md:627`.

### Storage and identity

- **Identity providers:** Microsoft Entra ID, Google Workspace
  (Google Cloud Identity), Okta.
  Source: `product/COMPONENT_TAXONOMY.md:33-37`,
  `admin-web-client/client/src/data/integrations.ts:25-55`.
- **Storage backends (for Workspaces):** Amazon S3, SharePoint,
  Google Cloud Storage. (No OneDrive. Google Drive is a separate
  share-in-place connector, not a storage backend.)
  Source: `product/COMPONENT_TAXONOMY.md:27-31`,
  `admin-web-client/client/src/data/integrations.ts`.

## Screenshots

None planned for this article. Competitor median for overview
pieces is 0 to 1 screenshots; the prose carries the explanation.
If a single screenshot is added during revision, it would be the
recipient-side share-link landing (the surface most readers
have not seen). Decision deferred to draft review.

## Differences from plan vocabulary

- The plan calls the document viewer "SpecterX Viewer." The UI
  calls it "Secure Viewer." The article uses both, with a brief
  note.
- The plan says "Recipient Page." This is internal jargon. The
  article describes the surface functionally rather than using
  "Recipient Page" as a proper noun.
- The plan calls the security concept a "security policy." The
  UI calls it "Policy." The article introduces it as "security
  policy" then refers to "policy" or "the policy" thereafter.
