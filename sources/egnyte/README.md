# Egnyte — Documentation Analysis (Phase 1 draft)

Sources crawled: **15 pages** (see [`index.json`](index.json)). Selection focused on Egnyte's secure content sharing — link sharing, link security, folder permissions, governance/classification, admin & roles, the Outlook add-in (a direct analog to SpecterX's Outlook connector), and the desktop app. Includes the page the user explicitly cited: the Knowledge Bases User Guide.

Egnyte's product domain is the closest functional match to SpecterX — secure content collaboration, link-based external sharing, classification/DLP, governance. Treat conclusions here as high-relevance.

> **Phase 1 caveat.** Conclusions are drawn from 15 hand-picked pages out of 1,350+ Egnyte articles in their sitemap. Patterns that hold across all 15 samples (page skeleton, promo banner, voice mixing) are likely platform-wide; specific quantitative claims (e.g. screenshot count) are noted as "in this sample" where they vary.

---

## 1. Hierarchy

Egnyte runs on Zendesk. URLs follow `/hc/en-us/articles/<numeric-id>-<descriptive-slug>`. The IA is two-level: **Category → Section → Article**. From the help-center home, observable top-level categories (no descriptive URL slugs — only numeric IDs):

```
Egnyte Help Desk
├── Browse Categories
│   ├── AI
│   ├── Desktop App
│   ├── Mobile
│   ├── Web UI                     ← sharing/permissions live here
│   ├── Document Portal
│   ├── Document Room              ← data-room / secure repo
│   ├── API
│   ├── Migration App
│   ├── Secure and Govern          ← classification, DLP, governance
│   ├── External Replication
│   ├── Reporting
│   ├── AEC                        ← architecture/engineering vertical
│   ├── Life Sciences              ← life-sciences vertical
│   ├── Billing
│   └── CMMC                       ← compliance framework
├── User Types
│   ├── Admin Users
│   └── Non-Admin Users
├── Integrations
│   ├── MS Teams
│   ├── Google Apps
│   ├── Microsoft Office
│   └── Salesforce
└── Certified Apps
    ├── AutoCAD / Civil 3D / NavisWorks
```

Notable IA decisions:

- **Categories cut by product surface, not by user job.** "Web UI", "Desktop App", "Mobile" are interface buckets, not workflow buckets like DocSend's "Securing your data" or "Managing spaces".
- **Vertical categories alongside horizontal ones.** "AEC" and "Life Sciences" sit next to "Reporting" — a tacit signal that Egnyte's customers in regulated industries want vertical-specific landing pages.
- **"User Types" duplicates the IA.** The same article may be reachable via the product-surface category *and* via Admin Users or Non-Admin Users. This is duplication-as-discovery — common in Zendesk help centers.
- **No global breadcrumb on article pages.** Pages do not show the IA path. Discovery happens through category landings and the on-page Search.

**Takeaway for SpecterX:** if you want users to find docs by either *surface* (web UI / Outlook / mobile) *or* *role* (admin / end-user), Egnyte's "User Types" duplication is a pragmatic pattern. Don't try to force a one-true taxonomy. But unlike Egnyte, **keep breadcrumbs visible** — they're a navigation aid Egnyte sacrifices.

## 2. Page anatomy

Most pages in the sample follow this skeleton:

```
[Community promo banner]                 ← cross-page boilerplate
H1  <Page title>
    Intro paragraph: "<Feature> in Egnyte allow/provides …"
    (Optional: link to a more advanced/related article inline.)
H2  Prerequisites                         ← when install/config required
H2  Supported configurations / OS         ← when relevant
H2  <Task or sub-feature #1>
    (steps, screenshots inline)
H2  <Task or sub-feature #2>
H2  <Limits / FAQs section>
H2  Additional Resources                  ← list of related article links
```

Evidence:
- [`Folder Permissions`](pages/helpdesk.egnyte.com_hc_en-us_articles_201637444-folder-permissions.html): H2s = Add A Domain User / Add a User to Existing Group / Invite New User(s) / Remove a User or Group / Folder Notification / Folder Access Levels / Subfolder Access / Sharing from a Mobile Device — 8 H2s, 1,907 words, 19 images
- [`How Do I Make File and Folder Links More Secure?`](pages/helpdesk.egnyte.com_hc_en-us_articles_201637554-how-do-i-make-file-and-folder-links-more-secure.html): H2s = Public Links / Private Links / Specific Recipients / Additional Security Options / For Admins — 5 H2s, 594 words, 11 images
- [`Egnyte for Outlook Add-In - Configuration Guide`](pages/helpdesk.egnyte.com_hc_en-us_articles_4427094546317-egnyte-for-outlook-add-in-configuration-guide.html): H2s = Prerequisites / Supported Outlook Client Configurations / Supported Office Licenses / Configuring Outlook Add-in as an Admin / Deploy Egnyte for Outlook as an Admin / Known Limitations / Useful Links — 7 H2s, 1,229 words
- [`Desktop App Overview`](pages/helpdesk.egnyte.com_hc_en-us_articles_202206920-desktop-app-overview.html): H2s = Features / Availability / Supported Operating Systems / Additional Resources — overview pages stay short and structured

