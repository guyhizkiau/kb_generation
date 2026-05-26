# Vera (Tricentis) — Documentation Analysis (Phase 1 draft)

Sources crawled: **12 pages** (see [`index.json`](index.json)). Selection covers the home, what's-new release notes, the user guide for the Web Portal (the part end-users actually use — approve/reject records, approval queue, email notifications), one integration page (Tricentis Tosca), and the top of the admin guide. Installation/upgrade pages were deliberately skipped per the plan.

Vera is a validation/approvals platform for regulated industries (life sciences, GxP). It's the **least functionally similar** to SpecterX in the set — but it's a useful **contrast point**: enterprise B2B docs with very different style choices.

> **Phase 1 caveat.** Vera's documentation is comparatively small. 12 pages is a meaningful proportion of its top-level topics. Conclusions about the *kind* of voice/structure Vera uses are well-supported by this sample. Conclusions about screenshot density should be revisited with a deeper crawl into the actual feature pages (Phase 2).

---

## 1. Hierarchy

Tricentis runs Vera docs on a custom MadCap-Flare-style portal at `docs.tricentis.com/vera-latest/content/<section>/<page>.htm`. The IA is explicit in URL paths:

```
Vera Documentation
├── home.htm                                         (card-grid landing)
├── release_notes/key_features.htm                   ("What's new")
├── user_guide/                                      (end-user docs)
│   ├── user_guide.htm                                  ← section index
│   ├── web_portal/                                     ← the actual UI
│   │   ├── web_portal.htm
│   │   ├── log_in_web_portal.htm
│   │   ├── approval_queue.htm
│   │   ├── approve_records.htm
│   │   ├── reject_records.htm
│   │   ├── view_record_detail.htm
│   │   ├── record_search.htm
│   │   ├── email_notifications.htm
│   │   ├── email_notification_settings.htm
│   │   ├── change_your_password.htm
│   │   └── view_edit_profile.htm
│   ├── tricentis_tosca/                                ← integration with Tosca
│   └── tricentis_qtest/                                ← integration with qTest
├── admin_guide/                                     (admin docs)
│   ├── administrative_docu.htm                         ← admin guide index
│   ├── administration/                                 ← user/role admin
│   ├── installation/
│   ├── integrations/
│   └── system_administration/
├── configuration_guide/                             (config recipes)
├── constraints/                                     (known limits)
├── system_requirements/
└── upgrade/
```

Notable IA decisions:

- **Three-level deep folder structure** (`user_guide / web_portal / approve_records`). Vera commits to a hierarchy and surfaces it in URLs.
- **Section index pages exist at every level** (`user_guide.htm`, `web_portal.htm`, `administrative_docu.htm`). They are navigation hubs, not content pages — typically 200–500 words and a list of links.
- **Audience split by guide.** "User guide" vs "Admin guide" vs "Configuration guide" — strong audience-based separation, like Egnyte's Outlook split but applied to the entire product.
- **Constraints get a dedicated top-level section.** That's an enterprise-doc tell: regulated customers want a single canonical list of what the product cannot do, separate from the happy-path docs.

**Takeaway for SpecterX:** Vera's strict folder hierarchy is overkill for a smaller product, but the **separate audience guides** (User / Admin / Configuration) and the **dedicated "Constraints" page** are both worth adopting. Especially the latter — every regulated SpecterX customer asks "what are the known limits" early in the buying conversation.

## 2. Page anatomy

Two clear page types in the sample:

### A. Section index pages (orientation hubs)

Very short — 200–500 words. Pattern:

```
H1  <Section name>
    Intro paragraph: "This comprehensive guide provides …"
    Bulleted list of links to sub-topics OR
    A card-grid (home page only).
    Copyright footer.
```

Example: [`administrative_docu.htm`](pages/docs.tricentis.com_vera-latest_content_admin_guide_administrative_docu.htm.html) — 204 words, no H2s, just lists what the admin guide contains.

### B. Task / feature pages (the real content)

Pattern:

