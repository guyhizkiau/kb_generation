# HubSpot — Documentation Analysis (Phase 1 draft)

Sources crawled: **17 pages** (see [`index.json`](index.json)). Selection deliberately focused on HubSpot's **connector/integration documentation** — exactly the pattern SpecterX needs for its Gmail and Outlook connectors. Coverage:

- The full **HubSpot Sales Chrome extension** lifecycle (10 pages): get-started, install, customize, track/log, sales tools, across-the-web, meetings/calendar, contact profiles, troubleshoot, uninstall.
- **Outlook desktop add-in** (2 pages): get-started, troubleshoot.
- **Office 365 / Outlook on the web add-in** (2 pages): get-started, contact profiles (shared with desktop add-in).
- **Cross-provider connected inbox** (1 page): which features need which kind of mailbox connection.
- **Account & security exemplars** (2 pages): SSO setup, password reset.

HubSpot is the **primary reference** in this set for connector documentation. The patterns extracted in §0 below directly seed [`guidelines/PAGE_TEMPLATE.md`](../../guidelines/PAGE_TEMPLATE.md) in Phase 2.

> **Phase 1 caveat.** HubSpot's robots.txt is malformed in a way that Python's stdlib parser mis-applies — see [`tools/platforms/hubspot.yml`](../../tools/platforms/hubspot.yml). Crawl uses `respect_robots_txt: false` with the actual robots.txt rules verified manually. Polite rate-limit (1.5s/page) and identifying user-agent unchanged.

---

## 0. The HubSpot connector documentation pattern (BONUS — primary takeaway)

HubSpot documents three host-app connectors (Chrome extension for Gmail, Outlook desktop add-in, Office 365 / Outlook web add-in) using the **same repeatable page set** for each. This is the playbook to copy.

For each connector, HubSpot publishes **a "lifecycle" of pages** (typical 8–12):

```
┌──────────────────────────────────────────────────────────────────────┐
│  CONNECTOR: HubSpot Sales Chrome extension (canonical example)       │
├──────────────────────────────────────────────────────────────────────┤
│ Phase           │ Page                                                │
├─────────────────┼────────────────────────────────────────────────────┤
│ Discover        │  Set up the HubSpot Sales Chrome extension          │
│                 │  ← short landing page that links to everything     │
│                 │                                                     │
│ Install         │  Install HubSpot Sales for Gmail, Office 365,      │
│                 │  and Outlook desktop                                 │
│                 │  ← cross-connector install hub                      │
│                 │                                                     │
│ Configure       │  Customize HubSpot Sales Chrome extension settings │
│                 │  ← default behavior, preferences                    │
│                 │                                                     │
│ Use (primary)   │  Track and log emails with the … Chrome extension  │
│ Use (secondary) │  Use sales tools in the … Chrome extension          │
│ Use (cross-web) │  Use the … Chrome extension across the web          │
│ Use (calendar)  │  Manage meetings in Google Calendar with the …      │
│ Use (CRM-side)  │  Use contact profiles with the … Chrome extension   │
│                 │                                                     │
│ Troubleshoot    │  Troubleshoot the … Chrome extension                │
│                 │                                                     │
│ Uninstall       │  Uninstall the HubSpot Sales email extension        │
└──────────────────────────────────────────────────────────────────────┘
```

Key cross-connector observations:

1. **One landing page per connector.** Title: "Set up the \<connector name\>". Very short (≤500 words). Contains:
   - 1-paragraph **product description**: "The HubSpot Sales Chrome extension is a browser extension for Chrome that allows you to track and log your emails sent from Gmail and use some of the HubSpot sales tools directly in your inbox and across the web." (from [`get-started-with-the-hubspot-sales-chrome-extension`](pages/knowledge.hubspot.com_connected-email_get-started-with-the-hubspot-sales-chrome-extension.html))
   - A **lifecycle-resource list**: "This guide provides a list of resources to get you started with the HubSpot Sales Chrome extension:" followed by a bulleted list of links to install / configure / use / troubleshoot pages.
   - **Cross-references to sibling connectors**: "If you're using the HubSpot Sales Office 365 add-in or Outlook desktop add-in, learn more about getting started with the HubSpot Sales Office 365 add-in or the Outlook desktop add-in." → readers who landed on the wrong connector are redirected.

