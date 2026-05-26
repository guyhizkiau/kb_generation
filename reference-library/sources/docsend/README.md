# Dropbox DocSend — Documentation Analysis (Phase 1 draft)

Sources crawled: **15 pages** (see [`index.json`](index.json)). Selection focused on the DocSend area of `help.dropbox.com` — the category index, link security (watermarks, allow/block, passcode, expiration, email auth/validation, disable), Agreements (NDA equivalent), viewer analytics, Spaces, link management, and an account/permissions exemplar.

DocSend is the closest analog to SpecterX in this set, so the conclusions here weigh heavily in the synthesis.

> **Phase 1 caveat.** Conclusions are drawn from 15 hand-picked pages, not the full 100+ DocSend articles. Specific shape of the boilerplate ("In this article", footer, "Related Articles") and the consistent per-page screenshot count of ~7 are confirmed across all 15 pages and look like enforced templates, not coincidences.

---

## 1. Hierarchy

DocSend lives under `help.dropbox.com/docsend`, a **product-scoped landing page** that fronts a single, flat list of articles grouped by H2 category headings on the index. Categories observed on [`help.dropbox.com_docsend.html`](pages/help.dropbox.com_docsend.html):

```
Dropbox DocSend (product)
├── Dropbox DocSend plans
├── Creating documents in Dropbox DocSend
├── Managing payments
├── Dropbox DocSend links and documents   ← bulk of security/sharing content
├── Commenting on files
├── Managing spaces
├── Managing account settings
├── Requesting support
├── Managing team access                  ← SSO, sub-teams
├── Uploading to Dropbox DocSend
├── Previewing and viewing files
├── Dropbox DocSend integrations
├── Organizing files and folders
├── Setting sharing permissions
├── Securing your data
├── Managing passwords
└── … (~20 categories total)
```

- **Depth: 2 levels.** Every article is `Dropbox DocSend → <category> → <article>`. No sub-categories or nested folders.
- **Breadcrumbs are minimal.** Pages show `Help center → Share → <Article title>` — the breadcrumb groups DocSend under the broader Dropbox "Share" topic rather than under "DocSend" specifically. The product-scoped landing page is the de-facto IA root for DocSend.
- **Category names are short verb phrases or feature nouns** ("Managing spaces", "Securing your data") — never the literal product feature name. The article title carries the feature name.

**Takeaway for SpecterX:** for a product like ours, a single flat-ish category list under a clear product-scoped landing page is enough. Don't nest. Use category names that describe the *user's job*, not the feature name.

## 2. Page anatomy

Every saved DocSend page follows the same skeleton (with small variations):

```
H1  <Page title — same as <title> minus " - Dropbox Help">
    "This article describes a feature available on <plan>."   ← plan-gate banner
    1-paragraph intro: what the feature does + why you'd use it
H2  In this article            ← auto-generated TOC linking to remaining H2s
    [optional Important callout]
H2  <Primary task #1>          ← e.g. "Add a watermark to a link"
    H3 Sub-task (optional)
H2  <Primary task #2>          ← e.g. "Customize and preview watermarks"
H2  <State / experience notes> ← e.g. "Visitor experience"
H2  <Admin / defaults notes>   ← e.g. "Default watermark options"
H2  Other ways to get help     ← boilerplate footer
H2  Choose a language          ← boilerplate footer
H3  Related Articles            ← 4 sibling article links
```

Evidence:
- [`watermarks.html`](pages/help.dropbox.com_share_dropbox-docsend-watermarks.html): H2 = In this article / Add a watermark / Customize and preview / Visitor experience / Default watermark options / Other ways to get help / Choose a language
- [`restrict-access-allow-or-block-viewers.html`](pages/help.dropbox.com_share_dropbox-docsend-restrict-access-allow-or-block-viewers.html): same skeleton, with one extra H2 "Things to consider"
- [`agreements.html`](pages/help.dropbox.com_share_dropbox-docsend-agreements.html): same skeleton, larger article — 14 H2s

**Length range:** 800–1,600 words for security/workflow articles; up to 1,500 for the long Agreements page. Pages stay under "one focused feature" — there is no page that explains multiple unrelated capabilities.

