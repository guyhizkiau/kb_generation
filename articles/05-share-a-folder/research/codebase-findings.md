# Codebase findings — Share a folder

Repo paths searched:
- `~/specterx-codebase/web-client/` (end-user web app)
- `~/specterx-codebase/admin-web-client/` (admin app — no end-user folder-share surface; skipped)

The web-client only has one i18n bundle: `src/content/general.json` (and a Hebrew copy). There is no `src/locales/` or `src/i18n/` directory.

## UI strings (canonical labels)

End-user labels related to folders and sharing, from `web-client/src/content/general.json`:

- Share menu / dragger
  - L161 `draggerDropdownFile`: "Share a file"
  - L162 `draggerDropdownFolder`: "Share a folder"
  - L160 `draggerFolder`: "Choose a folder or drag it here"
- My Files header buttons (L599-607)
  - L602 `createFolder`: "Create folder"
  - L603 `refresh`: "Refresh"
  - L604 `shareFiles`: "Share files"
  - L605 `auditFolder`: "View logs"
  - L606 `folderInfo`: "View info"
- Create folder (L465-484)
  - L466 `title`: "New folder"
  - L468 `untitledFolder`: "Untitled folder"
  - L472 `emptyName`: "Folder name should not be empty"
  - L474 `createFolder` (error): "Unable to create folder {{folderName}}"
  - L477 `createFolder` (success): "Folder {{folderName}} created"
- Upload-into-folder hints (L513-575)
  - L514 dragger hint: "Drag file or folder into this area to upload"
  - L521 `uploadFolder`: "Upload a folder"
  - L574 `uploadInfoText`: "Users who have access to this {{folderType}} will have access to the files you add"
  - L575 `uploadFolderInfoText`: "Add Files to {{folderName}}"
- Batch share button (L1502-1503)
  - L1503 `batchActions.share`: "Share selected"
- Recipient roles — folder-specific descriptions (L1590-1626)
  - L1592 viewer.title: "Viewer", folder.description (L1597): "Can view content"
  - L1604 editor.title: "Contributor", folder.description (L1609): "Can edit content"
  - L1616 coOwner.title: "Co-owner", folder.description (L1621): "Can add, edit, share content and read associated logs"
- Permission Drawer — folder-specific (L1317-1346)
  - L1318 `choosePolicy`: "Choose Policy"
  - L1319 `assignedPolicy`: "Assigned policy"
  - L1323 `usersWithAccess`: "Users with access"
  - L1329 `addRecipientEmail`: "Add new recipient via email"
  - L1330 `addNewRecipients`: "Add New Recipients"
  - L1345 `parentPolicy`: "Parent policy" — used when item being shared is a folder
  - L1346 `policyChangeHint`: "Adding and removing recipients can trigger policy change"
- File info drawer (L1408-1424)
  - L1410 `whoHasAccess`: "Who has access"
  - L1411 `manageAccess`: "Manage access"
  - L1412 `fileNotShared`: "Item is not shared"
  - L1413 `shareFile`: "Share"
  - L1419 `folder`: "Folder"
  - L1422 `securityLevel`: "Security Level"
  - L1423 `parentPolicy`: "Parent policy"
- Recipient page (folder access) (L201, L229-230)
  - L201 `recipientPage.accessButtons.folder`: "Open folder"
  - L229 `openWorkspacesSecurely`: "Open workspace"
  - L230 `openFolderSecurely`: "Open folder"

## Feature flags affecting folder sharing

No dedicated feature flag for folder sharing was found. Grep across `web-client/src` for `FEATURE_FLAG`, `featureFlag`, `feature_flag` returned no matches relevant to folders. The only `isEnabled` hit (`stores/PolicyStore/index.ts:393`) is the policy editor's "limit-to-users" toggle, unrelated to folder share gating. Folder share UI is always available — gating is at the data layer (permission/role check on the folder itself).

## Folder-share specific behavior (PARENT POLICY / INHERITANCE)

The folder's own policy is rendered as "Parent policy" rather than "Choose Policy" or "Security Level". This is the visible signal of folder-to-child inheritance.

