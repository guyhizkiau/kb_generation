# Internal sources — Share a folder
# Gathered: 2026-06-11

No `references/internal/` directory exists in this repository.

No internal sources found for this topic. Drafting will rely on codebase findings and UI reconnaissance.

## Notes from the article plan

From `editorial/ARTICLES_PLAN.md` — "Share a folder" (Section 2):

**Topics to cover:**
- How sharing a folder differs from sharing a file: all files inside inherit the folder's policy
- The Share a folder flow from the Share files menu
- The parent policy and policy inheritance: new files uploaded to a shared folder automatically get the folder's policy
- Setting per-file policies that override the parent
- Recipient experience: what a recipient sees when they receive a shared folder link
- Folder permissions vs file permissions: can a recipient with Viewer access on the folder download individual files?
- What happens when you add a new file to an already-shared folder

**From cluster SCENARIO.md (05-share-a-folder):**
- Create a temporary test folder and upload at least one file to it before testing the share flow.
- Clean up the folder after screenshots are captured.

**Related articles in the same cluster:**
- `04-share-a-file` — covers the Share Files drawer (common infrastructure)
- `06-set-recipient-permissions` — covers Viewer / Contributor / Co-owner in depth
- `07-update-permissions` — covers the Share & Permissions drawer post-share