**Takeaway for SpecterX:** standardize a page skeleton: H1 title → plan-gate banner (if relevant) → 1-paragraph intro → "In this article" TOC → 2–6 task H2s → optional "Visitor experience" / "Defaults" → "Related articles". Keep articles 800–1,500 words. Anything longer is a sign you should split.

## 3. Page scope — what gets its own page

DocSend's strongest editorial decision: **each link-security mechanism gets its own page**, even when several share the same UI surface (the link settings modal). Observed split:

| Capability | Page |
|---|---|
| Watermarks | dropbox-docsend-watermarks |
| Restrict access (allow/block) | dropbox-docsend-restrict-access-allow-or-block-viewers |
| Email authentication for viewers | dropbox-docsend-email-authentication |
| Email *validation* (lighter check) | dropbox-docsend-viewer-email-validation |
| Password protection | dropbox-docsend-password-protected-document-support |
| Disable a link | dropbox-docsend-disable-access-to-link |
| Update link settings (general) | dropbox-docsend-update-link-settings |

Email *authentication* and email *validation* are deliberately separated despite being closely related, because they describe distinct security models and viewer experiences. The author chose clarity over consolidation.

**Heuristic that explains the split:**
- One page = one *thing the user enables and one outcome they get*. If two settings produce different end-states (e.g. "viewer must authenticate" vs "viewer must just confirm email"), they get separate pages.
- The integrating page ("Update link settings") explains the UI surface and links *out* to each focused page — never tries to explain them all inline.

**Takeaway for SpecterX:** when a single settings panel exposes multiple security controls, write one short overview page that maps the panel, and one focused page per control. The focused pages are searchable and shareable; the overview page is the orientation.

## 4. Cross-references between pages

Three patterns, in increasing strength:

1. **Inline link, no special styling.** Used for incidental references. Example: in [`watermarks.html`](pages/help.dropbox.com_share_dropbox-docsend-watermarks.html), "If you're an account owner or admin, you can set a default watermark configuration from the **Permissions page**." The "Permissions page" is a regular underlined link to the permissions article. There's no "see also" decoration around it.
2. **In-flow callout box.** Yellow-tinted callouts begin with bold "Important:" or "Note:" and are used when missing the linked context would cause errors or surprises. Example: the **Important** callout on the watermarks page warning that some file types can't be watermarked, with inline links to the download-only files and URL uploads articles.
3. **"Related Articles" footer.** Every page ends with exactly **4 related-article tiles** (heading + 1-sentence snippet). The selection appears to be category-mate articles — siblings in the same H2 group on the product index, not the page that linked *to* this one. So related articles function as *lateral discovery*, not as a guided next-step.

DocSend does **not** use sequential next/previous links between pages. There is no implied reading order. Every page is written to stand alone.

**Takeaway for SpecterX:** prefer inline links to "see also" lists. Reserve "Related articles" for lateral discovery (siblings), not for next-step navigation. If a user must do another thing first, link to it inline at the top, ideally inside a Prerequisites callout.

## 5. Screenshots

DocSend's screenshot discipline is **uniform to the point of being conspicuous**: every one of the 15 saved pages has **7 content images** (`asset_count` in [`index.json`](index.json) — most pages show 9, but 2 are footer/social icons that survived the deny-list). This consistency suggests a per-page screenshot quota or template.

Observed rules:

- **Placement: above the step they illustrate.** Within a numbered list of steps, the screenshot appears immediately under the step it shows. Never at the top of a section as a "hero" image.
- **One screenshot per major UI state, not per click.** A multi-click workflow gets one screenshot showing the relevant panel, not one per click.
- **Crop: tight to the UI region.** Screenshots are cropped to the link-settings modal, the access-list panel, etc. The surrounding Dropbox app chrome is omitted. The crop boundary appears to be the dialog/panel border + a small margin.
- **Annotations: minimal.** Most screenshots are clean captures with no arrows, circles, or numbered markers. Where emphasis is needed, the surrounding prose carries it ("Click **Edit Permissions** to open the access list").
- **Visitor-side screenshots.** Pages dedicate a section ("Visitor experience") to what the recipient sees, with its own screenshot — a strong pattern for any product where the recipient experience differs from the sharer's.
- **Alt text.** Images carry descriptive alt text matching the section they're in (sample inspection — not exhaustive).

