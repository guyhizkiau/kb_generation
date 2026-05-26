# Virtru — Documentation Analysis

Sources sampled: the full `support.virtru.com` homepage structure (all categories/sections/article titles extracted via live browser crawl) + two key articles read in full: "Read a Virtru Encrypted Email without Virtru Installed" (recipient) and "Send secure messages via Outlook 365 Add-in" (sender/connector). Virtru runs on Zendesk.

Virtru is the **most direct functional competitor to SpecterX** in this reference set: Gmail and Outlook extensions for email encryption, a recipient-side Secure Reader, file protection, access revocation, verification flows (email OTP, SMS, Google/Microsoft SSO). Treat all conclusions here as high-relevance.

---

## 1. Hierarchy

```
Virtru Support Center (support.virtru.com)
├── Virtru for Recipients           ← audience-first, SEPARATE top-level section
│   ├── Access Secure Emails & Files
│   │   ├── Read a Virtru Encrypted Email without Virtru Installed
│   │   ├── View a Secure File Shared with You via Virtru Secure Share
│   │   ├── Reading Virtru Encrypted Content without Virtru Installed
│   │   ├── Reply to a Virtru Encrypted Email without Virtru Installed
│   │   ├── Share a Virtru Secured File without Virtru Installed
│   │   ├── Using SMS for secondary verification
│   │   ├── Open a Virtru Encrypted Google Drive File without Virtru Installed
│   │   ├── Accessing a tdf.html File (Persistent File Protection)
│   │   └── Request Access Workflow (for Recipients of tdf.html files)
│   ├── Troubleshooting for Recipients (15 articles)
│   └── FAQs for Recipients
│
├── Virtru for Users                ← end-user senders
│   ├── General (Get Started / Managing Content / Cross-Platform Troubleshooting)
│   ├── Google
│   │   ├── Gmail
│   │   └── Drive
│   ├── Outlook
│   │   ├── Virtru for Outlook 365 add-in       ← sub-section with lifecycle articles
│   │   ├── Virtru for Outlook Desktop extension ← separate sub-section
│   │   └── What is the difference between...?   ← disambiguation FAQ article
│   ├── Secure Share (main + Zendesk / Google Drive / OneDrive-SharePoint-Teams)
│   └── Mobile (iOS, Android, troubleshooting, uninstall)
│
├── Virtru for Admins               ← admin senders
│   ├── Install & Deploy Virtru for Admins
│   │   ├── Gmail Extension
│   │   ├── Outlook Add-in
│   │   ├── Secure Share (+ integrations)
│   │   ├── Drive Extension
│   │   └── Mobile Apps
│   ├── Manage Users & Admins (Control Center, Managing Users, Syncing)
│   ├── Organization Settings & Features
│   │   ├── General
│   │   ├── Security Rules (formerly DLP)  ← equivalent of SpecterX's policy controls
│   │   ├── SAML
│   │   ├── Custom Branding
│   │   └── Audit Page
│   ├── Manage Emails & Files for Admins (Org Data Page, eDiscovery, Vault)
│   ├── FAQs for Admins
│   └── Troubleshooting for Admins
│
├── Advanced Products               ← deployment-complexity content, separate section
│   ├── Virtru Hosted Gateway          ← each follows Prerequisites→Install→Post-install→Reference→About
│   ├── Virtru Customer Hosted Gateway
│   ├── Virtru Data Protection Toolkit
│   ├── Virtru Private Keystore (for Virtru Solutions)
│   ├── Virtru Private Keystore (for Google Workspace CSE)
│   ├── Virtru Google Marketplace
│   ├── Virtru Active Directory Domain Sync
│   └── Virtru Audit Export Client
│
└── Billing & More
    ├── Billing & Payments
    ├── Compliance & Legal (HIPAA, CJIS, FERPA, FIPS 140-2)
    ├── Security & Government Surveillance
    ├── Release Notes (per product: Gmail Plugin, Outlook Desktop Ext., Outlook 365 Add-in, Secure Reader, Secure Share, Customer-Hosted Gateway)
    └── Translated Articles - French
```

Notable IA decisions:

