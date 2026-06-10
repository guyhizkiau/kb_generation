# UI glossary — Securely share a file from the SpecterX web platform

- Captured: 2026-06-08 (codebase-derived; live screenshots are
  captured fresh in the test phase under `screenshots/_all/`).
- Source: `~/specterx-codebase/web-client/src/content/general.json` —
  the i18n keys that ship with the production tenant.
- SpecterX build: unknown from the live UI; no version string is
  exposed on the dashboard chrome. Treat as "live production as of
  2026-06-08."

## Page: My Files (`/my-files`)

The post-sign-in landing page for an end user with an active session.

Visible primary actions in the page header / toolbar:

- **Share files** — primary button. Opens the Share Files drawer.
  (Code: `general.buttons.shareFiles`.)
- **Upload File** — the same drawer is reached by selecting the
  "Upload" sub-step inside the Share Files drawer; there is no
  separate top-level Upload button distinct from Share files in the
  build the codebase reflects.
- Per-file row, a three-dot or icon menu exposes **Share** for an
  existing file. (Code: `fileActions.share`.)
- Multi-select toolbar exposes **Share selected**.
  (Code: `batchActions.share`.)

## Drawer: Share Files

The drawer that opens when the user clicks **Share files**. Title:
**Share Files** (Code: `share.stepTitle`).

The drawer has a step indicator at the top with these step labels:

1. **Add items and Recipients** — combined upload + recipient step.
2. **Select Policy** (or **Choose or Review Policy** when a Platform
   Governance Rule pre-assigns a policy).
3. **Confirm** — final summary + success screen.

### Step 1 — Add items and Recipients

Sub-block: file upload area.
- Empty-state text: **Click or drag a file to this area to upload**
  (Code: `upload.clickOrDrag`).
- "Choose a file or drag it here" alternate label exists in the
  generic dragger (`uploadDragger.draggerFile`).

Sub-block: **Share with** (the recipient block; Code: `sharingBlock.title`).
- Recipient input placeholder: **Insert email address and click
  `Enter`** (Code: `sharingBlock.input.placeholder`). The placeholder
  literally renders the word "Enter" in backticks.
- Add control / button: when an email is partially typed the user
  must commit it by pressing Enter or clicking **Add**.
- Per-recipient row: shows the recipient's email plus a role dropdown.

Recipient role dropdown values (Code: `sharingBlock.recipientRolesSelect.*.title`):

| Role | UI label | File-context description (from `.file.description`) |
|---|---|---|
| viewer | **Viewer** | Can view content |
| editor | **Contributor** | Can edit content |
| coOwner | **Co-owner** | Can share content and read associated logs |

**The product label for the highest tier is "Co-owner"** (lowercase
`o`). Use this casing in the article and not "Co-Owner" from the plan.

Other Step-1 controls:
- **Notify recipients** toggle (Code: `notifyRecipients.label`).
- **Notify new recipients** label variant (Code: `notifyRecipients.labelNew`).
- **Add message (Optional)** secondary action (Code:
  `notifyRecipients.addMessage`).

### Step 2 — Select Policy

- Heading: **Select Policy** (or **Choose or Review Policy** when a
  governance rule has pre-assigned the policy).
- Policy dropdown labelled **Choose Policy** (Code:
  `policyStep.choosePolicy`); selected state shows the policy name
  as the dropdown value.
- When the selected policy requires phone (SMS) verification, the
  recipient list reappears with an "Add phone number" affordance
  per recipient (Code: `sharingBlock.recipientsList.addPhone`). A
  banner with text **One or more of the recipients' phone numbers
  are missing. Please complete them.** appears at the top until all
  required phone numbers are entered (Code:
  `policyStep.missingPhoneNumber`).
- When the policy requires a personal-secret / password verification,
  an "Add password" affordance appears per recipient with similar
  banner messaging (Code: `policyStep.missingPassword`,
  `sharingBlock.recipientsList.addPassword`).

### Step 3 — Confirm / success

- Heading: **Confirm** (Code: `success.stepTitle`).
- Success message: **Sharing Successful.** (Code:
  `success.sharingIsCaring`).
- Detail line: **{N} Files shared successfully with {ownerEmail}**
  (Code: `successScreen.filesSharedSuccessfullyWith`).
- **Copy Link** action button (Code: `copyLink.copyLink`).

## Drawer: Share & Permissions (post-share management)

Opens from a share icon on an already-shared file in My Files.

- Heading: **Who has access** (Code:
  `permissionDrawer.editPermissions`).
- Sub-block titles: **Add New Recipients** / **Review Existing
  Permission** (Code: `permissionDrawer.addNewRecipients`,
  `permissionDrawer.reviewExistingPermission`).
- Policy dropdown labelled **Parent policy** (Code:
  `permissionDrawer.parentPolicy`).
- Per-recipient row: same role dropdown (Viewer / Contributor /
  Co-owner) plus a **Revoke** action.

## Validation / blocker copy

When the **Share** button stays disabled at the end of the flow, the
UI surfaces one of these messages (Code: `shareBlockers.*`):

- **Please add files to share** (`noFiles`).
- **Please add recipients to share** (`noRecipients`).
- **Recipient wasn't added. Please click on "Add" button**
  (`missingRecipient`).
- **You have something into input. Would you like to add more
  recipients?** (`missingRecipientInvalid` — slightly ungrammatical;
  do not quote in prose).
- **Some files are still uploading. Please wait until they finish
  uploading** (`isUploading`).

Inline validation while typing a recipient (Code:
`sharingBlock.validation.*`):

- **Invalid email address**
- **You already have access to this item** (sharing with yourself)
- **You have already shared this file with {email}**
- **Email already added**

## Diff against `canon/GLOSSARY.md`

`canon/GLOSSARY.md` is empty (no terms defined yet). New terms this
article proposes for the glossary:

- **Share Files drawer** — the multi-step drawer that opens from the
  Share files button in My Files.
- **Share & Permissions Drawer** — the drawer that opens from the
  share icon on an already-shared file in My Files. Used to
  add/remove recipients, change permission levels, or change the
  parent policy.
- **Parent policy** — the policy applied to a file (or folder) as
  shown in the Share & Permissions Drawer.
- **Viewer / Contributor / Co-owner** — the three recipient role
  tiers. Note casing on "Co-owner".

These get filed during stage 5 post-merge if approved.