**Takeaway for SpecterX:** target ~5–8 content screenshots per workflow page, placed inline above the step they illustrate. Crop tight. Avoid annotations unless the prose can't make the point. Always include a "What the recipient sees" section with at least one screenshot whenever the recipient view differs from the sharer view (every SpecterX share workflow qualifies).

## 6. Page-worthy vs. assumed knowledge

**Documented (and worth documenting):**
- Every distinct link-security mechanism (see §3)
- Plan-gating: a one-line banner at the top of every article calls out which plan a feature requires
- "Things to consider" sections that surface the *limits* of a feature (max list sizes, conflicts, what it does NOT prevent)
- Both sender and recipient experiences

**Deliberately not documented (assumed):**
- What an email address looks like
- How to open the Dropbox app
- Generic browser behavior
- Generic concepts like "a CSV file" — referenced casually without explaining what one is

DocSend articles assume basic computer literacy and that the reader is already a Dropbox/DocSend user (they don't onboard you to the product, they help you do a specific thing inside it). Articles do **not** explain the broader Dropbox account structure on every page — they assume you got here on purpose.

**Takeaway for SpecterX:** assume the reader is already a SpecterX user inside the right context. Don't re-explain SpecterX-wide concepts on every page; have one or two foundational pages and link to them. Always document the limits, not just the happy path.

## 7. Voice & language

Confirmed across saved samples (e.g. [`restrict-access-allow-or-block-viewers.html`](pages/help.dropbox.com_share_dropbox-docsend-restrict-access-allow-or-block-viewers.html), [`watermarks.html`](pages/help.dropbox.com_share_dropbox-docsend-watermarks.html), [`agreements.html`](pages/help.dropbox.com_share_dropbox-docsend-agreements.html)):

- **Second person ("you", "your") throughout.** Never "the user" or "one". Examples: "you'll receive an automated email", "your allowed viewers list can include up to 500 email addresses".
- **Imperative for steps.** "Select the document or Space you want to share. Click **Create link**…"
- **Present tense.** Future tense ("you'll receive") only for downstream effects.
- **Contractions allowed.** "you'll", "doesn't", "can't" — feels conversational, not corporate.
- **Active voice dominates.** Passive only for facts about the system ("This will automatically add the unauthorized visitor email to your Block List").
- **Product feature names are Title Case.** "Allow Viewers", "Block Viewers", "Access List", "Create link" — even mid-sentence. UI button names are bold.
- **Conversational connectives** add flow: "Just like a visit to a regular DocSend link, you'll receive…", "Depending on what's enabled, you will be given the option to…"
- **Callout grammar.** "**Important:** …", "**Note:** …" — bold label, colon, then a normal sentence. Used sparingly.
- **Sentence length** averages ~18 words. Short, scannable.
- **Headings are noun phrases or imperative phrases.** "Add a watermark to a link", "Manage Your Access List", "Visitor experience".

**Takeaway for SpecterX:** second-person, present tense, imperative steps, contractions allowed, Title Case for product features, **bold** for UI button names, "Important/Note:" callouts only when omitting would cause confusion or errors.

---

## Summary of the strongest DocSend patterns to copy

1. **One feature, one page, with a focused outcome.** Don't pile multiple security controls into one article.
2. **A consistent page skeleton.** Plan-gate banner → 1-paragraph intro → auto-TOC → 2–6 task sections → "Visitor experience" → "Defaults/admin" → "Related articles".
3. **A per-page screenshot quota** (~5–8 content images), placed inline above the step they illustrate, cropped tight to the UI region.
4. **Always document the recipient/visitor experience.** A dedicated "Visitor experience" section with at least one screenshot.
5. **Always state the limits.** A "Things to consider" or similar section that explains what the feature does NOT do.
6. **Second-person, imperative, contractions, bold for UI labels.**
7. **"Related articles" = lateral siblings, not next-step.** Don't make the reader do navigational gymnastics.