- **"Virtru for Recipients" is a top-level section**, not a sub-section of Users or a "Visitor experience" H2 inside sender articles. Recipients may never have heard of Virtru. They receive a link, click it, and need help. Burying recipient docs inside sender sections forces them to navigate the wrong tree.
- **3 levels of depth** (Audience → Surface → Article), but the Zendesk nav surfaces it cleanly. The breadcrumb on each article shows all 3 levels.
- **Connector-first within Users**: inside "Virtru for Users", the organization is by connector (Google/Gmail, Drive, Outlook 365, Outlook Desktop, Secure Share, Mobile). No cross-connector hub — each connector is a separate sub-section.
- **Disambiguation FAQ article for connectors**: "What is the difference between Virtru's Outlook 365 Add-in and Outlook Desktop Extension?" is a single FAQ that answers the "which one should I install?" question and then points users to the right sub-section. This is Virtru's substitute for HubSpot's shared install hub.
- **Advanced Products isolated from end-user docs**: all gateway/keystore/toolkit content is in its own top-level section, separate from the per-connector user docs. This keeps the main Users and Admins sections clean.
- **Compliance & Legal articles** (HIPAA, CJIS, FERPA, FIPS, ITAR) are in Billing & More, not in Admins. They answer "is Virtru compliant with X?" — a compliance/legal question, not a configuration task.
- **Release notes are per-product** and in Billing & More — not in product-specific sections. They stay out of the main nav flow.

**Takeaway for SpecterX:**
1. Keep §3 "Receive files" as a top-level section — Virtru validates this. Recipients are a distinct audience.
2. Add a disambiguation article to §5 — "Outlook Classic vs Outlook New Add-in: which should I use?" matches Virtru's pattern exactly.
3. Consider adding compliance content (HIPAA, GDPR) to §11 Reference.
4. Add release notes as planned articles in §11 Reference.
5. Restructure §10 "Deploy on-premises" using Virtru's per-product skeleton: About → Prerequisites → Install → Post-install → Reference articles.

---

## 2. Page anatomy

### Recipient article ("Read a Virtru Encrypted Email without Virtru Installed")

```
Breadcrumb: Virtru > Virtru for Recipients > Access Secure Emails & Files
H1  Read a Virtru Encrypted Email without Virtru Installed
    "If you're reading this, you've likely received a Virtru-secured email..."
    (Inline link to "Virtru-secured email" concept)

H4  Please Note:                ← H4 callout, NOT H2/H3
    [If you have Virtru installed, the email auto-decrypts.]
    [If you want to reply, see here.]
    [More detailed step-by-step below.]

H3  Skip to:                    ← mini TOC (only 3 sections)
    How to access and read your message · Threading · Additional Resources

H2  How to access and read your message
    Step 1. Click Unlock Message
    Step 2. Select your email address
    H4  An important note about email aliases
    Step 3. Choose how to verify (Google/Microsoft SSO or Send Verification Email)
    Step 4. Check inbox for verify@virtru.com
    H4  Note: both links must open in same browser and device
    Step 5. Message opens in Virtru Secure Reader
    H4  Attachments (explains .tdf extension, watermarking disables downloads)

H2  Threading
    (Explains secure email threads)

H2  Additional Resources         ← link list (not cards)
    Reply to a Virtru Encrypted Email without Virtru Installed
    Troubleshooting for Recipients
    FAQs for Recipients
    About Virtru

Related articles (5 items)      ← auto-generated by Zendesk
```

### Connector article ("Send secure messages via Outlook 365 Add-in")

```
Breadcrumb: Virtru > Virtru for Users > Outlook > Virtru for Outlook 365 add-in
H1  About                       ← unusual H1 for introductory section
    Product description + "you will first need to install and activate..."
    (Inline link to install article)

H4  Please Note:                ← cross-connector disambiguation callout
    "Virtru offers a separate Outlook Desktop Plugin. If you use that, see here."

H2  Steps to Encrypt
    1. Click New Email
    2. In Outlook Desktop, select Virtru for Outlook / In OWA, open Apps
    3. Turn Virtru Protection On (toggle turns blue)
    4. Add recipients, subject, body, attachments
    5. Hit Send

Recently viewed articles        ← auto-generated
Related articles (5 items)     ← auto-generated
```

Length: both articles are **short** (under 600 words). Virtru's pages are much shorter than Egnyte or HubSpot. Each article does exactly one thing.

**Takeaway for SpecterX:**
- Short article length (under 600 words for task pages) is valid for simple workflows. Match length to complexity.
- "Please Note:" H4 callouts at the top of connector articles for cross-connector disambiguation are a clean pattern. Use this in the Outlook Classic article ("**Please note:** The Outlook New Add-in is recommended for new installations. [See which to choose →]").
- The "About" section as an introductory block (not just a paragraph) deserves consideration for longer feature articles.

---

## 3. Page scope — what gets its own page

