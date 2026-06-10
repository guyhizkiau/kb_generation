---
vendor: dropbox
slug: share-file
source_url: https://help.dropbox.com/share/share-with-others
title: How to share in Dropbox
captured: 2026-06-08
captured_by: VM-Claude
search_query: "share a file"
selected_because: "Top end-user 'how to share a file or folder' article on Dropbox; covers file-and-folder sharing in a single unified flow, which is the closest match to SpecterX's share dialog."
topics: [share a file, share a folder, add people, edit access, view access, copy link, manage links, qr code, default sharing settings, recipient email, view-only link]
---

# Coverage notes (paraphrased)

Dropbox's "How to share in Dropbox" page is the canonical entry point for end-user sharing. It treats files and folders as a single unified flow: the same Share button, the same Add people dialog, the same edit/view-only choice. The page is medium length (estimated ~1,500 words across the in-line jump-list of nine sub-sections) and is **platform-tabbed** rather than article-split — every action is documented three times, once for `dropbox.com`, once for the Desktop app, and once for the Mobile app.

There are no inline product screenshots on this page. Dropbox relies entirely on bulleted text steps, with the "Share" button click as the universal starting point. UI labels are bolded inline.

## What the article covers (the canonical share flow)

For the share-with-specific-people path (the closest match to the SpecterX flow):

1. Hover over the file or folder, click Share.
2. Click Add people.
3. Type the recipient's email, name, or group; pick from autocomplete results.
4. Choose "can edit" or "can view".
5. Optionally add a message.
6. Click Share — recipients receive an email with the link.

## Concepts the article exposes inline

- **Two recipient access levels: edit vs view.** That's the only role split. Notably, this is *fewer* tiers than Egnyte (5) and SpecterX (3 sender-side + permission inheritance). Dropbox keeps it deliberately binary at the share dialog.
- **Two sharing modes: direct invite vs link.** Invite-by-email puts named people on the access list and sends them an email; "Copy link" creates a shareable URL. The two modes coexist on the same Share dialog.
- **Account requirement on invite-by-email.** To open a file shared by direct invitation, the recipient must have a Dropbox account and be signed in. That's a key UX gap SpecterX deliberately fills: SpecterX recipients never need a SpecterX account; they verify per share.
- **View-only links and a QR code option** as alternatives when the recipient doesn't have or doesn't want a Dropbox account.
- **Team-vs-individual rules** for who auto-joins shared folders.
- **Link settings (passwords, restrictions) only apply to link-access**, not to people directly invited. Direct invites keep their existing permissions. This is a subtle distinction Dropbox flags explicitly; SpecterX makes this simpler — the policy applies to everyone the file is shared with, regardless of how they got access.
- **Default sharing settings** as a separate administrative concept layered above per-share choices.

## Tone and reader framing

Written for someone already inside Dropbox, with a Dropbox account, who knows what "Share" means. Voice is consumer-friendly, second-person, imperative. Sentences are short. The article does not try to teach the security model — it treats sharing as a productivity action, not a governance action. No policy concept; no recipient-verification step; no audit-trail mention; no "revoke access" callout from this page (deferred to a separate article).

Notable absences compared to a security-product article:
- No mention of recipient verification or identity confirmation.
- No mention of how forwarding works once a link is out.
- No mention of expiry, watermarking, or download restrictions on this page (they exist in Dropbox at higher plan tiers but live in different articles).
- No mention of audit logging.
