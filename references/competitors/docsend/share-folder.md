---
vendor: docsend
slug: share-folder
source_url: https://help.dropbox.com/organize/dropbox-docsend-create-a-space-data-room
title: Create a Space (data room) in Dropbox DocSend
captured: 2026-06-07
topics: [space, data room, share folder, granular permissions, visible, downloadable, watermark, NDA, expiration, allow list, block list, content folders]
---

# Coverage notes (paraphrased)

DocSend doesn't use the word "folder" for its sharing primitive — it uses "Space" (their virtual data room). The "Create a Space (data room)" article is the closest equivalent to a folder-share guide and is short (estimated 350-450 words, around 2-3 inline screenshots). It exists mostly as a router into other Space management articles. Plan gating is called out up front: Spaces only exist on DocSend Standard, Advanced, and Advanced Data Rooms; certain subfolder behavior only works on Advanced.

Concepts the create-Space article surfaces:

- Three creation paths: Spaces tab + Create Space button, Content library + select-folder + Share, Content library + multi-select + Share as Space.
- Renaming and subtitle support; rebrandable background and logo.
- A "share the folder link, files added later automatically appear" behavior — the equivalent of inheritance, but expressed as "add new files to the existing Space."
- Multiple links per Space, so the same content can be exposed to different audiences with different settings.
- Team visibility: Spaces created inside a team are visible (name + content) to all teammates.
- A Standard-plan limitation that explicitly excludes subfolder-of-subfolder structure from the share — Advanced lets you use "Space folders."

## Supporting article: Set granular space permissions in Dropbox DocSend

URL: https://help.dropbox.com/organize/dropbox-docsend-granular-space-permissions

A second, much denser article (estimated 1,200-1,500 words) that does the heavy lifting on the access-control model. This is where DocSend competes hardest with Egnyte's permission matrix, though framed entirely around external recipients rather than internal teammates.

- The unit of policy is the Space LINK, not the Space itself. One Space can have multiple links, each with its own settings, so the same content reaches different audiences with different controls.
- Per-link content controls, configurable for the whole Space or per item: Visible (show/hide), Downloadable (allow/deny), Watermark (PDFs), NDA (require accept before viewing).
- Link-level access controls separate from content controls: allow/block list of email addresses, watermark toggle, require NDA, require email authentication, expiration date, password, custom welcome message.
- A separate Groups concept for managing invited visitors: Manage access, watermark, NDA, "send reminder" emails to invitees who haven't shown up.
- An explicit hide-from-team workflow: making content "not Visible" hides it from external visitors only; to hide a file from your own team you have to physically move it from a team folder into a personal folder under "Auto-created Space Folders."
- A note that granular permissions OVERRIDE default Space-link settings — there's a precedence rule, not a merge.

## Reader framing

These two articles together read like documentation for someone running a fundraising or M&A data room, not a casual file-sharing user. Vocabulary is heavier ("granular permissions", "auto-created Space folders", "allow/block list", "visitor"). Plan-tier disclosures appear at the top of every article. Tone is procedural but mixed with reference-style toggle lists. Voice is imperative for the click paths, declarative for the model. The companion granular-permissions article carries the implicit "this is the differentiator" weight — the create-a-Space article is mostly a starting point that hands you off.
