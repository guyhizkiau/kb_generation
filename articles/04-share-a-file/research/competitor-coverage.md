# Competitor coverage checklist — Securely share a file from the SpecterX web platform

## Articles read end to end

- **Dropbox — "How to share in Dropbox"** (`references/competitors/dropbox/share-file.md`, cached 2026-06-08, ~1,500 words, 0 inline screenshots, platform-tabbed for web/desktop/mobile). The clearest direct match for our flow.
- **Dropbox — "How to share files or folders in Dropbox"** (`references/competitors/dropbox/share-folder.md`, cached 2026-06-07, ~350–450 words). Router page that defines the edit/view-only/file-request mental model.
- **Virtru — "Persistent File Protection (PFP)"** (`references/competitors/virtru/share-folder.md`, cached 2026-06-07, ~700–900 words, 4–6 inline screenshots). Closest to SpecterX in spirit because the unit of protection is the file — but framed as an email-attachment add-in, not a web-app share dialog.
- **Egnyte — "Folder Permissions"** (`references/competitors/egnyte/share-folder.md`, cached 2026-06-07, ~1,500–1,800 words, 6–10 inline screenshots). The dense reference-style permissions matrix; reads as the canon for tiered-access docs.
- **DocSend — "Set granular space permissions"** (referenced in `references/competitors/docsend/share-folder.md`, ~1,200–1,500 words). The strongest competitor on per-link/per-recipient governance controls.

## Shape budget (derived from above)

- **Target length:** 700–1,100 words. Dropbox's main share article runs ~1,500 across three platforms; ours covers one (web) and adds a policy concept Dropbox doesn't have, so a single-platform article in the 700–1,100 band reads complete without padding.
- **Target screenshot count:** 3 (median of the competitor set, weighted toward Egnyte/Virtru since they screenshot more for security-product flows). Cover: (1) the empty Share Files dialog with the upload area, (2) the recipient + policy step with a recipient added, (3) the post-share confirmation with Copy Link.
- **Intro length:** 2–3 sentences. Dropbox's intro is 2 sentences; Virtru's is 4 but theirs is product-positioning. Stay in the 2–3 band; no marketing voice.

## Coverage checklist — what they thought worth covering

From Dropbox's main share-with-others page:
- [x] How to share files or folders with specific people (step-by-step) — **in scope**.
- [x] How to add multiple recipients — **in scope** (cover by saying you can repeat the recipient step).
- [x] Two-tier permission split — **in scope** (we have three tiers: Viewer / Contributor / Co-Owner).
- [ ] "How to share a link" (Copy link mode without recipients) — **out of scope for this article**: SpecterX doesn't have anonymous share-via-link without a named recipient list; the link is tied to the named recipients in the share dialog. We do cover "copy the link after sharing" as step 8.
- [ ] QR code share — **N/A**, SpecterX does not offer QR.
- [ ] Default link settings panel — **N/A** as separate concept; SpecterX uses a policy applied at share time.
- [x] What happens after sharing (recipient receives email) — **in scope**.

From Egnyte's Folder Permissions page:
- [ ] Permission inheritance from parent — **out of scope**: that's folder-share territory (article 05-share-a-folder).
- [x] Capability table per permission level — **in scope** but condensed inline, not as a wide matrix; one-line description per tier.
- [ ] Inviting brand-new external users from inside the dialog — **partially in scope**: SpecterX provisions external recipients automatically on the share; we mention this in the "What recipients experience" section.
- [ ] Group permissions / permission precedence — **out of scope**: groups belong in admin documentation.
- [ ] Notification email variants — **partial**: we mention "SpecterX sends a notification email" but don't catalogue variants.

From Virtru's PFP page:
- [x] Per-file policy controls (revoke, expire, watermark, prevent download) — **in scope** via "Select a security policy" step.
- [x] Recipient access via a verification step — **in scope** in the "What recipients experience" paragraph.
- [ ] Request Access workflow (unauthorized recipient asks for access) — **out of scope**: SpecterX's equivalent is "Add recipient" from the Share & Permissions Drawer, which is the focus of article 07-update-permissions.
- [x] Phone (SMS) verification at send time — **in scope** as step 6; flagged as conditional on policy.

From DocSend's granular permissions:
- [ ] Per-link allow/block lists — **out of scope**: SpecterX recipients are named, not list-filtered.
- [ ] Watermark / NDA / Visible / Downloadable per-item — **out of scope**: these are policy choices, set by an admin in the policy editor, not at share time. Cross-reference to "Apply a policy when sharing" (admin docs).
- [x] Multiple recipients per share — **in scope** (the Share Files dialog supports it).

## Related topics they reference inline

Competitors link inline (not just in "Related articles") to:

- Manage / change permissions after the share — Dropbox: "manage shared link settings"; Egnyte: "Non-Inherited Permissions". → **Inline link in the Share & Permissions Drawer section** to article 07-update-permissions when approved.
- Revoke access — Virtru: "revoke any time"; Dropbox: separate article. → **Inline link** to article 08-revoke-access when approved.
- Recipient experience — Virtru: "Secure Reader"; Dropbox: "recipient receives email". → **Inline link** to recipient articles in Section 3 when approved.

For articles 05–10 that aren't yet approved, we plant the cross-reference in the body but leave the link as an in-document anchor or `#` placeholder until they're merged.

## Coverage gaps in our plan entry

- **The Share & Permissions Drawer** — the plan lists it but I'm treating it as a post-share section ("After you share"), not a separate flow. Article 07-update-permissions will own the drawer in depth.
- **Recipient permission interaction with policy** — the plan lists "interactions with the active policy". The article notes that a Contributor cannot download if the policy blocks download; we don't enumerate every interaction (that belongs in article 06-set-recipient-permissions).
- **Copying the protected link after sharing** — explicitly in the plan; covered as step 8.

## Patterns NOT to copy

- **Dropbox's platform-tabbing** (web / desktop / mobile in one article). SpecterX is web-only for this flow, so one platform is enough; no tabbing.
- **Dropbox's screenshot-free style.** It works for them because the flow is well known to their consumer base; SpecterX is unfamiliar, so we include 3 screenshots.
- **Egnyte's dense capability matrix.** We condense the three SpecterX permission tiers to one-line bullets. The full matrix lives in article 06-set-recipient-permissions.
- **Virtru's product-marketing voice** ("PFP gives you a downloadable link…"). Stay procedural; describe what the button does, not how great the product is.
- **DocSend's reference-style permission lists** with every toggle defined inline. Defer toggle-level explanations to the policy admin article.
- **Marketing fluff in the intro.** Dropbox sometimes opens with "Not using Dropbox yet? See how Dropbox helps you easily share folders." That's an upsell; the SpecterX intro stays task-focused.