- `web-client/src/components/FilesTable/PermissionDrawer/PermissionsView.tsx:231-236` — the section header switches: if `isFolder` it shows `parentPolicy`; otherwise `assignedPolicy` (when locked by a rule) or `choosePolicy`.
- `web-client/src/components/FilesTable/PermissionDrawer/AddRecipientsView.tsx:73-77, 239-249` — per-file "variant" resolution returns `'parent'` for any folder (otherwise `'choose'` or `'assigned'`); `getSectionTitle('parent')` returns `parentPolicy`.
- `web-client/src/components/FilesTable/InfiniteScrollTable/FileInfoDrawer/FileInfoDetails/index.tsx:136` — info drawer labels the policy block as `parentPolicy` when the item is a folder, otherwise as `securityLevel`.
- `web-client/src/components/FilesTable/PermissionDrawer/index.tsx:375-394, 444-456` — when sharing a folder, the drawer fetches the folder's children via `?parent_folder=<fid>` and tracks: total `folderFileCounts`, child names (`folderChildNames`), and child files that already have a rule-assigned policy (`ruleAssignedChildren`). The view then shows the parent policy AND a separate section listing children whose policy was locked by a rule.

So inheritance is implemented as: the folder's `policy_id` is the default for new and existing children, but a child file can override (rule-assigned policies are shown as locked groups under the parent policy).

## Permission interactions with folders

