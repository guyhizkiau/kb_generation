# Codebase findings — Securely share a file from the SpecterX web platform

Source corpus: `~/specterx-codebase/web-client/` (no admin-side strings consumed for this article).

## Canonical UI labels (file: `src/content/general.json`)

### My Files page entry points

| Code key | Label | Where it appears |
|---|---|---|
| `general.buttons.shareFiles` | **Share files** | Top-of-page primary action button on **My Files** |
| `fileActions.share` | **Share** | Per-row file action |
| `batchActions.share` | **Share selected** | Multi-select toolbar action |

### Share Files drawer — step labels

| Code key | Label | Stage in the flow |
|---|---|---|
| `shareDrawer.steps.addItemsAndRecipients` | **Add items and Recipients** | Step 1 |
| `shareDrawer.steps.selectPolicy` | **Select Policy** | Step 2 |
| `shareDrawer.steps.chooseOrReviewPolicy` | **Choose or Review Policy** | Step 2 alternate label when a policy is auto-assigned by a Platform Governance Rule |
| `upload.stepTitle` | **Upload File** | Sub-step inside Add items |
| `upload.clickOrDrag` | **Click or drag a file to this area to upload** | Empty state of the upload area |
| `share.stepTitle` | **Share Files** | Drawer title |
| `success.stepTitle` | **Confirm** | Final step heading |
| `success.sharingIsCaring` | **Sharing Successful.** | Toast/heading on success step |

### Recipient block (`sharingBlock`)

| Code key | Label |
|---|---|
| `sharingBlock.title` | **Share with** |
| `sharingBlock.input.placeholder` | **Insert email address and click `Enter`** |
| `sharingBlock.notifyRecipients.label` | **Notify recipients** |
| `sharingBlock.notifyRecipients.addMessage` | **Add message (Optional)** |

### Recipient permission tiers (the three roles)

Code branch: `sharingBlock.recipientRolesSelect`. **The UI label for the highest tier is "Co-owner", not "Co-Owner"** — note the lowercase `o`. The plan entry uses "Co-Owner" but the product UI is "Co-owner". Use the product label.

| Code key | UI title | File-context description |
|---|---|---|
| `viewer.title` | **Viewer** | Can view content |
| `editor.title` | **Contributor** | Can edit content |
| `coOwner.title` | **Co-owner** | Can share content and read associated logs |

Note that the description strings are the short ones that show in the role-select dropdown. The plan entry's longer description ("can view, upload, and download (subject to policy)") is editorial expansion, not a direct UI string.

### Policy block

| Code key | Label |
|---|---|
| `policyStep.choosePolicy` | **Choose Policy** |
| `policyStep.assignedPolicy` | **Assigned Policy** |
| `policyStep.policy` | **Policy** |

### Post-share success screen (`successScreen`)

| Code key | Label |
|---|---|
| `successScreen.filesSharedSuccessfullyWith` | **{filesCount} Files shared successfully with {ownerEmail}** |
| `successScreen.onDate` | **on {date}** |

### Copy link

| Code key | Label |
|---|---|
| `copyLink.copyLink` | **Copy Link** |
| `copyLink.copyLinkToClipboard` | **Copy link to clipboard** |
| `copyLink.creatingNewLink` | **Creating new link** |

### Share & Permissions Drawer (post-share management)

| Code key | Label |
|---|---|
| `permissionDrawer.parentPolicy` | **Parent policy** |
| `permissionDrawer.reviewExistingPermission` | **Review Existing Permission** |
| `permissionDrawer.addNewRecipients` | **Add New Recipients** |
| `permissionDrawer.editPermissions` | **Who has access** |

## Validation / blocker messages (verified strings)

These are the strings the **Share** button surfaces when it stays disabled:

| Code key | Message |
|---|---|
| `shareBlockers.isUploading` | **Some files are still uploading. Please wait until they finish uploading** |
| `shareBlockers.noFiles` | **Please add files to share** |
| `shareBlockers.noRecipients` | **Please add recipients to share** |
| `shareBlockers.missingRecipient` | **Recipient wasn't added. Please click on "Add" button** |
| `shareBlockers.missingRecipientInvalid` | **You have something into input. Would you like to add more recipients?** |
| `general.specterxCommon.invalidEmail` | **Invalid email address** |
| `sharingBlock.validation.cannotShareWithYourself` | **You already have access to this item** |
| `sharingBlock.validation.alreadyShared` | **You have already shared this file with {email}** |

### Phone-verification gating

When the selected policy requires phone verification, missing-phone-number messages surface:

| Code key | Message |
|---|---|
| `policyStep.missingPhoneNumber` | **One or more of the recipients' phone numbers are missing. Please complete them.** |
| `policyStep.invalidNumber` | **Some recipients has invalid phone numbers** (sic — the product string is slightly ungrammatical; do not quote in customer prose) |

### Share failure

| Code key | Message |
|---|---|
| `specterxCommon.couldNotShareFile` | **Unable to share file** |
| `specterxCommon.couldNotShareTryAgain` | **Unable to share files, please try again** |

## Feature flags affecting this article

A quick survey of `FEATURE_` / `featureFlag` patterns under `src/` did not surface flags that gate the basic share-file flow. Phone-verification and password-verification gating come from the *policy* (not a flag), so the user-visible behavior is policy-driven.

## Recently modified files (last ~6 months, share-related)

`src/components/UploadDrawer/UploadFiles/PolicyStep/` and `src/components/UploadDrawer/SuccessScreen/` both show heavy recent activity:

- `UploadDrawer/SuccessScreen/SharedFilesTable/index.tsx`
- `UploadDrawer/SuccessScreen/BlockedSummaryBar/index.tsx`
- `UploadDrawer/UploadFiles/PolicyStep/MissingDetails/MissingPasswordInput.tsx`
- `UploadDrawer/UploadFiles/PolicyStep/MissingDetails/MissingPhoneInput.tsx`
- `UploadDrawer/UploadFiles/RulesLoadingState/index.tsx`

**Implication for the article:** the policy step and the success step both moved recently. The screenshots should be captured fresh; do not rely on the previous attempt's `screenshots/06-recipient-added.png` to represent the current UI. Recapture during the test phase.

## Code-leak safety

No source code has been quoted in this file beyond key paths and i18n label keys. Source code does not enter `draft-1.md`.
