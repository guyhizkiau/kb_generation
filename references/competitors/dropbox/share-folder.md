---
vendor: dropbox
slug: share-folder
source_url: https://help.dropbox.com/share/share-file-or-folder
title: How to share files or folders in Dropbox
captured: 2026-06-07
topics: [share folder, editor access, viewer access, shared link, file request, team folder vs shared folder, subfolder sharing, ownership]
---

# Coverage notes (paraphrased)

Dropbox's top-of-funnel "How to share files or folders in Dropbox" page is short (estimated 350-450 words) and treats files and folders as one unified flow. It opens with a three-question decision ladder the reader is asked to answer before doing anything: do you want them to edit, do you want them to view only, or are you actually trying to collect files from them? Each branch is described in 2-4 sentences and then deferred to a dedicated sub-article ("Learn how to share a folder", "Learn how to share a link", "Learn how to create a file request"). There are no step-by-step screenshots on this page — it functions as a router.

Key concepts surfaced inline:

- Edit vs. view-only access as the basic split, with edit access including add/edit/download/delete/share-link privileges.
- "Invitation by email from your Dropbox account" vs. "create a link" as two separate sharing modes.
- A team-vs-individual rule: people on individual accounts must explicitly accept a shared folder; teammates on the same Dropbox team auto-join personal folders shared internally.
- Plan-gated extras (Professional / Standard / Business / Advanced / Business Plus / Enterprise): branded invitation emails, and team-level controls over how members may share links.
- A pointer for admins to "manage sharing settings for your team."

## Supporting article: Dropbox Shared Folders FAQs

URL: https://help.dropbox.com/share/shared-folder-faq

A longer FAQ (estimated 1,000-1,200 words) structured as ten Q&A blocks. This is the page Dropbox uses to explain the conceptual model behind sharing:

- Parent folder / subfolder definitions stated up front.
- "Team folders vs. shared folders" gets the most ink: team folders are for ongoing, org-wide collaboration with admin-managed access, file storage that counts against team quota, and member-list reuse without re-sharing; shared folders are for short-term collaboration, individually picked members, files counting against each member's quota.
- Ownership rules: the owner of a parent shared folder automatically owns every subfolder, including new ones, even those created by someone else; transferring ownership has to happen at the parent level.
- A "Can I move a shared folder into another shared folder?" answer with platform-specific instructions for the web app and the iOS/Android mobile app — but explicitly NOT the desktop app.
- "Can I unshare?" rule: only possible if the folder has no shared folders inside it AND isn't itself nested inside another shared folder.
- "Why can't I create a shared folder?" gives a numbered list of seven reasons: limit reached, unverified email, admin disabled external sharing, admin disabled top-level shared-folder creation, sharing-suspended account, third-party app-folder incompatibilities (three sub-cases).
- Hard quotas surface here: max 1,500 shared subfolders inside any single parent and 30,000 shared folders across an account.

## Supporting article: Can I share a subfolder inside a shared folder?

URL: https://help.dropbox.com/share/share-inside-folder

A very short page (≈200 words) that answers a single question. The interesting content is the access-tier mapping: parent-folder owner can re-share any subfolder freely; parent-folder editor can re-share a subfolder only if the owner granted that capability; parent-folder viewer can only generate a view-only link. Adds a special-case note: Dropbox Family plan can't re-share subfolders at all and must fall back to link sharing.

## Reader framing

The three pages stack as a funnel: a router page, an FAQ that explains the data model, and a narrow Q&A page that handles an edge case. Tone is consumer-friendly and short-sentence, addresses "you" directly, uses imperative voice for steps. Almost no screenshots on these three pages — Dropbox relies on text-only steps and pushes UI walkthroughs into the linked sub-articles. The reader is assumed to know what a folder is; the only "concept teaching" is the team-vs-shared distinction.