- Folder children are fetched on demand for the share UI via `GET /…?parent_folder=<fid>` (`PermissionDrawer/index.tsx:377`, `446`).
- `sharedUsersStore.fetchSharedUsers(file.fid, …)` is called for the folder itself; when multi-sharing the drawer also calls `getFilePermissions` per file and computes the intersection ("shared with all") to seed recipients (`PermissionDrawer/index.tsx:368-414`).
- The Hebrew/English upload hint (`uploadInfoText`, L574) is the explicit user-facing statement: "Users who have access to this {{folderType}} will have access to the files you add." This is rendered when uploading into a workspace/folder (`UploadIntoFolderHint.tsx:20-22`).
- Role descriptions for `folder` (L1596-1622) are the same as `file` for Viewer ("Can view content") and Contributor ("Can edit content"), but Co-owner on a folder gains "add" rights: "Can add, edit, share content and read associated logs."
- No client-side cascade logic was found for downloading individual files when a Viewer of a folder opens a child — the check happens server-side (the codebase only labels things as `viewer` and routes to the file's own permission check).

## Recipient experience for shared folders

When a recipient opens a share link to a folder:

- `usePossibleRedirectToFolder.ts` (RecipientPage hook) auto-redirects to the folder browser when the link contains a single folder/workspace, MFA is satisfied, and the recipient has `permissionsAdded` summary. It suppresses the redirect for ~N ms right after login (to avoid race with auth params in the URL).
- `getPathToSharedFolder.ts` chooses the destination:
  - If the recipient owns the folder → route to `AppRoutes.myFiles?folderId=<fid>`.
  - Otherwise → `AppRoutes.sharedWithMe?folderId=<fid>`.
- If no auto-redirect, the carousel renders `FolderView/index.tsx` showing a folder icon and a link labeled "Open folder" (`recipientPage.accessButtons.folder`, L201). The link opens the same My Files / Shared With Me route in a new tab.
- The "Open folder securely" CTA (L230) is the recipient-side text equivalent of "Open file securely".

## Error messages (for troubleshooting section)

Surface strings, from `web-client/src/content/general.json`:

- L1575 `cannotShareWithYourself`: "You already have access to this item"
- L1576 `cannotShareWithOwner`: "You can't share with file owner"
- L1579 `alreadyShared`: "You have already shared this file with {{email}}"
- L1649 `shareBlockers.isUploading`: "Some files are still uploading. Please wait until they finish uploading"
- L1650 `shareBlockers.noFiles`: "Please add files to share"
- L1652 `shareBlockers.noRecipients`: "Please add recipients to share"
- L1666 `shareEditPolicy.result.success`: "Shared files successfully"
- L1679 `giveAccess.shareResult.noPermissions`: "You do not have permissions to share this file"
- L97 `couldNotShareFile`: "Unable to share file"
- L100 `couldNotShareTryAgain`: "Unable to share files, please try again"
- L474 `createFolder.error.createFolder`: "Unable to create folder {{folderName}}"
- L494 `uploadFiles.error.couldNotCreateFolder`: "Unable to create folder {{folderName}}"
- L498 `uploadFiles.error.setPolicyError`: "Cannot set policy to the file. Please try again in a few minutes."
- L505 `uploadFiles.error.couldNotNotify`: "Could not notify workspace owner"
- L1378 `failed_policy`: "There was an error updating the file's policy"
- L1379 `failed_shareSettings`: "We had an issue changing the permissions settings."
- L1380 `failed_all`: "We had an issue changing the file's security settings."
- L1399 `loadingError`: "Error Loading Policy..."
- L1400 `savingError`: "Error saving file policy..."
- L4 `403`: "You don't have permissions for this operation."
- L223 `downloadPermissionFailed`: "You don't have permission to download some files. Rest will be downloaded"

## Adjacent components / flows worth knowing

- `web-client/src/components/MyFiles/MyFilesHeader/ExtraContent/BatchShareButton/index.tsx` — "Share selected" toolbar button (icon `SendOutlined`). On click it sets `appStore.requestShareSelectedFiles()` (a flag observed elsewhere in the app that opens the share drawer with the currently selected items). This is how a user shares a folder they've selected in the My Files grid.
- `web-client/src/components/MyFiles/MyFilesHeader/ExtraContent/OpenFolderInfoButton/index.tsx` — "View info" button (icon `InfoCircleOutlined`) for the current folder; opens the file/folder info drawer for the current folder by calling `setChosenTableFileId(currentFolderId)`. The info drawer then shows owner, created/changed, folder name, "Parent policy" select, and the "Who has access" list — i.e., it is the entry point for managing folder sharing without leaving My Files.
- `web-client/src/components/MyFiles/MyFilesHeader/FolderBreadcrumbs/index.tsx` — renders breadcrumbs above the file list using `filesListStore.currentFolderBreadcrumbs`; breadcrumbs are clickable `FolderLink`s and droppable (drag-to-move) when in `myFiles` view. The root crumb label depends on display type ("My Files" / "Shared With Me" / "All Files"). Not directly involved in sharing, but is the navigation context the user sees while sharing a folder.
- `web-client/src/components/ExternalStorage/ShareLink/index.tsx` — Small block that renders a divider + "Copy Link" title (`externalStorage.shareLink.title` L1044) over a `CopyFileLink`. Used inside the external-storage share success flow, not the in-app folder share success screen.
- Folder-specific success table behavior: `web-client/src/components/Common/SuccessScreen/SharedFilesTable/index.tsx` and `web-client/src/components/UploadDrawer/SuccessScreen/SharedFilesTable/index.tsx` both expand a shared folder row into a folder header + its child file rows, applying the folder's policy to children unless a rule overrode the child's policy.

## Recently modified (last 90 days)

Output of `git log --since="90 days ago" --name-only --pretty=format: -- 'src/components/**Share**' 'src/components/**Folder**' 'src/stores/SharedUsersStore'`:

- `src/components/Common/SuccessScreen/SharedFilesTable/index.tsx` (+ scss)
- `src/components/FilesTable/Modals/ShareModal/ShareFile.tsx`
- `src/components/FilesTable/Modals/ShareModal/ShareSettings.tsx`
- `src/components/FilesTable/Modals/ShareModal/index.tsx`
- `src/components/FilesTable/Modals/ShareSettingsTable/index.tsx`
- `src/components/MyFiles/MyFilesHeader/ExtraContent/BatchShareButton/index.tsx` (+ scss)
- `src/components/UploadDrawer/SuccessScreen/SharedFilesTable/index.tsx`
- `src/components/WorkspaceDrawer/ShareWorkspace/WorkspaceNameBlock/index.tsx` (+ scss)
- `src/stores/SharedUsersStore/index.ts`
- `src/stores/SharedUsersStore/constants.ts`

Also active in the same window (broader Permission Drawer area, where folder-share UI lives): `FilesTable/PermissionDrawer/*` — commits SPX-5525, SPX-5575, SPX-5604, SPX-5605, SPX-5618, SPX-5654, SPX-5763, SPX-5976, SPX-5994 ("implement permission drawer", "support multiple files handling", "fixes for permission drawer", "UI styles"). This is the drawer that distinguishes "Parent policy" (folder) from "Choose policy" / "Assigned policy" (file).

## Items NOT found

- No feature flag specifically gating folder sharing.
- No string literal "Share folder" or "Folder permissions" header. The Permission Drawer reuses the same title (`shareDialog_WhoHasAccess`, "Users with access") for files and folders; the only folder-aware UI swap is `parentPolicy` ↔ `choosePolicy`/`securityLevel`.
- No "policyInheritance" / "inheritPolicy" identifier — inheritance is conveyed by the "Parent policy" label and by computing rule-locked child groups, not by an explicit inheritance toggle.
- `admin-web-client` has no end-user folder-sharing surface; its only folder-related strings concern admin policy explainers about the recipients' "Shared with me folder".
