# Competitor coverage checklist — Share a folder

## Articles read

- Egnyte — "Folder Permissions" (cached 2026-06-07, ~1,500-1,800 words, est. 6-10 screenshots)
  - Plus support pages: "Additional Details on Folder Sharing" (~400 words) and "Shared and Private Folders" (~350 words)
- Dropbox — "How to share files or folders in Dropbox" (cached 2026-06-07, ~350-450 words, no screenshots)
  - Plus support pages: "Dropbox Shared Folders FAQs" (~1,000-1,200 words) and "Can I share a subfolder inside a shared folder?" (~200 words)
- Virtru — "Security Option — Persistent File Protection (PFP)" (cached 2026-06-07, ~700-900 words, est. 4-6 screenshots) — closest proxy; Virtru has no folder primitive
- DocSend — "Create a Space (data room) in Dropbox DocSend" (cached 2026-06-07, ~350-450 words, est. 2-3 screenshots)
  - Plus companion: "Set granular space permissions in Dropbox DocSend" (~1,200-1,500 words)

Vendor not covered: Vera (Tricentis). Searches for "vera folder share", "Tricentis Vera secure share folder rights management" surfaced only product-marketing / FAQ PDFs and admin-deployment docs; the public Tricentis Vera KB has no end-user folder-share article. Documented and skipped per the procedure.

## Shape budget (derived from above)