**Length range: 575–3,020 words** — much wider than DocSend's tight 800–1,500 range. Egnyte's user-cited [`Knowledge Bases User Guide`](pages/helpdesk.egnyte.com_hc_en-us_articles_27922151052429-knowledge-bases-user-guide.html) is at the long end (3,020 words, 15 H2s, 88 images) and reads as a feature manual rather than a task guide.

**Takeaway for SpecterX:** distinguish between short *overview* pages (Features / Availability / Supported OS / Additional Resources) and longer *task* pages (one feature, multiple sub-tasks, lots of screenshots). Don't let any page exceed ~2,000 words; split into siblings if you do.

## 3. Page scope — what gets its own page

Egnyte's split is **less aggressive than DocSend's**. Examples from the sample:

- **One page covers multiple sharing operations** ([`Share with File and Folder Links in the WebUI`](pages/helpdesk.egnyte.com_hc_en-us_articles_201637104-share-with-file-and-folder-links-in-the-webui.html)) handles both file links *and* folder links, including direct links. DocSend would likely split these.
- **Security options bundled into one page** ([`How Do I Make File and Folder Links More Secure?`](pages/helpdesk.egnyte.com_hc_en-us_articles_201637554-how-do-i-make-file-and-folder-links-more-secure.html)) covers Public / Private / Specific Recipients / Additional Security / Admin settings in 594 words — a true overview that says "here are your options" rather than going deep on any one.
- **Upload Links and Preview-Only Links get separate pages** because they're conceptually different link *types*, not just settings.
- **The Outlook add-in is split into two pages**: a [User Guide](pages/helpdesk.egnyte.com_hc_en-us_articles_4427124922125-egnyte-for-outlook-add-in-user-guide.html) (1,663 words, what end-users do) and a [Configuration Guide](pages/helpdesk.egnyte.com_hc_en-us_articles_4427094546317-egnyte-for-outlook-add-in-configuration-guide.html) (1,229 words, what admins do). **Audience-based split**.

**The Egnyte rule (inferred):**
- Split when the *audience* changes (admin vs end-user, sender vs receiver).
- Split when the *concept* changes (a different link type, a different feature).
- Keep together when it's the *same workflow* with multiple options (link security options on one page).

**Takeaway for SpecterX:** audience-based splits are a strong organizing principle. Have separate "Admin guide" and "User guide" pages for any feature that exposes both surfaces (most security features do). Don't split on every setting if they belong to the same panel and same workflow.

## 4. Cross-references between pages

Patterns observed:

1. **Inline links in the intro paragraph** pointing at the canonical "next thing to read" — e.g. `Folder Permissions` intro links to "Permissions FAQs". This is a strong "if you want more depth, here it is" gesture.
2. **"Additional Resources" footer block** rather than DocSend's "Related Articles" cards. Plain bulleted links, no thumbnails. Often 3–6 entries, hand-curated to the article topic.
3. **In-body links to dependency articles.** When the Outlook config guide mentions licensing requirements, it doesn't re-explain them — it links to the Microsoft licensing article.
4. **No callouts for cross-refs.** Unlike DocSend, Egnyte does not wrap "see also" links in Important/Note boxes. Plain inline links carry the cross-reference.

Egnyte does not use sequential next/previous navigation. Each article is self-contained.

**Takeaway for SpecterX:** combine DocSend's "inline links carry the dependency" with Egnyte's "Additional Resources" footer. Don't duplicate — if a topic is linked inline in the body, it doesn't need to appear again in the footer.

## 5. Screenshots

Egnyte's screenshot density is **much higher and more variable** than DocSend's:

- [`Knowledge Bases User Guide`](pages/helpdesk.egnyte.com_hc_en-us_articles_27922151052429-knowledge-bases-user-guide.html): **88 local images** — essentially screenshots per step throughout a 3,020-word feature manual.
- [`Folder Permissions`](pages/helpdesk.egnyte.com_hc_en-us_articles_201637444-folder-permissions.html): 19 images for 8 H2 sections — ~2.5 per H2.
- [`Outlook Add-In User Guide`](pages/helpdesk.egnyte.com_hc_en-us_articles_4427124922125-egnyte-for-outlook-add-in-user-guide.html): 20 images for 9 sections — similar density.
- Short overview pages: 3–4 images total.

Observed rules:

