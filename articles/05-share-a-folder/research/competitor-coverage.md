# Competitor coverage — Share a folder

Cache-first lookup: the `references/competitors/INDEX.json` has 4
entries whose `topics` match "share folder" keywords across 4 different
vendors. Cache threshold (2+ matches across different vendors) is met.
No online scraping was performed.

## Cached entries used

| Vendor | Slug | File | Captured |
|---|---|---|---|
| Egnyte | `share-folder` | `egnyte/share-folder.md` | 2026-06-07 |
| Dropbox | `share-folder` | `dropbox/share-folder.md` | 2026-06-07 |
| Virtru | `share-folder` | `virtru/share-folder.md` | 2026-06-07 |
| DocSend | `share-folder` | `docsend/share-folder.md` | 2026-06-07 |

---

## Coverage checklist

The following is a checklist of topics competitors covered, extracted
from the cached notes (see each source file for full paraphrased
coverage; do not copy their words):

### Access model and permission levels
- [x] **Egnyte**: 5-tier permission matrix (Viewer-Only / Viewer /
  Editor / Full / Owner); explicit capability comparison table.
- [x] **Dropbox**: Editor vs. viewer access as the basic split; editor
  access includes add, edit, download, delete, reshare; viewer is
  read-only. Sub-folder re-share rights tied to parent-folder
  permission level.
- [x] **DocSend**: Permissions applied per-link (not per-user): Visible
  / Downloadable / Watermark / NDA per item; link-level allow/block list.
- [ ] **Virtru**: No folder-level permissions — file-centric model only.
  Virtru treats each file as an independent protection unit.

### Inheritance: what happens when access is granted on a parent
- [x] **Egnyte**: Sharing a parent automatically shares all subfolders
  (inheritance on by default). A subfolder can disable inheritance; then
  its permissions are managed independently. A user without parent access
  can still be granted access to a specific subfolder and sees the parent
  as a greyed navigation path.
- [x] **Dropbox FAQ**: Owner of a parent shared folder automatically
  owns every subfolder, including ones created by others. You cannot
  unshare a folder that has nested shared folders inside it.
- [ ] **DocSend**: Inheritance expressed as "add new files to the
  existing Space; recipients automatically see them." Advanced plan
  allows subfolder-of-subfolder structure.

### Policy / protection inheritance (how a folder's policy applies to its files)
- [ ] None of the competitors have a direct equivalent to SpecterX's
  policy inheritance model. This is a key differentiator to explain.
  Egnyte has permission inheritance, not encryption-policy inheritance.
  Virtru is per-file only. DocSend has per-link settings.

### What a recipient sees when they receive a shared folder link
- [x] **Dropbox**: Recipients must accept shared folder invitation
  (individual accounts); teammates auto-join team folders.
- [x] **DocSend**: Recipient-facing experience is a "Space" view;
  multiple links per Space allow different audience controls. NDA
  acceptance gate before entry.
- [ ] **Egnyte / Virtru**: Recipient experience not prominently covered
  for folders specifically.

### Adding files to an already-shared folder
- [x] **DocSend**: Explicitly documents "add new files to the existing
  Space; recipients with the link automatically see them." This is the
  DocSend equivalent of SpecterX's inheritance behavior.
- [x] **Egnyte**: Implicit: new files in a shared folder inherit the
  folder's access unless the subfolder has its own permissions.
- [ ] SpecterX plan covers this ("What happens when you add a new file
  to an already-shared folder").

### Folder ownership and management after sharing
- [x] **Dropbox**: Only the owner can unshare a folder with no nested
  shared folders. Ownership transfers must happen at the parent level.
  Sub-folder re-share follows a permission-tier rule (owner free / editor
  if granted / viewer link-only).
- [x] **Egnyte**: Owner (highest tier) can revoke access; a user
  granted directly wins over group-level grants.

### Revoking and updating access
- [x] **Egnyte**: Per-user revocation; a "None" record in the Folder
  Permissions Report marks explicit exclusion.
- [x] **Virtru**: Revoke at any time from the Control Center; works
  per-file not per-folder.
- [ ] SpecterX plan does not separately document revocation for folders
  (covered in article 08-revoke-access for files; the folder article
  should cross-reference).

### Notification email when access changes
- [x] **Egnyte**: Email sent every time access is granted, altered, or
  revoked for an individual user. Group membership and inheritance
  changes do NOT trigger the notification. Noted as "limited
  availability."

### Plan gating / feature availability
- [x] **Egnyte**: Bulk-invite gated to Document Room / Enterprise Lite.
- [x] **DocSend**: Spaces only on Standard, Advanced, Advanced Data
  Rooms plans; subfolder nesting only on Advanced.
- [x] **Dropbox**: Edit access, team folder controls gated by plan tier
  (Professional / Standard / Business / etc.).
- [ ] **SpecterX**: No feature gating identified for folder sharing.

---

## Patterns NOT to copy

- **Egnyte's 9-section article structure**: too dense and reference-
  heavy for our article style. SpecterX articles should be task-
  oriented quickstarts, not exhaustive references.
- **DocSend's "Space" vocabulary**: DocSend calls folders "Spaces" and
  "data rooms" — do not use this framing for SpecterX folders.
- **Virtru's per-file framing**: Virtru explicitly lacks a folder
  primitive. Do not frame SpecterX folder sharing in per-file terms.
- **Dropbox's consumer-facing short-sentence voice**: appropriate for
  Dropbox's consumer product; SpecterX is enterprise-oriented.

---

## Proposed additions from competitor coverage

The following topics appear in competitor docs but are not in the current
plan entry. Flagging for Guy to decide on inclusion:

1. **Explicit exclusion / removal of inherited access**: Egnyte covers
   the case where a user needs to be blocked from a specific subfolder
   even though they have parent access. The SpecterX plan doesn't
   mention this explicitly — may be worth a note if SpecterX supports it.

2. **Limits or quotas on folder sharing**: Dropbox documents hard limits
   (1,500 nested shared folders; 30,000 across account). If SpecterX has
   no such limits, a brief "there are no share limits on folders"
   sentence could reassure users.

3. **What happens to the folder if the owner's account is deactivated**:
   Dropbox covers ownership transfer; Egnyte has admin override. Worth a
   brief mention if SpecterX has a corresponding behavior.

4. **Re-sharing / forwarding at the folder level**: Can a Co-owner
   reshare the folder with new recipients? The plan mentions Co-owner can
   do this (implied by the role description), but making it explicit
   with a sentence would match competitor coverage depth.

---

## Articles read

- Egnyte: `references/competitors/egnyte/share-folder.md` (captured 2026-06-07)
- Dropbox: `references/competitors/dropbox/share-folder.md` (captured 2026-06-07)
- Virtru: `references/competitors/virtru/share-folder.md` (captured 2026-06-07)
- DocSend: `references/competitors/docsend/share-folder.md` (captured 2026-06-07)