- Target length: **700-1,100 words** for the primary "Share a folder" article. The two competitors who own this topic (Egnyte, DocSend granular permissions) overshoot at 1,200-1,800 words because they fold permission reference into the same page. Dropbox proves the short version works (350-450 words) when subtopics are deferred. SpecterX's article should sit between — long enough to teach the inheritance model, short enough to stay a how-to rather than a reference.
- Target screenshot count: **4-6**. Egnyte uses ~8 (dense, reference-style), Dropbox uses 0 (router page), DocSend uses ~3. A how-to with inheritance needs to show: the Share entry point, the recipient/permission picker, the policy dropdown (or equivalent), the Share & Permissions drawer for an already-shared folder, and one "what the recipient sees" shot. Optional 6th: the per-file override.
- Intro length: **2-3 sentences**. State the goal (share a folder with external recipients), state the differentiator (the folder's policy is inherited by every file inside, including new uploads), and orient the reader to the rest of the article. Dropbox and Egnyte both use a 1-paragraph intro of this shape; DocSend's intro is one sentence plus a plan-gating callout.

## What they thought worth covering

### From Egnyte's "Folder Permissions" (+ supporting articles)
- [ ] Where the action lives in the UI (a Permissions icon on the folder)
- [ ] Who is allowed to share — folder owners and admins only
- [ ] A capability matrix of access levels (Viewer / Editor / Full / Owner) showing what each can read, edit, upload, delete, re-share, set permissions
- [ ] Inheritance: subfolders auto-inherit from parent, including new ones
- [ ] Disabling inheritance on a specific subfolder
- [ ] Exclusion: removing a user from a specific subfolder while leaving them on the parent
- [ ] Precedence: direct user grant overrides group grant; higher access level wins across multiple group memberships
- [ ] Adding a brand-new external user from inside the permissions dialog (email + username, user-type default)
- [ ] Removing access and what cascades (revokes share links created by that user)
- [ ] Email notification to the affected user every time their access is granted, altered, or revoked
- [ ] Top-of-hierarchy model: there is a Shared root that all collaborative content sits under, with rules about what can/can't live at the root
- [ ] Mobile parity — sharing/permission management from iOS and Android

### From Dropbox's "Share files or folders" + FAQ + subfolder-sharing
- [ ] An upfront decision: do you want edit, view, or are you actually collecting files (very useful framing for the intro of our article)
- [ ] Editor vs. Viewer as the basic split with edit including add/edit/download/delete/share
- [ ] Two sharing modes: send by email from inside the product vs. create a link
- [ ] Auto-join vs. opt-in: teammates on the same Dropbox team auto-join shared folders; individual-account users have to accept
- [ ] Ownership rules: owner of parent shared folder automatically owns all subfolders, including ones others create
- [ ] Transferring ownership has to happen at the parent level
- [ ] Reasons a share might fail (limit reached, unverified email, admin disabled external sharing, etc.)
- [ ] Subfolder re-sharing limited by your own access level: viewer can only re-share as view-only link; editor only if owner granted re-share; owner can re-share freely
- [ ] Quotas (Dropbox-specific but the pattern is universal: limits exist on how many shared folders a user can create)

### From Virtru's PFP (proxy)
- [ ] What happens to unsupported file types when applying a folder policy (Virtru handles per-attachment with a "continue without protection" warning; our folder article needs a clear answer too)
- [ ] Revoking access after the share
- [ ] Setting expiration / watermark / prevent-download as policy attributes
- [ ] Request Access workflow: a recipient who isn't authorized can ask the owner
- [ ] "Re-shared attachments" — what happens when a recipient forwards a file out of the shared container
- [ ] Recipient experience as its own section (Virtru's is the Secure Reader; ours would be the SpecterX recipient view)

### From DocSend's Spaces + granular permissions
- [ ] Multiple links per Space — same folder content, different audiences, different settings (worth considering as a SpecterX power-user pattern even if it's not in v1)
- [ ] Per-content overrides on top of folder-level defaults (Visible, Downloadable, Watermark, NDA toggles per file inside the share)
- [ ] Override precedence is explicit: granular permissions BEAT default folder/link settings (this matches our "per-file policy overrides parent" plan item)
- [ ] Adding new files to an existing share without re-sending the link (DocSend says "add new files to the existing Space"; we need a clean answer for our parent-policy inheritance)
- [ ] Recipient-side gates as policy attributes: require email, require NDA, password, expiration, allow/block list
- [ ] Hide-from-team vs. hide-from-visitor distinction (DocSend treats these as different mechanisms; we should be clear which audience our visibility controls affect)
- [ ] Plan-gating callouts as a top-of-article device

## Related topics they reference inline

- Permission inheritance / non-inherited permissions (Egnyte)
- Permission change email notifications (Egnyte)
- Folder Permissions Report / who has access view (Egnyte, Dropbox)
- Transfer ownership of a shared folder (Dropbox)
- Move shared folder into another shared folder (Dropbox — has a special "can only do this on web/mobile, not desktop" wrinkle)
- File request / collect files (Dropbox — relevant for "Contributor upload to a shared folder" framing)
- Team folders vs. shared folders (Dropbox — two different primitives)
- Secure Reader / recipient view (Virtru)
- Request Access workflow (Virtru)
- Re-shared attachments (Virtru)
- Granular Space permissions / per-content overrides (DocSend)
- Allow/block list, NDA, watermark, expiration as link attributes (DocSend)
- Auto-created Space folders / team-vs-personal visibility (DocSend)

## Coverage gaps in our plan entry

Our plan entry covers seven bullets: file-vs-folder difference, the Share-a-folder flow, parent policy + inheritance, per-file override, recipient experience, folder-vs-file permission interaction, and adding a new file to an already-shared folder. Worth adding from competitor coverage:

- **Removing access / revocation** — every vendor we read covers this; our plan doesn't. The cluster's "Set recipient permissions" article may cover it, but our folder article should at least cross-link.
- **Who is allowed to share a folder** (Egnyte gates this to owner/admin; Dropbox has a list of failure reasons). SpecterX needs a one-liner: only the folder owner / co-owner can share.
- **What happens to recipient access when a parent folder's policy is changed mid-share** — both Egnyte and Virtru spend time on after-the-fact policy changes. Our plan touches "updating permissions" elsewhere but the folder article should mention that policy edits propagate.
- **"What the recipient sees when they browse the folder"** is in our plan but the level of detail isn't specified. Egnyte, DocSend, and Virtru all dedicate a clearly-named section to recipient experience. We should match.
- **Failure modes / why a folder share might not work** (Dropbox's "Why can't I create a shared folder?" pattern). Worth a short troubleshooting block: e.g., "if the policy you picked requires phone verification and the recipient hasn't a phone number on file, what happens?"
- **Adding NEW files to an already-shared folder** is in our plan, but the read showed two distinct cases worth separating: (a) the owner adds a file (most obvious — picks up parent policy); (b) a Contributor recipient uploads a file (does the upload pick up the parent policy too?). DocSend and Egnyte both handle these as separate flows.
- **Cross-link to "Set recipient permissions"** — Dropbox makes the editor-vs-viewer split the very first decision; our cluster has a separate article for permissions but the folder article needs to at minimum name the three tiers (Viewer, Contributor, Co-Owner) so the reader can choose.

## Patterns NOT to copy

- **Egnyte's capability matrix** (Viewer / Editor / Full / Owner × 12 actions). It's reference content, not how-to content, and it would crush a SpecterX article that's trying to teach folder inheritance. Defer the full matrix to the "Set recipient permissions" article and only mention tier names here.
- **Dropbox's nine-question FAQ format.** Their main share-folder page is a router; the FAQ is a separate page. We're writing a how-to, not a router, so structure as a linear walkthrough.
- **DocSend's plan-gating callouts** at the top of every section. SpecterX's pricing model isn't tier-flagged in the public KB; we don't have a Standard-vs-Advanced split to disclose.
- **Virtru's per-file model** carried over to a folder article. Virtru's KB exposes its lack of folder primitive everywhere; SpecterX should make the folder-as-container model load-bearing in the intro and not apologize for it.
- **Egnyte's dense top-of-page jump list** of 9 sub-sections. Useful in a 1,800-word reference; overkill at 700-1,100 words.
- **Marketing voice** ("PFP gives you a downloadable link…", Virtru). The article should stay imperative-procedural like Dropbox and Egnyte's body copy, not feature-pitch.
- **Multiple-links-per-Space** (DocSend). Tempting to mention but not in v1 scope per the plan entry; treat as out of scope.