2. **A shared install hub** ([`how-to-install-hubspot-sales`](pages/knowledge.hubspot.com_connected-email_how-to-install-hubspot-sales.html)) covers install across all three connectors on one page, since the install action is the user's first decision (Chrome? Outlook desktop? Office 365?). Cross-connector questions (which one should I install) belong on a hub page; per-connector setup (use, troubleshoot, customize) lives on connector-specific pages.

3. **Lifecycle status is explicit.** The Outlook desktop add-in page calls out, on the page, that the add-in is "for Windows only" and "in maintenance mode" — with the rationale (Microsoft's changes to the new Outlook for Windows): "We use cookies to improve HubSpot's site… The HubSpot Sales Outlook desktop add-in allows you to track and log emails, and use some of the HubSpot's sales tools directly in your email account. This add-in is for Windows only and is in maintenance mode. … Please note: due to the significant changes introduced by Microsoft as part of the new Outlook for Windows, HubSpot will no longer actively develop or improve the HubSpot Sales Outlook desktop add-in." (from [`get-started-with-the-outlook-desktop-add-in`](pages/knowledge.hubspot.com_connected-email_get-started-with-the-outlook-desktop-add-in.html))

4. **Action-titles, not feature-titles.** "Track and log emails with the …", "Manage meetings in Google Calendar with the …", "Use sales tools in the …". The verb comes first. Every page title fits the pattern `<Verb phrase> with the <Connector name>`.

5. **Symmetry across connectors.** When a feature exists in two connectors, there's either:
   - **One shared page** describing both (e.g. [`use-contact-profiles-with-the-hubspot-sales-office-365-add-in-and-outlook-desktop-add-in`](pages/knowledge.hubspot.com_connected-email_use-contact-profiles-with-the-hubspot-sales-office-365-add-in-and-outlook-desktop-add-in.html) — explicitly titled to cover both add-ins), OR
   - **Sibling pages** with matching structure (Chrome extension has its own "use contact profiles" page — same H2/H3 structure as its Outlook counterparts).

**Direct application to SpecterX.** When we document the Gmail connector and the Outlook connector (and any future host-app integrations), publish this page set:

```
SpecterX Gmail connector
├── Set up the SpecterX Gmail extension              ← landing
├── (shared) Install the SpecterX email connectors    ← cross-connector install hub
├── Configure default settings
├── Send a SpecterX-protected link from Gmail
├── Use SpecterX sharing controls in Gmail
├── Track recipient activity in Gmail
├── Troubleshoot the SpecterX Gmail extension
└── Uninstall the SpecterX Gmail extension
```

Mirror exactly for Outlook (desktop and OWA). One landing per connector, one shared install hub, action-titled use pages, one troubleshoot, one uninstall.

---

## 1. Hierarchy

HubSpot's URL pattern is `knowledge.hubspot.com/<topic>/<descriptive-slug>`. The IA is **two-level: Topic → Article**. Top-level topics relevant to our crawl:

```
HubSpot Knowledge Base
├── connected-email        ← all email/CRM integration connectors (Chrome, Outlook, Office 365)
├── account-security        ← SSO, MFA, password reset
├── account-and-setup       ← cross-cutting account topics
├── account-management      ← user/license operations
├── integrations            ← marketplace integrations (Zoom, Slack, Salesforce, etc.)
├── account                 ← billing, settings
└── … (many more)
```

- **No URL-level breadcrumb hierarchy.** All "connected-email" pages are siblings at the same depth; there's no `connected-email/chrome-extension/install`. Discovery is by sidebar IA and search.
- **No visible breadcrumbs in the article body.** Like Egnyte, navigation context is delivered by the sidebar (offsite — not in our saved HTML).
- **The topic name groups by capability, not by audience.** "Connected email" doesn't say "for sales reps" or "for admins" — both audiences hit the same topic.

**Takeaway for SpecterX:** keep topic slugs short and capability-based. **Always show breadcrumbs in the page body** (HubSpot doesn't, but it's still a good practice — users land via Google and need orientation).

## 2. Page anatomy

Two clear page types observed (plus the landing exception):

### A. Landing / index pages (Get Started with …)

Short, link-only. Pattern:

```
H1  Set up the <connector name>
    1-paragraph product description.
    1-paragraph: "If you're using <other connector>, learn more about …"
    Section heading (bold paragraph or H2): "Install …"
    Section heading: "Configure …"
    Bulleted list of links.
```

Examples: [`set-up-…-chrome-extension`](pages/knowledge.hubspot.com_connected-email_get-started-with-the-hubspot-sales-chrome-extension.html), [`set-up-…-outlook-desktop-add-in`](pages/knowledge.hubspot.com_connected-email_get-started-with-the-outlook-desktop-add-in.html).

### B. Task pages (the workhorses)

Pattern:

```
H1  <Verb> the <Connector name>
    1–2 paragraphs of orientation:
    "Use the Track and Log features of the HubSpot Sales Chrome extension to monitor and keep a record of …"
    Optional: inline link to "learn more about <related concept>"

H2  Before you get started               ← almost universal preamble
    H3 Understand requirements              ← what the user needs
    H3 Understand limitations and considerations  ← what won't work / caveats
    [Optional: "Permissions required" bold-prefix paragraph]

H2  Configure default … settings          ← admin/setup of the feature
    (Numbered steps with bold UI labels)
    (Inline screenshot per major panel)

H2  <Primary task>                          ← "Tracking emails", "Logging emails", "Send a logged email…"
    H3 sub-tasks
    H3 "View the … in HubSpot"               ← seeing the result in CRM

(Repeat task H2s as needed.)
```

Evidence:
- [`track-and-log-emails-with-the-hubspot-sales-chrome-extension`](pages/knowledge.hubspot.com_connected-email_track-and-log-emails-with-the-hubspot-sales-chrome-extension.html): H2 = Before you get started / Configure default log and track settings / Tracking emails / Logging emails. H3s = Understand requirements / Understand limitations / View the tracked email's status / Tracking with data privacy settings turned on / Send a logged email using the Chrome extension / View the logged email in HubSpot.
- [`set-up-single-sign-on-sso`](pages/knowledge.hubspot.com_account-security_set-up-single-sign-on-sso.html): H2 = General setup / Instructions for specific identity providers / FAQs. H3s under "Instructions" = Okta / OneLogin / Microsoft Entra ID / Google. H3s under "FAQs" = specific question strings like "Which binding does HubSpot use as an SAML service provider?".

**Length range:** 1,500–2,800 words for full task pages. Shorter (≤500) for landing pages and uninstall.

**Takeaway for SpecterX:**

- **"Before you get started" is the single most copy-worthy H2 in this set.** It collects prerequisites + limits + permissions in one predictable place at the top of every page.
- **The (Configure → Use → View result) pattern** matches the natural workflow.
- **Multi-vendor sections use H3 per vendor** (the SSO page is the canonical example — Okta / OneLogin / Entra ID / Google as siblings). Use this when documenting any multi-IdP, multi-cloud, or multi-platform feature.

## 3. Page scope — what gets its own page

HubSpot's split rules are explicit:

- **Each verb gets its own page.** Track-and-log / Use sales tools / Manage meetings / Use contact profiles / Use across the web — all sibling pages, all titled with their action verb.
- **A landing page per connector orients to the verb pages.**
- **One shared install hub** for all three connectors (not three separate install pages) — because *the install decision is "which connector?"*, not "how to install Chrome extension".
- **Same-feature, multi-connector docs.** When two connectors implement the same feature, HubSpot will either share one page (titled to cover both) or duplicate sibling pages with matching structure. They explicitly *do not* hide one connector's feature inside another connector's docs.
- **Troubleshooting gets its own page per connector**, organized by H2 problem category (Updates / Accessibility / Tracking / Notifications / Errors / Debug logs) with H3 = specific problem statement.
- **Uninstall gets its own page**, even though it's short — discoverable via search ("how to uninstall HubSpot Sales").

**Inferred rule:** a page = one verb the user explicitly clicks/intends. Install, customize, track, log, manage meetings, use across web, troubleshoot, uninstall — each a separate page.

**Takeaway for SpecterX:** for each connector, publish ≥ 8 pages following this verb-split. Same rule applies to non-connector features (e.g. classification: configure / apply / view / change / remove, each its own page).

## 4. Cross-references between pages

Stronger and more aggressive than DocSend, Egnyte, or Vera:

- **Cross-connector redirects in the intro** (paragraph 2 of every landing page) point readers to sibling connectors. "If you're using the HubSpot Sales Office 365 add-in or Outlook desktop add-in, learn more about getting started with …"
- **Inline links to dependency concepts.** "Learn more about the difference between tracking and logging." — at the top of [`track-and-log-emails-with-the-hubspot-sales-chrome-extension`](pages/knowledge.hubspot.com_connected-email_track-and-log-emails-with-the-hubspot-sales-chrome-extension.html).
- **"Permissions required" inline callout-paragraph** with a link to the permissions reference. Short, predictable formatting.
- **Long, FAQ-style H3 questions inside the same page.** The SSO setup page bundles FAQs at the bottom as a section, not as a separate "FAQ" page. This **reduces cross-page hopping for adjacent questions**.

HubSpot does **not** use a "Related articles" footer block in the saved articles. Cross-refs are entirely inline.

**Takeaway for SpecterX:**
1. **Top-of-page cross-connector redirects** are essential for connectors.
2. **Bundle FAQs into the parent task page**, not as a separate page, when the FAQs are setup-related ≤10 items.
3. Use **predictable inline cross-ref formats**: "Learn more about \<linked-concept\>." and "Permissions required \<bold paragraph\>".

## 5. Screenshots

HubSpot's screenshot density is **high on task pages** and **deliberately low on landing pages**. Verified counts from [`index.json`](index.json):

| Page | Images |
|---|---|
| Troubleshoot the … Chrome extension | 76 |
| Track and log emails | 52 |
| Use sales tools | 47 |
| Use the … Chrome extension across the web | 47 |
| Customize Chrome ext settings | 40 |
| Uninstall the … email extension | 40 |
| Manage meetings in Google Calendar | 35 |
| Set up single sign-on (SSO) | 34 |
| Troubleshoot the … Outlook desktop add-in | 34 |
| Reset user passwords | 28 |
| Use contact profiles (Chrome) | 28 |
| Use contact profiles (Outlook) | 28 |
| Install HubSpot Sales (cross-connector hub) | 22 |
| Set up the … Office 365 add-in | 22 |
| Set up the … Chrome extension (landing) | 4 |
| Set up the Outlook desktop add-in (landing) | 4 |
| Requirements to use HubSpot tools | 4 |

The pattern is crystal clear: **landings are screenshot-light (≤5); task pages are screenshot-heavy (≥20, often ≥40)**. Troubleshooting is the densest because every problem state needs a visual.

Patterns observed:

- **Inline placement, immediately below the step.** Like DocSend, but more screenshots per step.
- **GIFs / short animations** are used inline for actions that are hard to capture in a single still (a click revealing a dropdown, a drag).
- **Crops are full-panel, not full-window.** Tighter than Egnyte, looser than DocSend.
- **No annotations / arrows / numbered overlays** in the screenshots. Prose carries pointing.
- **Repeated UI screenshots are accepted.** Same Gmail compose window appears across multiple pages — HubSpot does not try to dedupe screenshots across the lifecycle pages.
- **Visual continuity is high.** Each page's screenshots share the same Chrome/Gmail chrome, same fake-data avatars, same email subject lines — strongly suggests a single recording session per connector lifecycle.

**Takeaway for SpecterX:**

- **Target ~5–10 screenshots per task page**, more for long workflows. Don't be uniform: short landing pages and uninstall don't need many.
- **Use GIFs for click-reveal interactions** (dropdowns, expandable rows, panel transitions). Not for full task flows.
- **Plan a "recording day" per connector** so all screenshots come from the same demo account and look visually consistent.

## 6. Page-worthy vs. assumed knowledge

**Documented:**
- Every verb the user can perform with the connector
- A separate install page that covers the *decision* of which connector to install
- "Before you get started" with prerequisites, limitations, permissions
- Lifecycle/status callouts (maintenance mode, deprecation, beta)
- Troubleshooting per problem category
- FAQ blocks inside setup pages (when there are <10)
- Multi-vendor / multi-IdP instructions (SSO — Okta / OneLogin / Entra ID / Google as H3 siblings)

**Deliberately not documented (assumed):**
- General concepts of CRM, contacts, deals, pipelines (assumed reader is HubSpot-aware)
- How email works in general
- How to install Chrome itself (linked out to vendor docs)
- Identity-provider setup *on the provider's side* (HubSpot covers only the HubSpot-side configuration; expects the reader to have admin access to their own Okta/Google Workspace)

**Takeaway for SpecterX:** for every connector page, document the SpecterX side of the integration only — link out to the host application (Gmail Help, Microsoft Docs) for browser- or mail-client-level steps. Don't try to re-host their docs.

## 7. Voice & language

Confirmed across all 17 saved pages:

- **Strict second person.** "Use the Track and Log features … to monitor and keep a record of **your** contacts' engagement with **your** emails." No "the user" or 3rd person observed in the sample.
- **Imperative for steps.** "In the left sidebar menu, under **Data Management**, navigate to **Objects**." Heavy use of bold for UI labels.
- **Bold for every UI label.** "Click the **Select an object** dropdown menu and select **Activities**." Every named button, menu, tab, checkbox, dropdown is bolded. **The most consistent formatting pattern across the sample.**
- **Action-titled headings.** "Tracking emails", "Logging emails", "View the logged email in HubSpot" — gerund + noun phrase. Sentence case.
- **Inline product capitalization.** "HubSpot Sales Chrome extension" / "HubSpot Sales Outlook desktop add-in" — full product name spelled out the first time, often the second too. Doesn't abbreviate to "the extension" mid-paragraph (despite the prose getting wordy).
- **Permissions called out by name.** "Permissions required Super Admin permissions are required to configure default behavior …" — a recurring formatting pattern, almost an in-line callout.
- **"Please note:" and "Please:" callouts** appear inline as bold prefixes — slightly more formal than DocSend's "Note:".
- **Status callouts inline.** "This add-in is for Windows only and is in maintenance mode." Sits right in paragraph 2 of the article, calls out lifecycle status before the reader invests time.
- **Conditional opening clauses.** "Before you begin working with the HubSpot Sales Chrome extension, review the requirements and limitations …" — sets context first.
- **Contractions allowed**, sparingly. "It's recommended …", "you'll need …".

**Takeaway for SpecterX:** HubSpot's voice is the cleanest in this set for connector docs.
- **Strict 2nd person.**
- **Bold every UI label, every time.**
- **Sentence-case headings.**
- **"Before you get started" / "Permissions required" / "Please note:" as canonical inline-callout formats.**
- **Spell out the full connector name** at every mention until the user is clearly oriented; the wordiness is a feature, not a bug, because users skim and need the connector to be unambiguous.

---

## Summary of the strongest HubSpot patterns to copy

1. **The connector lifecycle page set** (§0): one landing, one shared install hub, action-titled use pages, one troubleshoot, one uninstall — **directly adopt for SpecterX Gmail + Outlook connectors.**
2. **"Before you get started" as the universal first H2** of task pages, with H3 = Requirements + Limitations + Permissions.
3. **Cross-connector redirects in paragraph 2 of every landing page.**
4. **Multi-vendor H3 siblings inside one page** (SSO IdP setup — Okta / OneLogin / Entra ID / Google).
5. **Bold every UI label.** Every time.
6. **Action-titled, sentence-case headings.**
7. **Lifecycle status callouts inline** (maintenance mode, beta, deprecation).
8. **GIFs for click-reveal interactions.**

## Patterns NOT to copy from HubSpot

1. **No breadcrumbs.** Always add them — users land via Google.
2. **No "Related articles" footer at all.** A small one helps lateral discovery without much cost.
3. **The 1,500-2,800-word range is long.** SpecterX should target ≤1,800 for connector task pages.