```
H1  <Task name>                              ← "Approval queue", "Email notifications", "Approve records"
    1–2 sentence orientation paragraph:
    "When you sign into the Tricentis Vera Web Portal, all the pending tasks are displayed in the Approval queue page."
H2  <Sub-feature or scenario #1>             ← "Approve or reject a single record"
    (Numbered steps)
    (Optional inline screenshot — often only 1 per page)
H2  <Sub-feature or scenario #2>             ← "Approve records in bulk"
    (More steps)
[Optional: small "New in version X.Y" callout sprinkled in])
```

Length range: **250–1,000 words** for the saved task pages — *much shorter than DocSend (800–1,500) or Egnyte (575–3,020).*

Evidence:
- [`approval_queue.htm`](pages/docs.tricentis.com_vera-latest_content_user_guide_web_portal_approval_queue.htm.html): 620 words, 2 H2s, 3 images
- [`approve_records.htm`](pages/docs.tricentis.com_vera-latest_content_user_guide_web_portal_approve_records.htm.html): 833 words, 2 H2s, 1 image
- [`email_notifications.htm`](pages/docs.tricentis.com_vera-latest_content_user_guide_web_portal_email_notifications.htm.html): 1,024 words, 4 H2s, 1 image

**Takeaway for SpecterX:** the **two-page-type pattern** (index hubs vs task pages) is good IA hygiene. Index pages are short, link-only orientation; task pages do the work. Don't blur them.

## 3. Page scope — what gets its own page

Vera splits **very aggressively at the task level**:

- "Log in to the web portal" → its own page
- "Approval queue" → its own page
- "Approve records" → its own page
- "Reject records" → its own page (sibling to "Approve records", not a section within it!)
- "View record detail" → its own page
- "Record search" → its own page
- "Change your password" → its own page
- "Email notifications" → its own page
- "Email notification settings" → its own page (sibling to "Email notifications", not nested)

