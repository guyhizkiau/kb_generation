---
vendor: egnyte
slug: share-folder
source_url: https://helpdesk.egnyte.com/hc/en-us/articles/201637444-Folder-Permissions
title: Folder Permissions
captured: 2026-06-07
topics: [share folder, folder permissions, permission inheritance, access levels, subfolder access, group permissions, mobile sharing, viewer, editor, full, owner]
---

# Coverage notes (paraphrased)

Egnyte's "Folder Permissions" article is the canonical folder-sharing page and treats the action of "sharing a folder" as identical to "granting folder permissions" — the user reaches it from a Permissions icon at the top of a folder. The article is long (estimated 1,500-1,800 words) and reads more like a reference than a quickstart. It uses an inline jump-list of nine sub-sections at the top so readers can land on the part they need (add a domain user, add to an existing group, invite a new external user, remove access, notifications, access-level reference, subfolder behavior, mobile, on-prem sync).

Concepts introduced or assumed: a Shared folder hierarchy that organization data lives under; five access levels (Viewer-Only in limited availability, Viewer, Editor, Full, Owner) with a detailed capability matrix; permission inheritance from parent to subfolder by default; the ability to disable inheritance on a specific subfolder; group membership as the recommended way to scale permissions; explicit user grants overriding group grants when both apply; "permission precedence" where the higher level wins across multiple group memberships; "Non-Inherited Permissions" as a separate page that owners use to lock down sensitive subtrees; and a clearly stated rule that adding a new user to a folder gives them immediate access to all subfolders that inherit from it.

The article also covers some specifically external-sharing concerns: inviting a brand-new user from inside the permissions dialog (Username + Email required, user type defaults to Power User, permission defaults to Viewer), bulk-invite gated to Document Room / Enterprise Lite plans, and an email notification sent to the affected user every time their access is granted, altered or revoked. Egnyte calls this last feature "limited availability" and explicitly notes that group-membership and inheritance changes do NOT trigger the notification.

Reader framing: the article is written for a folder owner or admin who is already inside Egnyte; it does not re-explain the product. It assumes the reader can navigate to a folder, click an icon, and understand "Power User vs. Standard User vs. Administrator." Tone is procedural and dense; voice mixes imperative ("Navigate to the folder", "Click Add") with reference text ("The default permission is set to Viewer"). Estimated 6-10 inline screenshots covering the Permissions dropdown, the search bar with autocomplete, the "Invite new user" form, the access-level matrix table, the three notification email variants, and a mobile-app sequence.

# Supporting article: Additional Details on Folder Sharing

URL: https://helpdesk.egnyte.com/hc/en-us/articles/201637254-Additional-Details-on-Folder-Sharing

A short companion (≈400 words) that uses worked examples instead of UI screenshots to explain four behaviors users hit in practice:

- Folders and the files inside them are completely invisible to users who have not been shared in (admins are the only exception).
- Inheritance is the default: sharing a parent shares every subfolder.
- A subfolder can be shared with someone who does NOT have access to the parent — they see the parent as a greyed navigation path with no files, only the subfolder they're entitled to.
- Exclusion: an admin can remove a user from a specific subfolder under a shared parent (e.g. lock User B out of /Sales/Accounts while keeping them in /Sales/Collateral). This shows up as a "None" record in the Folder Permissions Report.
- When a user is granted access directly AND via a group, the direct user-level grant wins.

# Supporting article: Shared and Private Folders

URL: https://helpdesk.egnyte.com/hc/en-us/articles/201637174-Shared-and-Private-Folders

A short reference page (≈350 words) that frames the top-level taxonomy: every Egnyte domain has a "Shared" root that holds all collaborative content, plus optional per-user "Private" subfolders. Notes the Shared folder cannot be renamed, re-permissioned, or deleted; files can never live directly at the Shared root (always inside a subfolder). Includes a side-by-side comparison table of Shared vs. Private across naming, draft mode, who can create files, ownership, access levels, visibility, and collaboration intent. Worth noting because it establishes the implicit mental model the main folder-sharing article relies on.
