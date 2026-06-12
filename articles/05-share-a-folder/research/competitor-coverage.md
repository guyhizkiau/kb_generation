# Competitor coverage — Share a folder
# Gathered: 2026-06-11

## Cache strategy

Four vendors have cached entries matching the "share folder" topic in `references/competitors/INDEX.json`. All four are from different vendors (Egnyte, Dropbox, Virtru, DocSend), meeting the "2+ matches across different vendors" threshold. No live scraping was performed.

## Articles read

- Egnyte — "Folder Permissions" (cached 2026-06-07, ~1,800 words)
- Dropbox — "How to share files or folders in Dropbox" (cached 2026-06-07, ~450 words)
- Virtru — "Security Option — Persistent File Protection (PFP)" (cached 2026-06-07, ~800 words)
- DocSend — "Create a Space (data room) in Dropbox DocSend" (cached 2026-06-07, ~450 words)

---

## Coverage checklist

Things competitors thought worth covering — organized by concept:

### Access levels and roles
- [ ] A permission matrix or table showing what each level can do (Egnyte does this in detail)
- [ ] How the three (or more) roles differ: view-only vs. edit vs. full control (all vendors cover this in some form)
- [ ] Whether role applies to the folder only or all contents (Egnyte, Dropbox)

### Inheritance
- [ ] How sharing a parent folder gives access to all subfolders/files inside it (Egnyte, Dropbox)
- [ ] Whether new files added after the share automatically inherit access and policy (DocSend calls it "files added later automatically appear")
- [ ] Whether a subfolder can be locked down from a parent share (Egnyte — "Non-Inherited Permissions")
- [ ] Explicit statement: you cannot remove a user's inherited access at the child level; change must happen at parent (Egnyte)

### Sharing mechanics
- [ ] Multiple ways to add a folder share (Dropbox: invite by email OR create a link)
- [ ] Email notification when a recipient is granted, changed, or revoked (Egnyte)
- [ ] Explaining what the recipient sees (all vendors)

### Limits and edge cases
- [ ] Plan-gating callouts (Dropbox, DocSend both say certain features are Premium/Business only)
- [ ] Quota or scale limits (Dropbox: max 1,500 shared subfolders in a parent; max 30,000 shared folders per account)
- [ ] What you can and cannot do with nested shares (Dropbox: sub-sharing only if parent owner grants it)

### Policy / security
- [ ] How security settings travel with the folder contents (Virtru: per-file wrapping; DocSend: per-link settings)
- [ ] Revoke access after the fact (Virtru, DocSend)
- [ ] Expiry for the folder share (DocSend)

---

## Patterns NOT to copy

- **Egnyte's reference-doc density.** The Egnyte article reads more like a capability spec than a task guide. It lists nine sub-sections with jump links, mixing procedural steps with explanation. SpecterX articles should lead with the common path and keep edge cases in notes or separate sections.
- **Dropbox's router-page approach.** Dropbox puts the real content in five separate linked articles. That works for Dropbox's larger product but creates friction for a reader who just wants to share a folder. SpecterX should give the full procedure in one article with Related Articles for depth.
- **DocSend's plan-gate callout pattern.** DocSend leads every article with a plan tier disclaimer. SpecterX does not have a tiered plan structure exposed to end users.
- **Virtru's feature-spec tone.** The Virtru page reads like a product announcement ("PFP gives you a downloadable link…"). SpecterX articles should be task-oriented.

---

## Coverage gaps vs. the article plan

Concepts competitors covered that the SpecterX plan did not explicitly include:

1. **Email notification to recipients when access is granted or changed.** Egnyte explicitly documents the notification email that goes out when folder permissions change. The SpecterX plan doesn't mention whether a folder-share recipient gets a notification the same way a file-share recipient does. **Proposed addition:** Confirm whether SpecterX sends a notification email for folder shares (the `04-share-a-file` article documents a `Notify recipients` checkbox — verify this exists for folder shares too).

2. **What happens when a new user is added to a folder they are already inside via a sub-path.** Egnyte has a detailed note about permission precedence — direct user grant wins over group membership. This may not be relevant to SpecterX's simpler model but worth a brief note if user-level and group-level share overlap can occur.

3. **Ownership transfer.** Dropbox has a dedicated note about how ownership transfers to parent-folder owner even for subfolders created by others. SpecterX may not have this construct but it's worth checking.

4. **What the recipient sees when they click the folder link.** All vendors address this. The SpecterX plan includes it ("Recipient experience: what a recipient sees when they receive a shared folder link") but it needs confirmation of whether the recipient lands on a folder viewer or on individual file links.

---

## Key differentiators to highlight in the SpecterX article

- **Policy inheritance is security-centric, not just access-centric.** Unlike Dropbox (which only grants access) or DocSend (which manages link-level permissions), SpecterX applies a full security policy (verification, download controls, watermarking, RMS) to the folder. New files added inherit that policy automatically.
- **Recipient provisioning is automatic.** SpecterX doesn't require recipients to have an account before being added to a folder share (consistent with the file-share model).
- **The "Parent policy" concept.** This is SpecterX-specific terminology — neither Egnyte, Dropbox, nor Virtru use this phrasing. It's the right term and should be used consistently.