Virtru's scope decisions reveal important patterns:

- **Recipient verification methods get their own articles when they have distinct flows**: "Using SMS for secondary verification" is a separate article from "Read a Virtru Encrypted Email" because the SMS flow is meaningfully different (a phone number must be registered, the OTP arrives differently). The main article covers the common case (email OTP); the SMS article is supplementary.
- **"Reply to..." is a separate article**: even though it's closely related to "Read...", replying involves a different action and a different UI path, so it gets its own page.
- **Connector sub-types get separate sub-sections**: Outlook 365 add-in vs Outlook Desktop extension are separate sub-sections, not sub-H2s within one "Outlook" article. They have different install flows, different UIs, and different limitations.
- **"What is the difference?" as a separate disambiguation article**: Virtru answers "which connector should I install?" in a dedicated FAQ article that cross-references both sub-sections. This scales cleanly when connectors have different audiences (new users vs legacy Windows users).
- **Advanced Products each get a consistent article set**: every gateway/keystore product gets the same 5-article structure (About / Prerequisites / Install / Post-install / Reference). Page structure is entirely predictable across advanced products.

**Takeaway for SpecterX:**
1. Verification sub-articles (SMS, personal secret) can be separate articles if their flows are meaningfully different from the main flow — they are supplementary, linked from the main article.
2. Add "Outlook Classic vs Outlook New — which should I use?" as a disambiguation FAQ to §5.
3. §10 "Deploy on-premises" should use Virtru's 5-article product structure for the Gateway: About / Prerequisites / Install / Post-install / Reference.

---

## 4. Cross-references between pages

- **"Please Note:" H4 callouts for cross-connector refs** at the top of connector articles.
- **Inline links in step content**: "Install and activate" links in the intro paragraph of send articles. "Troubleshoot" links within error callouts.
- **"Additional Resources" link list** at the bottom of recipient articles (Egnyte-style, plain links, not cards).
- **"Related articles" auto-generated by Zendesk** (5 items, bottom of page). These appear to be based on article views/clicks rather than manual curation.
- **No "In this article" auto-TOC** for short articles (under 3 H2s). A "Skip to:" H3 serves the same purpose for longer articles (the recipient article has 3 H2s and uses "Skip to:").

**Takeaway for SpecterX:** The "Please Note:" cross-connector callout at the top of connector articles is the most copy-worthy Virtru pattern. It prevents a reader who landed on the wrong connector article from wasting time before they realise they're in the wrong section.

---

## 5. Screenshots

Not observable from the article snapshots (iframes or auth-gated images). Based on the article structure (short pages, simple flows), Virtru likely uses 2–5 screenshots per task page. The Zendesk platform supports inline images.

---

## 6. Unique patterns not in the other 4 reference KBs

1. **Recipient as a top-level audience** (not a section within sender docs).
2. **Connector disambiguation FAQ article** for choosing between two similar connectors.
3. **Advanced Products as a separate isolated section** (deployable infrastructure separate from user/admin docs).
4. **Per-product release notes** in a dedicated section (not inline with product docs).
5. **Compliance & Legal articles per regulatory framework** (HIPAA, CJIS, FERPA, FIPS, ITAR) — enterprise customers search for these by framework name.
6. **H4 "Please Note:" callout** at the top of articles for cross-connector disambiguation — lighter-weight than HubSpot's inline paragraph.

---

## Summary of the strongest Virtru patterns to copy

1. **Recipient as a top-level KB section** (validates §3 "Receive files").
2. **Disambiguation FAQ article** for Outlook Classic vs Outlook New ("which should I use?").
3. **"Please Note:" H4 cross-connector callout** at the top of each connector article, pointing users to the right one.
4. **Per-product Advanced Products structure**: About → Prerequisites → Install → Post-install → Reference (applies to §10 Deploy on-premises).
5. **Compliance articles per regulatory framework** in §11 Reference.
6. **Per-product release notes** as planned articles in §11 Reference.
7. **Short, single-action articles** (under 600 words for simple connector tasks).

## Patterns NOT to copy from Virtru

1. **H1 "About" section header** — using H1 for a descriptive section inside a page is unconventional and creates heading-level confusion.
2. **Auto-generated "Related articles"** only — Virtru appears to rely on Zendesk's auto-generation rather than manual curation. Manual curation (DocSend/Egnyte pattern) produces more relevant suggestions.
3. **"Skip to:" H3 instead of "In this article" H2** — our existing "In this article" H2 TOC is cleaner and more universally understood.
