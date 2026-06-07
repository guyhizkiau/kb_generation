---
vendor: virtru
slug: share-folder
source_url: https://support.virtru.com/hc/en-us/articles/360026244833-Security-Option-Persistent-File-Protection-PFP
title: Security Option — Persistent File Protection (PFP)
captured: 2026-06-07
topics: [folder protection proxy, persistent file protection, PFP, secure share, secure reader, revoke access, request access, re-shared attachments, TDF]
---

# Coverage notes (paraphrased)

Virtru does not have a "share a folder" article. Virtru's data model is file-centric: the unit of protection and revocation is an individual file (wrapped as a `.tdf.html`), not a folder. The closest equivalent article — and the one searches for "folder protect", "share folder" surface — is the Persistent File Protection (PFP) page. It is worth capturing because it shows what a competitor that has no folder primitive does instead, and the gaps that creates relative to a folder-policy product like SpecterX.

Estimated length 700-900 words, structured around six sub-headings (Email Clients, Secure Share, Control Center, Recipient Experience, Request Access Workflow, Re-Shared Attachments). 4-6 inline screenshots, mostly of the email-compose security menu and the Secure Share wizard.

Concepts the article does cover that are relevant to folder-policy thinking:

- A persistent wrapping/encryption applied per-file at send time, with a downloadable Secure Reader link as the access path.
- A short list of supported file types (DOCX/PPTX/XLSX, JPEG/PNG, PDF) and an explicit list of UNSUPPORTED types (.doc/.ppt/.xls/.txt/.csv/.msg/.zip/.md). This kind of "what happens to unsupported files when you batch-share" question would matter on a folder share but Virtru handles it per-attachment with a "continue without PFP on this one" prompt.
- Settings that travel with the file regardless of where it ends up: revoke at any time, expire, watermark, prevent download. These can be set at send time OR retroactively from the Control Center.
- A Request Access workflow: an unauthorized recipient can ask the owner for access, owner approves/denies in the Control Center.
- "Re-Shared Attachments": when someone other than the original owner forwards a protected file, the file keeps its policy and the forwarder cannot change the privacy settings. This is the closest Virtru gets to the SpecterX idea of "policy follows the asset."

Concepts the article does NOT cover, and which a folder-sharing article on a folder-native product would need to:

- No notion of a container that other files inherit a policy from.
- No "uploads to this location get protected automatically" flow (Virtru's drag-and-drop-into-folder integration with Drive/Box/SharePoint is mentioned elsewhere on the marketing site but is not in the support KB as a how-to).
- No collaborator/permission model — recipients are recipients, not folder members; there are no Viewer/Contributor/Co-Owner tiers.
- No browsing UI for recipients: each file opens in the Secure Reader as its own session.

Reader framing: written for an existing Virtru user composing or managing a secure email/Secure Share. Assumes the reader knows the Virtru toggle, the Secure Share wizard, and the Control Center. Voice is procedural and product-marketing-adjacent ("PFP gives you a downloadable link…"). The article reads more like a feature spec than a task tutorial.
