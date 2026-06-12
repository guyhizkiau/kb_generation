# UI glossary — Share a folder
# Captured: 2026-06-11T00:00:00Z (codebase-derived; no live browser available)
# SpecterX build: n/a — strings from web-client/src/content/general.json
# Browser: not captured (no Playwright or CDP endpoint in this environment)
# Viewport: n/a

> **Note:** No live browser screenshots were captured. This glossary is derived entirely
> from `web-client/src/content/general.json`. All labels have been verified against the
> approved `04-share-a-file` article, which uses the same drawer infrastructure. Screenshots
> must be captured during the test phase or a later manual recon pass.

---

## Surface: My Files page (`/my-files`)

### Top-level navigation and header actions

- **My Files** — page title (main navigation item)
- **Add files** — button in page header
- **Create folder** — button in page header
- **Share files** — button in page header (opens Share Files drawer)
- **Refresh** — button in page header
- **To root** — navigation button

### Folder row actions (context menu or row icons)

- **Share** — opens the Share Files drawer or Share & Permissions drawer for the folder
- **View logs** — opens audit log for the folder
- **View info** — opens the info/details drawer
- **Create folder** — creates a subfolder
- **Delete** — deletes the folder

---

## Surface: Share Files drawer (folder mode)

### Drawer header / step indicators

- **Add items and Recipients** — Step 1 heading
- **Select Policy** — Step 2 heading (standard flow)
- **Choose or Review Policy** — Step 2 heading (when a Platform Governance Rule pre-assigns the policy)

### Step 1: Upload area

- **Share a folder** — dropdown item that switches the dragger to folder mode
- **Share a file** — sibling dropdown item
- **Choose a folder or drag it here** — dragger label in folder mode
- **Upload a folder** — button label

### Step 1: Recipient block ("Share with")

- **Share with** — section title
- **Insert email address and click `Enter`** — input field placeholder
- **Notify recipients** — checkbox label (sends notification email on share)
- **Add message (Optional)** — label for optional personal message to recipients

### Step 1: Role selector (per recipient)

- **Viewer** — role option; folder description: "Can view content"
- **Contributor** — role option; folder description: "Can edit content"
- **Co-owner** — role option; folder description: "Can add, edit, share content and read associated logs"

### Step 2: Policy

- **Choose Policy** — dropdown label
- **Assigned policy** — label when a policy has been selected or pre-assigned
- **Assigned due to [rule name]** — shown when a PAR rule assigned the policy
- **Policy is locked by an assign policy rule** — warning when the policy cannot be changed
- **Setting up secure sharing** — loading state heading while PAR evaluates

### Step 3: Confirmation

- **Shared successfully** — success heading
- **Shared items** — column in confirmation table
- **Shared with** — column in confirmation table
- **Role** — column in confirmation table
- **Policy** — column in confirmation table
- **Copy link** — action in confirmation table per recipient
- **Done** — close button

---

## Surface: Permissions & Policy drawer (post-share)

Accessed from the share icon on the folder row in My Files.

### Drawer header

- **Permissions & Policy** — drawer title
- **Who has access** — toggle that shows recipient list

### Recipient list

- **Users with access** — section heading
- **No existing recipients** — empty state
- **Add new recipient via email** — field label for adding a new recipient
- **Search recipient by email or phone number** — search field placeholder
- **Role** — column header for permission level
- **Revoke** — action per recipient row

### Policy section

- **Parent policy** — label for the folder's active policy; this is the policy inherited by all files inside the folder
- **Choose Policy** — dropdown when changing the policy
- **Adding and removing recipients can trigger policy change** — tooltip hint

### Revocation modal

- **Revocation Warning** — modal title
- **Revoke access for [email]?** — modal heading
- **This will immediately remove all permissions from this recipient. This action cannot be undone.** — modal body
- **Revoke** — confirm action

---

## Surface: Folder info drawer

Accessed via "View info" on the folder row.

- **Owner** — field label
- **File Size** — field label
- **Folder** — field label (parent path)
- **Changed** — field label (last modified)
- **Created** — field label
- **Security Level** — field label
- **Parent policy** — field label showing the folder's current policy
- **Who has access** — section listing recipients
- **Manage access** — link to open the Permissions & Policy drawer
- **Share** — button if the folder is not yet shared

---

## Surface: Recipient Page (folder share)

What the recipient sees after clicking a shared folder link.

- **Open folder** — primary action button (equivalent to "Open files securely" for a file share)
- **{{sender}} shared a file with you** — greeting subject line (may read as "files" for a folder)

---

## Surface: Create Folder dialog

- **New folder** — dialog title
- **Untitled folder** — default folder name pre-filled in the name field
- **Folder name should not be empty** — validation error
- **Folder name should not start with [chars]** — validation error for invalid characters
- **Creating new folder...** — loading state

---

## Proposed glossary additions

Terms seen in the UI that are not in `canon/GLOSSARY.md`:

1. **Parent policy** — The security policy applied at the folder level; all files inside the folder inherit this policy by default. Files with an explicit per-file policy override the parent.
2. **Share a folder** — The action of sharing a SpecterX folder with recipients, applying a policy that governs access and security for all contents.
3. **Co-owner** (folder context) — A recipient role for folder shares; a Co-owner can add, edit, share content, and read the folder's audit logs.
4. **Contributor** (folder context) — A recipient role for folder shares; a Contributor can edit content.

## Canon terms confirmed in the UI

- **My Files** — matches `canon/GLOSSARY.md` usage in `04-share-a-file`
- **Viewer** — matches plan and `04-share-a-file`
- **Contributor** — matches plan and `04-share-a-file`
- **Co-owner** — matches plan (plan uses "Co-Owner" with capital O; UI uses "Co-owner" with lowercase o)

> **Flag:** The article plan writes "Co-Owner" (capital O) but the UI label in `general.json` is "Co-owner" (lowercase o). Use the UI label "**Co-owner**" in the article.

## Canon drift flags

No terms were found in `canon/GLOSSARY.md` that conflict with what the codebase shows. The glossary is minimal (only tenant URL guidance), so no drift is possible yet.