This is **finer-grained than DocSend**. SpecterX would probably bundle "Approve" + "Reject" into one page (they're variations of the same modal). Vera doesn't.

**The Vera rule (inferred):** one user-facing verb → one page. If the UI exposes the action under its own menu entry or button, the docs give it a dedicated page.

**Pros:** every page is laser-focused; search results are precise; titles match exactly what the user clicked.
**Cons:** the reader has to hop more between pages to learn related actions; "Reject records" duplicates context from "Approve records".

**Takeaway for SpecterX:** Vera's split is too granular for our product. **DocSend's "one feature, one outcome, one page"** is a better rule for us. But Vera's discipline — one menu entry, one page, matching titles — is worth borrowing for navigation clarity.

## 4. Cross-references between pages

Vera's cross-references are **structural, not narrative**:

- **The section index page is the table of contents.** Each task page is reached *from* its index, and pages don't link laterally to siblings in their own bodies (in the sample).
- **Inline links are used for "see related concept" references.** The [release notes](pages/docs.tricentis.com_vera-latest_content_release_notes_key_features.htm.html) link out to a "technical release notes" page for resolved issues.
- **No "Related articles" footer.** No "Other ways to get help". No callout boxes wrapping cross-refs.
- **"New in Vera X.Y" inline annotations** flag version-specific behaviors mid-content — a kind of *temporal cross-reference* to the release notes.

**Takeaway for SpecterX:** Vera's restraint is enterprise-doc orthodoxy — readers find content via the IA, not via cross-page suggestion. But it makes lateral discovery hard. Pick a hybrid: **explicit IA (Vera) + selective inline + a small "Related" footer (DocSend/Egnyte).**

## 5. Screenshots

**Vera uses very few screenshots.** Across the 12-page sample, image counts:

| Page | Images |
|---|---|
| Home (card-grid landing) | 13 |
| Approval queue | 3 |
| Tricentis Tosca | 2 |
| Every other page | 0–1 |

The Approval queue page has the most "real" screenshots (3, showing the queue grid in different states). Every other task page has at most one orientation screenshot of the panel being discussed; the steps are described in prose alone.

This is in stark contrast to DocSend (~7 content images per page) and Egnyte (up to 88 on a long feature page).

Likely reasons:
- Vera's audience is enterprise/regulated; readers tolerate text-heavy docs.
- Approval workflows are conceptually simple (a button to click); screenshots add less value.
- Maintenance cost: regulated-industry products release on cycles where screenshots quickly stale; less screenshot = less rework.

**Takeaway for SpecterX:** for our security/compliance audience, fewer screenshots is acceptable on conceptual/admin pages. But for **end-user share workflows** — the equivalent of DocSend's "create a watermarked link" — Vera's minimal style would feel sparse. **Pick screenshot density by page type**, not by site-wide style.

## 6. Page-worthy vs. assumed knowledge

**Documented:**
- Every UI screen / menu entry (one page each)
- Versioned behavior changes ("New in Vera 2023.2 the Location column was replaced with the System column")
- Notification semantics ("A domain user will receive an email notification when an approval task is assigned to one of their approval roles")
- Constraints (limits, known issues) — separate top-level section

**Deliberately not documented (assumed):**
- General concepts like "approval workflow", "domain user", "SMTP server" — Vera assumes the reader knows enterprise terminology
- How to log in to a web portal in general
- What a CSV / Excel file is
- Anything about the underlying technology (Java, IIS, etc.) outside the install guide

Vera also **omits "Visitor experience"-style sections** because Vera doesn't have external visitors — every actor is an authenticated internal user. **For SpecterX, the reverse is true:** the *recipient/external-viewer* perspective is central to every share workflow, so we must document it.

**Takeaway for SpecterX:** Vera's assumption that the reader is enterprise-literate is appropriate for its audience. SpecterX has both enterprise admins *and* less-technical end-users sending links — so we need both registers. Have "for admins" sections at the same enterprise register as Vera; have "for end users" sections at the friendlier DocSend register.

## 7. Voice & language

Confirmed across the sample:

- **Strong second person for the end-user reader.** "When **you** sign into the Tricentis Vera Web Portal, all the pending tasks are displayed in the Approval queue page." (from [`approval_queue.htm`](pages/docs.tricentis.com_vera-latest_content_user_guide_web_portal_approval_queue.htm.html))
- **Third person creeps in for system behavior.** "A domain user will receive an email notification when an approval task is assigned to one of their approval roles." — when describing how the system treats actors collectively. Less mixed than Egnyte, more than DocSend.
- **Present and future tense.** "Emails **will** automatically be sent when SMTP server management is configured" — uses future to describe downstream system behavior, present for current UI state.
- **Formal register.** "Tricentis Vera" full product name is used frequently (more than DocSend says "DocSend"). Few contractions. Few conversational connectives.
- **Brief, factual sentences.** Most are 10–18 words. No conversational asides.
- **Inline product-version annotations** appear in body text ("New in Vera 2023.2 …") — a feature unique to Vera in our set, valuable for regulated customers.
- **Title Case for UI labels** (Approval Queue, System, Author, Location) — consistent with the other platforms.
- **Minimal callout use.** No standard "Important:" / "Note:" boxes observed in this sample. Caveats are inline parenthetical clauses instead.
- **Headings use sentence case** ("Approve or reject a single record"), not title case. Different from DocSend ("Add a watermark to a link" — sentence case too, actually) and Egnyte (Title Case headings).

**Takeaway for SpecterX:** Vera's tight, formal register reads professional and trustworthy for an enterprise audience. But it lacks DocSend's warmth on end-user workflows. **Use Vera-register for admin/config/security pages; use DocSend-register for end-user workflows.**

---

## Summary of the strongest Vera patterns to copy

1. **Hard split: User Guide vs Admin Guide vs Configuration Guide.** Same product, different docs by audience.
2. **A dedicated "Constraints" / "Known Limitations" top-level section.** Enterprise customers find this fast.
3. **Section index pages as pure orientation** (short, link-only) — distinct page type from task pages.
4. **Inline "New in version X.Y" annotations.** Tell the reader when behavior changed; they don't have to dig into release notes.
5. **Sentence-case headings.** Easier to read than Title Case in dense text.
6. **Formal/concise register for admin docs.**

## Patterns NOT to copy from Vera

1. **Splitting "approve" and "reject" into separate pages.** Too granular; user has to context-hop. Bundle related sibling actions.
2. **No cross-page suggestions at all.** Readers benefit from at least a small "Related articles" footer or inline hint.
3. **Near-zero screenshots on end-user workflow pages.** Acceptable for admin docs, not for share workflows.
4. **A 3-level deep folder URL hierarchy.** Adds maintenance burden and forces over-classification. 2 levels is plenty.
