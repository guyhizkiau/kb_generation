---
ui-drift-risk: low
source: web-client/src/content/general.json
searched: 2026-06-11
---

# Codebase findings — Share a folder

## Source coverage

Searched: `~/specterx-codebase/web-client/src/content/general.json`
No `src/` TypeScript/TSX component files were accessible (git pack-only, no working tree checkout).
Admin web client does not contain folder-share UI strings relevant to end-user flows.

---

## UI strings — exact labels

### Share flow entry points (My Files page header)

- **"Share files"** — the primary button that opens the Share Files drawer (same button for files and folders)
- **"Share a folder"** — the dropdown item that switches the upload area to folder mode
- **"Share a file"** — sibling dropdown item for file mode

### Share Files drawer

- **"Choose a folder or drag it here"** — dragger area label when folder mode is active
- **"Upload a folder"** — button label inside the upload files section
- **"Add items and Recipients"** — Step 1 heading in the drawer
- **"Select Policy"** — Step 2 heading
- **"Choose or Review Policy"** — Step 2 heading when a Platform Governance Rule has pre-assigned the policy

### Recipient roles (folder context)

The role selector shows these exact labels with folder-specific descriptions:

| Internal key | Display title | Folder description |
|---|---|---|
| `viewer` | **Viewer** | "Can view content" |
| `editor` | **Contributor** | "Can edit content" |
| `coOwner` | **Co-owner** | "Can add, edit, share content and read associated logs" |

> Note: The internal key `editor` maps to the user-facing label **Contributor** — the article must use "Contributor", not "Editor."

### Permissions & Policy drawer (post-share)

- **"Permissions & Policy"** — drawer title (used in both file row menu and info drawer header)
- **"Parent policy"** — label for the policy applied at the folder level; appears in the info drawer and in the permission drawer
- **"Who has access"** — section heading listing current recipients
- **"Add new recipient via email"** — field label for adding new recipients after share
- **"Search recipient by email or phone number"** — search field placeholder
- **"Revoke"** — action label on each recipient row
- **"policyChangeHint"**: "Adding and removing recipients can trigger policy change" — tooltip on the policy area

### My Files page (folder-related)

- **"My Files"** — page name
- **"New folder"** — dialog title when creating a folder
- **"Untitled folder"** — default folder name
- **"Create folder"** — button label in page header
- **"Add files"** — button label in page header
- **"View logs"** — folder context menu item
- **"View info"** — folder context menu item

### Folder upload / inheritance

- **"Users who have access to this {{folderType}} will have access to the files you add"** — info banner shown during upload to a shared folder (key: `uploadInfoText`). This is the UI confirmation of policy inheritance.
- **"Add Files to {{folderName}}"** — info text when adding files to an existing folder (key: `uploadFolderInfoText`)
- **"Folder {{folderName}} created"** — success toast on folder creation

### Recipient Page (folder share)

- **"Open folder"** — the primary action button shown to a recipient who receives a folder share link (key: `recipientPage.accessButtons.folder` and `recipientPage.actions.openFolderSecurely`)

### Error and validation messages

- **"You do not have permissions to share this file"** — 403 error shown in the share flow when the user lacks share permission
- **"You don't have permission to download some files. Rest will be downloaded"** — download error on recipient page
- **"We had an issue changing the permissions settings."** — error when saving permission changes in the drawer
- **"There was an error updating the file's policy"** — error when changing the policy

### Policy-locked state

- **"Assigned policy"** — label when a policy has been selected
- **"Policy is locked by an assign policy rule"** — shown when a PAR rule has locked the policy choice
- **"Assigned due to {{ruleName}}"** — shown below the policy name when a PAR rule assigned it

### Policy chooser

- **"Choose Policy"** — dropdown label in the policy step

---

## Feature flags

No feature-flag strings (`FEATURE_`, `featureFlag`, `isEnabled`) were found in `general.json` related to folder sharing. The folder share functionality does not appear to be gated.

---

## Routes / adjacent flows

Not determinable from the JSON content file alone. The share flow is driven from the **My Files** page via the **Share files** button. The folder variant is a mode switch inside the same Share Files drawer.

---

## Key component paths

For context during testing/UI recon:

- `src/stores/FilesListStore/helpers/folders.ts` — folder data model helpers
- `src/stores/FilesListStore/interfaces/folders.ts` — folder type definitions
- `src/stores/FilesListStore/FilesManager/BaseFileManagerModules/FoldersModule.ts` — folder operations
- `src/stores/UploadFilesStore/FolderUploader/FoldersTree.ts` — folder upload tree
- `src/stores/UploadFilesStore/FolderUploader/CreateFolderService.ts` — folder creation service
- `src/components/Common/CreateFolderModal/` — "New folder" dialog
- `src/components/FilesTable/PermissionDrawer/PermissionsView.tsx` — permission drawer with Parent policy and role selectors
- `src/components/FilesTable/PermissionDrawer/AddRecipientsView.tsx` — add recipients
- `src/components/UploadDrawer/UploadFiles/VirtualUploadList/UploadIntoFolderHint/` — inheritance hint shown when uploading into a shared folder
- `src/components/FilesTable/InfiniteScrollTable/FileInfoDrawer/FileInfoDetails/index.tsx` (line ~136) — conditional display: shows "Parent policy" for folders, "Security Level" for files

---

## UI drift assessment

The `general.json` file is the primary i18n source; no discrepancies between the folder-share strings and the article plan's topics were found. The "Parent policy" term used in the plan matches the UI exactly. The role names (Viewer, Contributor, Co-owner) match between the plan and the JSON.

`ui-drift-risk: low` — the strings are consistent with the article plan and with the `04-share-a-file` approved article which uses the same drawer infrastructure.