- **Inline placement.** Like DocSend — screenshots sit directly above or below the step they illustrate.
- **Full-context crops more common.** Egnyte often shows enough surrounding chrome (left nav, breadcrumbs) so the user can locate the panel in the broader app. Tradeoff vs DocSend's tight crops: easier orientation, more visual noise.
- **No annotations in the sample.** Screenshots are clean — no arrows, circles, or numbered overlays. Where pointing is needed, the prose handles it ("Click the **Permissions** tab on the right").
- **Numbered step + screenshot pattern.** Ordered lists (`<ol>`) where each step ends with a screenshot. This is Egnyte's most consistent visual pattern.
- **Mobile vs desktop screenshots are mixed in the same article** ([`Folder Permissions`](pages/helpdesk.egnyte.com_hc_en-us_articles_201637444-folder-permissions.html) covers "Sharing from a Mobile Device" with mobile screenshots in the same flow as desktop ones).

**Takeaway for SpecterX:** Egnyte's screenshot-per-step density is appropriate for *feature manuals* (long, comprehensive). DocSend's lower density is appropriate for *task pages*. For SpecterX, pick the density that matches the page type — don't try to be uniform across all pages.

## 6. Page-worthy vs. assumed knowledge

**Documented:**
- Permissions matrix (who can do what) — gets its own page and a FAQs page
- Audience-specific install/config flows (Outlook admin vs user)
- Vertical-specific landing pages (AEC, Life Sciences) — Egnyte documents the vertical context, not just the feature
- "Known Limitations" sections (Outlook config guide has its own H2)
- Supported configurations / OS — explicitly enumerated on overview pages

**Deliberately not documented (assumed):**
- General Outlook usage
- What an Active Directory / domain is (assumed in admin-targeted pages)
- General Windows/Mac file system concepts
- What "CSV" means

Egnyte is **more enterprise-formal** about prerequisites — explicit OS support tables, license requirements, deployment-mode call-outs. This reflects a B2B/IT audience that needs to know "will this work in our environment" before installing.

**Takeaway for SpecterX:** for any connector or installable component (Outlook add-in, Gmail extension, desktop app), include explicit "Prerequisites" and "Known Limitations" H2 sections. SpecterX customers are also enterprise — they read these before installing.

## 7. Voice & language

Egnyte's voice is **more formal than DocSend's** and **mixes second and third person** in ways DocSend does not.

Confirmed across samples:

- **Mixed person.** Both 2nd ("you", "your") and 3rd ("the user", "users can", "admins and folder owners") appear in the same article. Example, from [`How Do I Make Links More Secure?`](pages/helpdesk.egnyte.com_hc_en-us_articles_201637554-how-do-i-make-file-and-folder-links-more-secure.html): "Egnyte makes it easy to keep links secure. **Users can** make the link public…" then later "If **you** want…" The shift signals "general capability" (3rd person) vs "what you specifically do next" (2nd person).
- **More passive constructions** than DocSend. "This is automatically generated…", "These settings are available after…"
- **Less contraction usage.** "Cannot" instead of "can't" is more common.
- **Feature names in Title Case.** "Public Link", "Anyone with a password", "Existing users" — same as DocSend.
- **UI button names in italics or quotes, not always bold.** Inconsistent — sometimes bold, sometimes italic, sometimes plain.
- **Conditional opening phrases.** "When creating a new link…", "For sharing a Public File Link…" — sets a scenario before the instruction. More indirect than DocSend's "Click **Create link**".
- **"Note" callouts** (no colon, sometimes) appear inline. Less consistent formatting than DocSend.
- **The "Community promo" banner appears at the top of every article**, which is a cross-page boilerplate they accept as visual cost in exchange for community engagement.

**Takeaway for SpecterX:** decide upfront whether to use strict 2nd person (DocSend) or mixed person (Egnyte). I recommend **strict 2nd person** — it's clearer and Egnyte's mixed style sometimes reads as inconsistent. Standardize callout formatting (always bold label + colon).

---

## Summary of the strongest Egnyte patterns to copy

1. **Audience-based splits.** Separate "User Guide" and "Configuration Guide" / "Admin Guide" pages for the same feature.
2. **Explicit Prerequisites and Supported Configurations sections** for any installable component (Outlook add-in, desktop app, Gmail extension).
3. **A "Known Limitations" section** when the feature has notable gaps — this is what enterprise IT readers look for first.
4. **Audience duplication in IA.** Reach the same article from both "Web UI" / "Outlook" (surface) and "Admin Users" / "Non-Admin Users" (role).
5. **Numbered list + inline screenshot per step.** Don't break this pattern.
6. **"Additional Resources" footer** as a hand-curated list of next-reads, not auto-generated siblings.

## Patterns NOT to copy from Egnyte

1. **Mixed 2nd/3rd person.** Pick one.
2. **Hiding the IA from article pages.** Always show breadcrumbs.
3. **Inconsistent UI-element formatting** (bold/italic/quoted).
4. **A promo banner at the top of every page.** It hurts scan-ability.
