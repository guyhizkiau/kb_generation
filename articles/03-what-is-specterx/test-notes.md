# Test notes — What is SpecterX?

**Test type:** label and concept verification (no procedural flow).
**Date:** 2026-06-01.
**Sources:**
- Codebase recon (`research/codebase-findings.md`) against
  `~/specterx-codebase/web-client/` and
  `~/specterx-codebase/admin-web-client/`.
- Internal sources (`research/internal-sources.md`) against
  `product/COMPONENT_TAXONOMY.md`, `product/components-inventory.txt`,
  and `editorial/ARTICLES_PLAN.md`.
- Existing live-tenant screenshots from articles 01
  (`articles/01-log-in-to-specterx/screenshots/`) and 02
  (`articles/02-set-or-reset-password/screenshots/`), captured against
  `https://app.specterx.com` in 2026-05 and 2026-06.

## Why this is light validation

This is an overview article. It has no step-by-step UI flow to
execute. The validation reduces to confirming that every UI label,
product term, and concept named in the body matches the live product
and the canonical product vocabulary.

## Labels and concepts verified

| Article term | Source | Verdict |
| --- | --- | --- |
| **Sender** / **Recipient** | `editorial/ARTICLES_PLAN.md:21`; `web-client/src/content/general.json:204, 412, 676` | Canonical product terms. "Recipient" is a UI label; "Sender" only appears in interpolated copy. Article describes both correctly. |
| **Security policy** / **Policy** | `web-client/src/content/general.json:246, 614`; `admin-web-client/client/src/i18n/config.ts:34, 248` | UI uses both. Article introduces "security policy" and uses "policy" thereafter. Consistent with the per-file pop-up label and the admin-portal nav. |
| **Secure Viewer** | `web-client/src/content/general.json:199, 1691` | Recipient-facing UI label. Article uses "Secure Viewer." |
| **Workspaces** | `web-client/src/content/general.json:93, 167, 467`; `web-client/src/components/SideBar/SideBar.tsx:54` | Canonical product term. Article notes the per-tenant availability caveat (gated by `ENABLE_WORKSPACE` per `web-client/src/config/env.ts:68`). |
| **Outlook Add-in** / **Outlook Classic Add-in** | `product/COMPONENT_TAXONOMY.md:52-55`; `editorial/ARTICLES_PLAN.md:490-494`; `legacy-manuals/customer/SpecterX - Outlook Add-in Group Policy*.docx`; `component-records/connectors/outlook-new/` | Canonical product names. Article uses "Outlook Add-in" (modern); the older classic add-in is omitted from the body to keep length tight. |
| **Gmail Extension** | `product/COMPONENT_TAXONOMY.md:56`; `product/components-inventory.txt:25`; `editorial/ARTICLES_PLAN.md:627` | Canonical. Article uses "Gmail Extension." |
| **Digital Signature** (standalone) | `product/COMPONENT_TAXONOMY.md:166`; `product/components-inventory.txt:9` | Canonical and aligns with the "is NOT a signature platform except via..." line in the plan. |
| **Identity providers** (Microsoft Entra ID, Google Workspace, Okta) | `product/COMPONENT_TAXONOMY.md:33-37`; `admin-web-client/client/src/data/integrations.ts:25-55` | Canonical IdP names. Article uses these forms. |
| **Storage backends** (Amazon S3, SharePoint, Google Cloud Storage) | `product/COMPONENT_TAXONOMY.md:27-31`; `admin-web-client/client/src/data/integrations.ts` | Canonical. Article omits OneDrive (not supported as storage) and Google Drive (separate share-in-place connector, not a storage backend). |
| **Verification methods** (email OTP, SMS, personal secret) | `web-client/src/content/general.json:1188-1259`; `admin-web-client/client/src/i18n/config.ts:328-423` | Canonical labels and behavior. Article paraphrases without claiming defaults beyond "usually a 6-digit code sent to email." |

## Things deliberately not captured by this article

- **"Recipient Page" as a UI proper noun.** The phrase appears as a
  component folder name and i18n namespace, but the recipient never
  sees the words. The article describes the surface functionally
  ("a verification page") rather than presenting "Recipient Page" as
  a proper noun.
- **Platform Governance Rules (PAR).** Real, named, and a real
  feature, but the foundational article would balloon if it
  introduced PAR alongside per-share policies. Deferred to a later
  article in the security-policies cluster.
- **Send-a-file-back / become-licensed-user upsell flows.** Real but
  recipient-side edge cases. Deferred.

## Limitations

- The Outlook and Gmail add-ins ship as separate extensions outside
  the two SPA repos (`web-client` and `admin-web-client`). Their
  existence is confirmed by `product/COMPONENT_TAXONOMY.md`,
  `product/components-inventory.txt`, `legacy-manuals/customer/`, and
  `component-records/connectors/outlook-new/`. A live UI capture of
  the Outlook panel and the Gmail panel was not performed for this
  article. If the article's claims about these add-ins are later
  challenged, the canonical citations are the taxonomy and the
  inventory.
- Workspaces is gated by `ENABLE_WORKSPACE` and is **off by default**
  on the base production config (`web-client/src/config/env.ts`).
  The article reflects this with "available when your administrator
  has enabled them for your organization."

## Screenshots

None promoted. The competitor median for overview pieces is 0 to 1
screenshots; the article carries its concepts in prose, and adding a
screenshot of the sign-in page (already shown in articles 01 and 02)
would not add new information here.
