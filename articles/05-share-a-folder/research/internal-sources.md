---
captured: 2026-06-07
article: 05-share-a-folder
---

# Internal sources — Share a folder

## Source: product/components-inventory.txt
**Provenance:** product/components-inventory.txt, line for "Folders"
**Relevance:** Confirms **Folders** is an inventoried SpecterX product component.

Key facts:
- Folders is a first-class component name; use the noun "folder" in prose.
- It is in the same inventory as Encrypt using Rights Management - Policy Protection (file/folder protection toggles run through policy).

## Source: product/COMPONENT_TAXONOMY.md
**Provenance:** product/COMPONENT_TAXONOMY.md, §"Policy Protection" (~line 170), §"Storage Integration" (~line 108)
**Relevance:** Defines how policy is applied to governed objects and where governed data lives.

Key facts:
- **Policy Protection** is a file-level security measure that admins enable through the policy management UI, and which applies automatically to files governed by that policy. The same enforcement model extends to files inside a shared folder when the folder's policy is set.
- Storage Integration "backs every kind of SpecterX-governed object" including files uploaded via the web platform; folders and their child files live in the customer's S3 / SharePoint / GCS bucket.
- Do not write that SpecterX provides its own managed storage; do not claim extra encryption layers.

## Source: product/notes.md
**Provenance:** product/notes.md, "From article 03 — What is SpecterX" (~lines 12–60)
**Relevance:** Establishes the share / policy / recipient model already used by approved articles.

Key facts:
- Sender vs recipient: recipients do not need a SpecterX account and are provisioned implicitly at share time.
- A **security policy** is an admin-defined bundle that the sender picks at share time. It governs recipient verification, forwarding, download blocking, watermarking, and password protection.
- Inside a Workspace, the sender/recipient relationship is a named role (Owner, Co-Owner, Contributor, Viewer). For one-off shares outside Workspaces, the same three recipient permission levels (Viewer, Contributor, Co-Owner) apply.

## Source: references/internal/
**Provenance:** references/internal/ does not exist in the repo.
**Relevance:** None — no PRDs or internal handbook material has been ingested yet.

Action: no internal docs to cite beyond product/. The article must rely on UI recon and codebase findings for behavior that isn't covered by the existing canon.

## Source: prior approved articles
**Provenance:** articles/01-log-in-to-specterx/final.md, articles/02-set-or-reset-password/final.md, articles/03-what-is-specterx/final.md
**Relevance:** Establish voice, structural conventions, intro length, and screenshot density expectations.

Key facts:
- Approved articles use second person, contractions, present tense, short symptom-led troubleshooting headers.
- Procedural articles open with one short paragraph (25–60 words) and follow the **Before you start / Steps / Troubleshooting / Related articles** skeleton.
- Approved articles forward-link to adjacent flows inline (e.g. "Reset your password") rather than burying them in "What this article doesn't cover."
