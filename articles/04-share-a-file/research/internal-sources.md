# Internal sources — Securely share a file from the SpecterX web platform

## `references/internal/`

No internal source documents matched on the keywords `share`, `recipient`, `policy`, `permission`, or `drawer`. The directory is currently empty of share-files-specific PRDs or design notes.

`references/internal/INDEX.md` does not exist; if Guy provides PRDs in `references/internal/_inbox/` in a later run, process them then.

## `product/`

### `product/COMPONENT_TAXONOMY.md`

**Relevant components:**

- **Share-in-Place Connector** (lines 124–129) — a Connector where the file *stays in its original storage location*. This article is **not** about Share-in-Place: it covers the case where the user uploads (or selects an existing) file in the SpecterX web platform and shares it from there. Article cross-references can mention Share-in-Place for Google Drive / SharePoint flows.
- **Storage Integration** (lines 108–112) — the "where the protected file actually lives" decision (Amazon S3 / SharePoint Storage / Google Cloud Storage). Tenant-wide; not visible in the Share Files dialog. Worth mentioning in the recipient-experience paragraph if a customer is confused about where their file went, but probably not.
- **The hard rule "no SpecterX-managed storage" framing** (line 110). The article must not say SpecterX "stores" the file or "saves a copy" — the file enters the organization's own storage backend.

### `product/component-records/user-facing-core/folders/`

Contains:
- `SpecterX Folder Model — Operating Logic and UX Guidance.docx`
- `SpecterX Folder Model — Proposed Operating Logic and UX.docx`
- `project-ux-and-permission-planning-folder/PRD_ Folder Permission Standardization.docx`
- `project-ux-and-permission-planning-folder/PRD_ Upload Flow Planning.docx`
- `project-ux-and-permission-planning-folder/PRD - Establishing Request Files as an Independent Action.docx`
- `project-ux-and-permission-planning-folder/UX & Permission Overhaul - Planning notes.docx`

These are folder/upload-flow PRDs. Relevant to the *folder* article (05-share-a-folder), only tangentially to this one. Worth keeping in mind that the upload-flow PRD discusses the same upload widget the share flow uses, and that the permission standardization PRD covers the Viewer / Contributor / Co-Owner tiers consistently. No direct facts to extract for this article that aren't already in the codebase i18n strings (see `codebase-findings.md`).

## Conclusion

The authoritative source for UI labels and behavior for this article is the codebase (`~/specterx-codebase/web-client/`) plus the live UI recon. There are no SpecterX-internal PRDs that change or override what the codebase shows for the share dialog flow.
