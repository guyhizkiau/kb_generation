# What to Expose in a Public Product Knowledge Base

A synthesis of the five reference KBs we crawled (HubSpot, Egnyte, Dropbox DocSend, Vera/Tricentis, Virtru) and the cross-cutting patterns in [`compare.html`](../reference-library/site/compare.html). The question this answers, in detail:

> **What kinds of information should be exposed to the public in a product KB?**

The answer breaks into three layers:

1. **What every public KB publishes** — the categories of content that are non-negotiable for a credible product KB.
2. **What every public KB deliberately omits** — content classes that are either assumed knowledge, belong somewhere else (marketing, security, sales), or would actively harm the product if exposed.
3. **How exposure decisions are scoped by audience and by sensitivity** — the same fact can be public for one audience and gated for another; some facts about security controls have to be deliberately under-described.

---

## TL;DR

A public product KB should expose, for each user-visible capability, the **what / who / where / how / what-if / what-next** of using it — and explicitly enumerate its **limits, prerequisites, supported environments, and recipient/visitor experience**. It should *not* expose internal architecture, unshipped features, attack surfaces, third-party host-app instructions, or boilerplate that the reader is presumed to already know.

The five KBs converge on roughly **15 categories that always appear** and **roughly 10 categories that are always omitted**. The differences between the platforms are differences of degree (how many screenshots, how strict the audience split) — not of which categories of content are public.

---

## 1. What every public KB publishes

Each subsection below is a category of content that appears across **all five** reference KBs (HubSpot, Egnyte, DocSend, Vera, Virtru) — sometimes as a dedicated page, sometimes as a section, sometimes as an inline callout, but always present. The category is "non-negotiable" if a credible KB without it would feel evasive.

### 1.1 Product description — "what this is, in one paragraph"

Every connector landing, every feature page, and every section index opens with a 1–2 sentence statement of what the product / surface / feature is and what problem it solves. It is short, declarative, and uses the full product name.

- **HubSpot:** _"The HubSpot Sales Chrome extension is a browser extension for Chrome that allows you to track and log your emails sent from Gmail and use some of the HubSpot sales tools directly in your inbox and across the web."_
- **Vera:** Section index pages are _"This comprehensive guide provides …"_-style orientation paragraphs, then a link list.
- **Virtru:** Recipient article opens with _"If you're reading this, you've likely received a Virtru-secured email…"_ — orients the reader before any step.

**Why public:** sets context for a reader who landed via Google search and may never have heard of the product/feature.

### 1.2 Lifecycle page set per surface (discover → install → configure → use → troubleshoot → uninstall)

For any **installable surface** (browser extension, mail-client add-in, desktop app), every KB publishes a full lifecycle of pages — not a single mega-page.

- **HubSpot Sales Chrome extension** publishes 10 lifecycle pages: get-started, install, customize, track/log, sales tools, across-the-web, meetings, contact profiles, troubleshoot, uninstall (see [`sources/hubspot/README.md`](../reference-library/sources/hubspot/README.md) §0).
- **Virtru** mirrors this for Outlook 365 Add-in, Outlook Desktop Extension, Gmail Plugin, Drive Extension, Mobile, Secure Share — and isolates the deployable infrastructure (Gateway, Keystore, Toolkit) into its own "Advanced Products" section with a consistent 5-article skeleton (About → Prerequisites → Install → Post-install → Reference).
- **Egnyte** splits the Outlook add-in into an explicit **User Guide** and **Configuration Guide** by audience.

**Why public:** uninstall and troubleshoot are first-class user actions. Hiding them is interpreted as "the product is hard to leave" or "the vendor doesn't acknowledge problems."

### 1.3 Per-feature task pages — "one verb the user explicitly clicks"

Every KB has a page-scope rule that produces a focused per-task article. The exact granularity differs:

| Platform   | Rule                                                           |
| ---------- | -------------------------------------------------------------- |
| HubSpot    | One user-visible verb per page (Install / Customize / Track …) |
| Egnyte     | Audience-based + concept-based split                           |
| DocSend    | One feature + one outcome = one page                           |
| Vera       | One UI menu entry per page (very granular)                     |
| Virtru     | One action per article; closely related actions get siblings   |

**What this means for "public exposure":** every action the UI exposes to the user must be documented as a discoverable, search-indexable page, with a title that matches what the user would type into Google ("How do I revoke access to a SpecterX link?") and a URL that includes that phrase.

### 1.4 Prerequisites — what the reader needs before starting

All five KBs surface prerequisites prominently, either as the universal first H2 (HubSpot's _"Before you get started"_), a dedicated _"Prerequisites"_ H2 (Egnyte, Vera install pages), or a one-line gating banner (DocSend's plan-gate banner). The category includes:

- Required SpecterX plan / license tier
- Required role or permission level
- Required host application (Chrome version, Outlook version, OS)
- Required identity provider / SSO configuration
- Required infrastructure (e.g., the Mail Protection Server must be deployed before the Mail Protection Service can be configured)
- Required data prerequisites (the user must have a configured storage connector before they can share from it)

**Why public:** prerequisites are the single most-skipped read in technical docs. Burying them costs hours of failed-setup support tickets.

### 1.5 Permissions / role requirements — "who can do this"

Documented inline at the top of every task. HubSpot's canonical pattern is the inline callout: _"**Permissions required** Super Admin permissions are required to configure default behavior …"_ — formatted as a bold-prefix paragraph, not a banner.

For SpecterX this means stating, on every admin-facing page, whether the action requires:

- Organisation Admin
- Workspace Admin
- Policy Manager
- Standard user (just the default role)
- A specific permission flag (e.g., "Export audit logs" requires the audit role)

**Why public:** a reader who lacks the permission needs to know that immediately, so they can request access or hand the task off — not at step 7 of a 10-step procedure.

### 1.6 Supported configurations — OS, browser, license, host versions

All five KBs publish explicit support matrices for any feature that depends on the host environment.

- **Egnyte:** _"Supported Outlook Client Configurations"_ and _"Supported Office Licenses"_ are H2 sections on the Outlook config guide.
- **HubSpot:** matched at the page-content level (_"This add-in is for Windows only and is in maintenance mode"_ — inline lifecycle status).
- **Virtru:** Advanced Products each ship a "Prerequisites" article that enumerates supported environments.
- **Vera:** has a dedicated top-level **System Requirements** section.

For SpecterX the matrix has to cover: supported browsers (sender + recipient), supported Outlook variants (Classic / New / OWA), supported Gmail surface (web / mobile), supported storage integrations, supported IdPs, supported file types for viewing / watermarking / encryption.

### 1.7 Plan / tier gating callouts

When a feature is gated behind a plan or add-on, every KB publishes that fact at the top of the article. DocSend has the strongest pattern: a one-line banner above the intro paragraph (_"This article describes a feature available on DocSend Advanced …"_). HubSpot uses an inline callout. Egnyte uses a "For Admins" H2 to gate admin-only sub-features.

**Why public:** if the reader can't access the feature on their plan, they need to know in the first 10 seconds — not after reading 1,500 words.

### 1.8 Step-by-step instructions with screenshots

Universal. The exact density differs (DocSend ~7 per page uniform; HubSpot 20–76; Egnyte 11–88; Vera 0–3; Virtru 2–5 estimated) — see [`compare.html`](../reference-library/site/compare.html) "Screenshot density".

A public KB exposes:

- Numbered steps (`<ol>`) with one verb per step
- A screenshot per major UI state (not per click)
- UI element labels in **bold** to match the on-screen text
- Bold UI labels are the **single most consistent formatting pattern** across all five KBs

### 1.9 Result / outcome — "what you see after the action"

The Configure → Use → **View result** triplet is HubSpot's canonical body shape. The result section is short ("You'll see the logged email appear on the contact's record in HubSpot") and is often paired with a screenshot of the post-action state. Skipping it leaves the reader unsure whether their action worked.

For SpecterX, the result section is especially important on:

- **Share workflows** — what the sender sees after clicking Share (and the email confirmation)
- **Policy changes** — the new Parent policy is reflected in the Share & Permissions Drawer
- **Revocation** — the recipient experience after revocation

### 1.10 Recipient / visitor experience — "what the other side sees"

DocSend has the cleanest pattern: a dedicated **"Visitor experience"** H2 on every share page, with at least one screenshot. Virtru goes further and makes _"Virtru for Recipients"_ a **top-level KB section** of its own — recipients may never have heard of the product and shouldn't have to navigate the sender tree to find help.

For SpecterX, every share-related article must document:

- What the recipient sees in their inbox (the notification email)
- What the Recipient Page looks like
- What verification steps the recipient has to complete (and which method — email OTP, SMS, SSO)
- What the SpecterX Viewer looks like and what it can / cannot let the recipient do (download, print, copy, forward, reply)
- What happens after revocation (the link stops working — what error does the recipient see?)

**This is the single most under-served audience in most enterprise security products' docs.** Virtru's structural decision to elevate recipients to a top-level audience is the single most copy-worthy IA decision in the five-platform set.

### 1.11 Constraints / known limitations — "what this doesn't do"

Every KB publishes limits, just under different names:

| Platform | Where limits live                                                          |
| -------- | -------------------------------------------------------------------------- |
| HubSpot  | _"Understand limitations and considerations"_ H3 inside "Before you get started" |
| Egnyte   | _"Known Limitations"_ H2 on installable-component pages                    |
| DocSend  | _"Things to consider"_ H2 (e.g., max 500 emails on allow-list)             |
| Vera     | Dedicated top-level **Constraints** section + inline parentheticals        |
| Virtru   | Inline H4 _"Please Note:"_ callouts                                        |

This category is the most-skipped category in vendor docs and the **first thing enterprise IT readers look for** before deploying.

For SpecterX, the canonical limits to publish include:

- File-size limits on upload, share, viewer, watermarking
- File-type limits (watermarking is PDF/DOCX/XLSX/PPTX only)
- Per-policy limits (max recipients per share, max recipients per policy)
- Concurrency / rate limits (how many shares per minute, how many notifications per hour)
- Behavioral limits ("Disabling download does not prevent screenshots" — see §3 below for how to write this honestly)

### 1.12 Lifecycle / status callouts (beta, GA, maintenance mode, deprecated, version-specific)

Every KB except DocSend has a documented pattern for "this feature is in a non-steady state":

- **HubSpot:** inline status line in paragraph 2 (_"This add-in is in maintenance mode"_).
- **Vera:** inline _"New in Vera 2023.2"_ annotations.
- **Egnyte:** version-specific notes inline.
- **Virtru:** dedicated per-product release notes section in "Billing & More".

For SpecterX, publishable status callouts include:

- Beta / Early Access
- General Availability
- Deprecation timeline (with sunset date)
- Maintenance-mode (Outlook Classic Connector, if applicable)
- Version-introduced annotations on capabilities

**Why public:** the reader is choosing to invest time. If the feature is going away or recently changed, they need to know before they invest.

### 1.13 Cross-references — inline links + a short "Related" footer

All five KBs publish cross-references, just at different intensities:

| Platform | Cross-reference pattern                                                       |
| -------- | ----------------------------------------------------------------------------- |
| HubSpot  | Inline + cross-connector redirects in paragraph 2 + FAQs bundled in-page      |
| Egnyte   | Inline + **"Additional Resources"** plain-link footer                          |
| DocSend  | Inline + **"Related Articles"** 4-card footer (lateral siblings)               |
| Vera     | IA-driven, minimal inline; section index is the table of contents             |
| Virtru   | Inline + H4 _"Please Note:"_ cross-connector callouts at the top + Zendesk auto-related |

**For SpecterX:** combine the strongest patterns — top-of-page disambiguation callout for connectors (Virtru), inline links for dependencies (all platforms), a small curated "Related" footer for lateral discovery (DocSend / Egnyte), and bundled FAQs in-page when there are ≤10 (HubSpot).

### 1.14 Disambiguation pages — "which one should I use?"

When a product exposes multiple connectors or sub-products that solve overlapping needs, every mature KB publishes a **disambiguation article** that helps the reader pick:

- **HubSpot** uses a shared install hub: _"Install HubSpot Sales for Gmail, Office 365, and Outlook desktop"_ — the install hub answers _which_ before _how_.
- **Virtru** uses a dedicated FAQ article: _"What is the difference between Virtru's Outlook 365 Add-in and Outlook Desktop Extension?"_
- **Egnyte** does this with audience-based splits — separate User Guide and Configuration Guide pages for the same feature.

For SpecterX this is critical for:

- Outlook Classic Connector vs Outlook New Connector
- Gmail Connector vs Google Drive Connector (when both apply to the same workflow)
- Mail Protection Server vs Mail Protection Service (different deployment models)
- Storage connectors (S3, GCS, SharePoint, Egnyte) — which one fits which org?

### 1.15 Troubleshooting — per surface, per problem category

Every KB except Vera publishes a per-surface troubleshooting page organised by problem category (Updates / Tracking / Notifications / Errors / Debug logs as H2; specific problem as H3 — HubSpot's structure). Virtru cleanly separates _"Troubleshooting for Recipients"_, _"Troubleshooting for Users"_, _"Troubleshooting for Admins"_, and a cross-platform troubleshooting page.

**Why public:** support deflection. Every well-organised troubleshooting page is one fewer ticket.

### 1.16 Reference content — IDs, codes, formats, file types, supported integrations

All KBs publish a reference layer alongside the task layer:

- Supported file types and what each supports (viewing / watermarking / encryption / signing)
- Supported browsers and minimum versions
- Supported identity providers and their setup requirements
- Permission matrix (who can do what — Egnyte has its own page; HubSpot has an SSO permissions reference; Vera has the "User & Role" admin docs)
- API references (HubSpot, Virtru) — separate from task docs
- Error code references (more common in admin troubleshooting)
- Glossary of product-specific terms (Workspace, Policy, Parent Policy, Verification, Co-Owner, Contributor)

### 1.17 Compliance & legal attestations (per framework)

Virtru is the strongest example: dedicated articles per regulatory framework — HIPAA, CJIS, FERPA, FIPS 140-2, ITAR — under a top-level "Compliance & Legal" section. Enterprise customers search by framework name and expect a yes/no answer plus the scope of the attestation.

For SpecterX, publishable compliance content includes:

- GDPR posture
- SOC 2 (with current report status and how to request it)
- HIPAA posture
- ISO 27001
- Sub-processor list
- Data residency options
- Audit log retention and export

This category is half KB, half Trust Center — but it belongs in the public KB because enterprise prospects expect to find it via Google.

### 1.18 Release notes — per product, in a dedicated section

Virtru ships per-product release notes (Gmail Plugin, Outlook Desktop Ext., Outlook 365 Add-in, Secure Reader, Secure Share, Customer-Hosted Gateway) in a separate "Billing & More" section — kept out of the main task-doc flow. Vera ships a _"What's new"_ Key Features page plus a separate technical release notes page.

**Why public:** customers running pinned versions need to know what changed, what fixed, what broke.

---

## 2. What every public KB deliberately omits

The omissions are as informative as the inclusions. Every README in `sources/` contains a § _"Page-worthy vs. assumed knowledge"_ section that catalogues exactly what the platform refuses to document — and the omissions are remarkably consistent.

### 2.1 Generic concepts the audience is presumed to know

- DocSend doesn't explain what an email address is, what "a CSV file" is, or how to open the Dropbox app.
- HubSpot doesn't explain general CRM concepts, what a contact is, how email works in general.
- Egnyte doesn't explain general Outlook usage, what an Active Directory / domain is, or general file-system concepts.
- Vera doesn't explain "approval workflow", "domain user", or "SMTP server".

**The rule:** scope the audience and assume the floor. For SpecterX, do not re-explain on every page what a security policy is, what a workspace is, or what SSO is — link to one foundational article and assume the reader has read it (or will go back).

### 2.2 Third-party host-app instructions

Every KB refuses to host docs that belong on the third party's site:

- HubSpot covers _the HubSpot side_ of integrating with Outlook — it does not document how to use Outlook generally, nor how to install Chrome.
- HubSpot's SSO docs cover the HubSpot side of the integration only — they expect the reader to have admin access to their own Okta/Google Workspace and do not re-host those vendors' setup steps.
- Egnyte links to Microsoft for licensing requirements rather than re-explaining them.

**For SpecterX:** the Gmail Connector docs cover Gmail-side setup that SpecterX-specific. Browser installation, generic Gmail usage, and Workspace admin steps on Google's side link out to Google Help. Same for Outlook, Salesforce, SharePoint, etc.

### 2.3 Internal architecture, system internals, and implementation details

Not one of the five KBs publishes:

- Database schemas
- Service-internal API contracts
- Deployment topology beyond what an admin needs to configure
- Internal microservice names
- Internal team names or org structure
- Internal monitoring / observability data

**Why omit:** these change frequently, leak information that helps attackers, and are not actionable for the public reader. They belong in internal engineering wikis (Confluence) and customer-NDA technical guides, not the public KB.

### 2.4 Anything that materially helps an attacker

Every KB describes its security mechanisms, but **honestly under-describes the limits** of what the controls prevent. DocSend's allow/block-viewers page is the most candid example:

> _"Stay in control; restrict access to a specific set of recipients … While **it's difficult to control whether visitors forward links**, the ability to restrict access helps ensure that only your intended viewers have access."_

DocSend acknowledges the limit honestly without writing an attack guide. This is the right register: state the user-facing behaviour, state the boundary, do not enumerate bypasses.

**For SpecterX:** publish what watermarking, download prevention, screenshot prevention, viewer-only mode, and verification do _and don't_ prevent. State the boundary ("Watermarking is a deterrent; it does not prevent re-photographing the screen") without enumerating exploits. Never publish:

- Internal threat models
- Pen-test findings
- Vulnerability disclosure history (publish a security.txt and a coordinated-disclosure policy instead)
- Specific bypass techniques

### 2.5 Roadmap, unshipped features, internal experiments

No KB in the set publishes roadmaps in the article tree. Beta features are published only after they're available to at least some customers (Vera's release-notes pattern). Unshipped features stay out of the KB entirely — they belong on a product blog or in customer-NDA roadmap calls.

### 2.6 Pricing internals, contract terms, sales playbooks

Pricing pages live on the marketing site, not in the KB. The KB references plan names ("Available on DocSend Advanced …") so the reader knows whether they have access to a feature, but does not republish the price list, contract terms, or commercial caveats.

### 2.7 Support metrics, ticket data, internal SLAs

Not published. The public-facing version is a "Status page" (uptime + incidents), not a KB article.

### 2.8 Customer lists and confidential references

Case studies live on the marketing site, with customer approval. The KB does not name customers in articles.

### 2.9 Personal data of staff or customers

Screenshots are taken from demo accounts with fake data. HubSpot's analysis explicitly notes:

> _"Visual continuity is high. Each page's screenshots share the same Chrome/Gmail chrome, same fake-data avatars, same email subject lines — strongly suggests a single recording session per connector lifecycle."_

For SpecterX, use a dedicated documentation demo tenant with fake users, fake emails, and fake file names — never real customer or staff data.

### 2.10 Boilerplate, marketing copy, and value-prop pitches

KB articles describe behaviour and procedure. Marketing copy ("the world's leading…", "trusted by Fortune 500") belongs on the website. The KB tone is informational, not persuasive.

---

## 3. Audience-driven exposure rules

The same fact can be public-for-one-audience and gated-for-another. The five KBs converge on **three (sometimes four) audiences** and split content accordingly. For SpecterX:

| Audience       | Where they live                                                           | What they need                                                                                                                |
| -------------- | ------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **Recipients** | Top-level KB section (Virtru pattern)                                     | Verification flows, Recipient Page UX, Viewer behaviour, what to do if the link doesn't work, how to reply, troubleshooting   |
| **End users**  | "For Users" or per-surface (Gmail / Outlook / Salesforce / Web)           | Share workflows, policy selection, revocation, recipient activity, mobile use                                                 |
| **Admins**     | "For Admins" or "Configuration Guide" (Egnyte pattern)                    | User provisioning, SSO, policy authoring, governance rules, audit logs, dashboards                                            |
| **Deployers**  | "Advanced Products" or "Deploy on-premises" (Virtru pattern)              | On-prem gateway install, customer-hosted keystore, KMS, sub-processor list, network topology                                  |

**Rule of thumb:** if the same fact is needed by two audiences, write it once and link from both (Egnyte's "User Types" duplication-as-discovery). Do not bury one audience's content inside another audience's tree (the Virtru lesson on recipients).

---

## 4. Sensitive-disclosure decisions for security products

SpecterX is a security product. Public docs sit on a finer line than for a general SaaS product. The five-KB consensus, as it applies to security docs:

| Information class                                                                | Publish?            | How                                                                                |
| -------------------------------------------------------------------------------- | ------------------- | ---------------------------------------------------------------------------------- |
| What a security control does (watermark, password, verification, expiry)         | Yes, fully          | One focused page per control (DocSend pattern)                                     |
| What the control does NOT prevent                                                | **Yes, explicitly** | Stated as a limit, not as an attack ("Watermarking does not prevent re-photographing the screen") |
| The specific bypass techniques                                                   | **No**              | Belongs in internal red-team docs and customer-NDA technical write-ups             |
| Encryption algorithms and key lengths (AES-256, RSA-2048, etc.)                  | Yes                 | Compliance/Reference section                                                       |
| Key management architecture at a customer-facing level (BYOK, HYOK, KMS options) | Yes                 | One page per option                                                                |
| Internal key-rotation cadence and operational procedures                         | No                  | Internal runbooks                                                                  |
| Supported authentication factors                                                 | Yes                 | One page per factor (verification flows)                                           |
| Implementation details of the OTP / TOTP generation                              | No                  | Internal engineering docs                                                          |
| Audit log schema and fields                                                      | Yes                 | Reference section                                                                  |
| Internal audit pipeline / SIEM integration internals                             | No                  | Customer-NDA architecture docs                                                     |
| Compliance attestations (SOC 2, ISO, HIPAA)                                      | Yes                 | Per-framework page (Virtru pattern)                                                |
| Actual SOC 2 / ISO reports                                                       | Gated, not public   | Available under NDA via Trust Center                                               |
| Sub-processor list                                                               | Yes                 | Compliance section                                                                 |
| Pen-test findings, vulnerability counts                                          | No                  | Disclosed under NDA on request                                                     |
| Coordinated disclosure policy                                                    | Yes                 | `/.well-known/security.txt` and a Security Disclosure article                       |

**Principle:** describe the user-facing behaviour and the boundary candidly; do not enumerate exploits; gate the artefacts that contain attack-useful operational detail.

---

## 5. The exposure decision: a simple test

For any candidate piece of information, three yes/no answers decide whether it belongs in the public KB:

1. **Will a customer (sender, recipient, admin, or deployer) need this to do something with the product, evaluate the product, or get unstuck?** If no, it does not belong in the KB.
2. **Is this information SpecterX-specific, or is it generic / belongs to a third party / belongs to the reader's own environment?** If it's not SpecterX-specific, link out instead of re-hosting.
3. **Could publishing this materially help an attacker, leak commercial terms, or expose customer/staff PII?** If yes, gate it or rewrite the disclosure at a safer level of detail.

If all three checks pass — yes-to-customer-utility, yes-to-SpecterX-specific, no-to-harm — publish it.

---

## 6. Practical exposure inventory for SpecterX

Mapping the categories above against the 53 platform components in [`components-inventory.txt`](../product/components-inventory.txt) and the [`ARTICLES_PLAN.md`](ARTICLES_PLAN.md) outline, the public KB should expose:

### Always public (every component)

- Product / component description (1 paragraph)
- Audience (who this is for)
- Prerequisites (plan, role, environment)
- Step-by-step task instructions with screenshots
- UI orientation (the panel, the pane, the drawer — annotated)
- Result / outcome ("what you'll see after")
- Recipient experience (for any share-related component)
- Constraints / known limitations
- Lifecycle status (beta / GA / maintenance / deprecated)
- Troubleshooting (per problem category)
- Related articles / next reads

### Public per surface (one set per connector / integration)

- Connector landing page
- Install / deploy
- Configure
- Use (one page per verb)
- Troubleshoot
- Uninstall
- "What's the difference between X and Y?" disambiguation when two connectors overlap

### Public per audience

- **Recipients:** dedicated top-level section — verification methods, Recipient Page tour, Viewer behaviour, "the link doesn't work" troubleshooting
- **End users:** task pages per workflow, mobile guidance, FAQ
- **Admins:** policy authoring, user / role management, SSO, governance rules, audit logs, dashboards
- **Deployers:** on-prem Gateway and Storage Connector — About / Prerequisites / Install / Post-install / Reference (Virtru pattern)

### Public as reference

- Supported file types matrix (viewing / watermarking / encryption / signing)
- Supported browsers (sender + recipient, mobile and desktop)
- Supported integrations (storage / IdP / mail / DLP)
- Permission matrix
- Glossary of SpecterX terms
- Compliance attestations per framework
- Sub-processor list
- Audit-log field reference
- API reference (when public)
- Per-product release notes
- Security disclosure policy

### Deliberately NOT public

- Internal architecture / service topology / database schemas
- Pen-test findings or vulnerability disclosure history (only the policy)
- Specific bypass techniques for any security control
- Roadmap / unshipped features
- Pricing internals or contract terms
- Customer names (outside marketing-approved case studies)
- Real customer or staff PII in screenshots
- Internal staff names, team org charts
- Generic concepts the audience already knows
- Third-party host-app instructions (Gmail / Outlook / browser / IdP-side setup)

---

## 7. External frameworks and 2026 industry conventions

The five-KB analysis converges with — and is sharpened by — a body of external work on what public product documentation should and should not contain. Five external sources reinforce, refine, and in some cases extend the conclusions above.

### 7.1 The Diátaxis framework — four kinds of content, four user needs

[Diátaxis](https://diataxis.fr/start-here/) is the de facto standard taxonomy for technical documentation. It identifies **four distinct kinds of content**, each serving a different user need, and proposes that every doc page should be cleanly one of them:

| Mode               | Answers                | Oriented to | Analogy                                       |
| ------------------ | ---------------------- | ----------- | --------------------------------------------- |
| **Tutorials**      | "Can you teach me to…?" | Learning    | Teaching a child to cook                      |
| **How-to guides**  | "How do I…?"            | Goals       | A recipe in a cookery book                    |
| **Reference**      | "What is…?"             | Information | Information on the back of a food packet      |
| **Explanation**    | "Why…?"                 | Understanding | An article on culinary social history         |

Two axes: **action vs cognition** (does the user do something, or know something?) and **study vs work** (are they learning, or trying to achieve a goal?).

**How this sharpens our answer.** The categories in §1 of this doc are mostly **how-to** (workflows, configuration, troubleshooting) and **reference** (supported file types, permissions matrix, compliance attestations). Two categories are systematically under-served in the five reference KBs and need explicit attention for SpecterX:

- **Tutorials** — a guided, end-to-end learning experience for a first-time user. None of the five reference KBs has a strong tutorial layer; they assume the reader is competent and already in the product. For SpecterX, the equivalent is a small set of "Get started in 10 minutes" pages per audience (sender / recipient / admin) that walk the user through one realistic end-to-end scenario.
- **Explanation** — discursive, why-this-exists content. The closest analogue across the reference set is a 1-paragraph "what this is" preamble; nobody publishes a substantive _explanation_ of, say, the security model. For SpecterX, conceptual articles ("How SpecterX policies work", "What a Workspace is and why it exists", "How verification protects you and your recipients") are public-worthy and missing from the per-component task plan.

Diátaxis is also explicit about a common anti-pattern: do **not** spin up empty buckets for the four modes and then try to fill them. Let the structure emerge from the content. The 18 categories in §1 of this doc are the natural top-level shape for SpecterX; Diátaxis is the lens for checking that each page is unambiguously one kind of thing.

### 7.2 2026 SaaS help-center conventions

Independent of our five-platform crawl, several recent industry write-ups converge on a consistent set of conventions for public B2B SaaS help centers ([HappySupport 2026 guide](https://happysupport.ai/blog/how-to-build-saas-knowledge-base), [eesel AI](https://www.eesel.ai/blog/how-to-build-knowledge-base), [Helpview](https://helpview.so/blog/help-center-best-practices-2026-deflect-tickets), [Pylon](https://www.usepylon.com/blog/effective-customer-knowledge-base-2026)). The conventions reinforce, and in some cases tighten, the choices the five reference KBs already make.

| Convention                                          | Industry consensus (2026)                                                                                  | How it maps to our findings                                                                                  |
| --------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Top-level categories                                | **4–8 top-level categories**                                                                                | DocSend, Egnyte, HubSpot all sit in this range; Vera has more (because of its strict guide-per-audience IA). |
| Hierarchy depth                                     | **2–3 levels maximum**                                                                                       | All five platforms sit at 2 levels (Vera at 3). 4+ levels is universally rejected.                           |
| Article scope                                       | **One task or one question per article**                                                                     | Convergent with DocSend's "one feature, one outcome, one page" and HubSpot's "one verb per page".            |
| Article types that cover ~90% of content            | **How-to · Troubleshooting · FAQ · Feature overview · Release notes**                                        | Adds "FAQ" and "release notes" as first-class types — both confirmed by Virtru's structure.                  |
| Title pattern                                       | **Verb-first or question-form titles in the user's language** (e.g. "Reset password", not "Password reset")  | Matches HubSpot's action-titled headings discipline.                                                         |
| First-paragraph job                                 | **Answer fast — put the answer in the first paragraph**                                                      | Aligns with the universal 1-paragraph product description but pushes further: the _answer_, not just orientation. |
| Visuals                                             | **Use screenshots only when they remove doubt** (function-first language otherwise)                          | Argues against DocSend's "uniform ~7 per page" quota and for matching density to the page's actual need.     |
| Search-first design                                 | **A prominent search bar is more important than the navigation tree**                                        | None of the five reference KBs surface this explicitly, but their flat-ish IA and rich titling assume it.    |
| Scope decided by data                               | **Start from real ticket themes and repeated searches, not a blank content plan**                            | New angle — see §7.3 below.                                                                                  |

**What this adds.** The most important convention not already in §1 is the **5-template article-type system**. Treating "FAQ" and "release notes" as named templates (rather than ad-hoc content) sharpens the public-vs-private decision: an FAQ answers a single conceptual question in 2–3 paragraphs; if the answer needs steps, it becomes a how-to and the FAQ links to it. This avoids the trap of FAQ pages drifting into multi-task articles that are hard to find and harder to maintain.

### 7.3 Scope decided by ticket and search data, not by product structure

A theme that runs through every 2026 help-center write-up but is **invisible in the five platform READMEs** (because crawled output doesn't reveal it):

> _"The best help centers do not try to document everything at once. They focus on the questions customers ask most, structure content around real tasks, and keep improving the content people actually search for."_ — Helpview

Concretely, the public KB scope should be driven by:

1. **Top support ticket themes for the last 90 days.** Each repeating theme is an article candidate. The article for the #1 theme should be on the help-center home page above the fold.
2. **Repeated in-product and in-help-center search queries.** Zero-result searches and high-volume repeat queries are gaps in the article catalogue.
3. **In-product confusion signals.** Tooltip clicks, "Need help?" button clicks per surface, abandoned-flow telemetry.
4. **Onboarding survey questions** at first-week and first-month checkpoints.

This is exposure-by-demand. It cleanly answers a question §1–§6 don't address: among the 18 publishable categories, **which articles to write first**. The answer is: the ones customers are already asking about.

For SpecterX the practical implication is that the 53-component plan in [`ARTICLES_PLAN.md`](ARTICLES_PLAN.md) should be re-prioritised the moment we have ticket data — write the troubleshoot-for-Outlook-Classic article before the troubleshoot-for-Salesforce-Reports article if the former is the support volume driver.

### 7.4 Where the public KB content actually surfaces (not just the help-center site)

A modern public KB is **multi-surfaced**. The same article body must be addressable from:

- The help-center site itself (the canonical `/help` or `/support` URL)
- In-product help widgets and contextual tooltips (the search widget that surfaces articles by URL context is described as a "force multiplier")
- Onboarding emails (linked to specific articles, not the KB home)
- The chatbot or live-chat flow (KB articles suggested before routing to a human)
- Public search engines (Google) and increasingly LLM-based search/answer engines
- Customer success and support agent tooling (the internal view of the same articles)

**What this adds to "what to expose".** URL stability and addressability are themselves exposure decisions. An article's URL is part of its public contract: in-product help widgets, chatbots, and customer-success email templates all pin to it. The implication for SpecterX:

- Pick URL slugs that are durable (verb + object: `/share-files-from-web`, not `/v2-share-flow`).
- Don't break URLs on rebrands or restructures; redirect.
- Tag every article with the feature/component it covers so that in-product widgets can surface it contextually.

### 7.5 Drift discipline determines what stays public

A 2026 audit of 30 SaaS help centers ([HappySupport](https://happysupport.ai/blog/audited-30-saas-help-centers)) found that the underlying cause of nearly every quality problem in public KBs is the same: **documentation drifts** — UI labels change, flows change, screenshots stale — but the articles don't get updated.

The three "low-decay" help centers in that audit all had a structural coupling between the docs and the product codebase: every product PR triggered a documentation review for affected articles. Two practical principles:

- **Write function-first, not visually.** Reference button labels and feature names ("Click **Share**"), not visual properties ("click the blue button in the top-right"). Visual descriptions stale faster than function names.
- **Use review triggers, not calendar reviews.** Tag each article with the component it covers. When engineering ships a change to that component, surface the affected articles for review immediately.

**What this adds to exposure.** Articles that cannot be kept current should be **demoted or unpublished**, not left to rot. A stale article is worse than a missing article — it actively misleads. The exposure decision for SpecterX therefore has a fourth question on top of the three in §5:

4. **Can we keep this current?** If the article references a UI that changes weekly and we have no review trigger for it, either invest in the trigger or write the article in function-first language that survives the UI change. If neither is possible, don't publish.

---

## 8. Adjacent public surfaces (not the KB, but linked from it)

A mature product publishes several public surfaces _alongside_ the KB. Each has its own scope rules and its own publish-vs-gate boundary. Confusing them with the KB leads to over- or under-disclosure.

| Surface                  | What it exposes                                                                                                 | What it does NOT expose                                                                  |
| ------------------------ | --------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| **Trust Center**         | Compliance posture (SOC 2 type, ISO, HIPAA, FedRAMP), sub-processor list, data-residency options, security FAQ; gated SOC 2 report download under NDA | The actual SOC 2 / ISO report (gated); pen-test findings; internal control catalogue     |
| **Security Advisory page** | Coordinated-disclosure policy; archive of resolved CVEs with affected versions, severity, fix version; PGP key for reporters | Unpatched vulnerabilities; bypass details; internal incident timelines                   |
| **Status page**          | Real-time service status, current/historical incidents, scheduled maintenance, RCA summaries                    | Detailed error logs; customer-specific impact; internal-tooling outages                  |
| **API reference**        | Endpoints, request/response schemas, error codes, auth model, rate limits, versioning policy                    | Internal-only APIs; deprecated-but-undocumented endpoints; SDK internals                 |
| **Roadmap (if public)**  | Themes and quarter-grain dates for in-flight items; recently shipped                                            | Specific commitments to customers; competitive positioning; engineering risk             |
| **Public changelog / release notes** | Per-product, per-release: what shipped, what fixed, breaking changes, deprecations               | Internal version numbers; rolled-back changes; root-cause detail for fixed bugs          |

**Why this matters for KB scope.** Each of these surfaces _absorbs_ content that would otherwise crowd into the KB. Compliance answers belong on Trust Center (not in admin docs). Outage notices belong on Status (not as KB updates). API specifics belong on API reference (not in user docs). The KB is what's left when each adjacent surface owns its own scope.

For SpecterX, the practical move is to publish even minimal versions of each adjacent surface (a one-page Trust Center, a security.txt + Security Disclosure article, a Status page, a public Changelog index) so the KB doesn't get asked to do their jobs.

---

## 9. Coordinated security disclosure — when security info becomes public

For a security product, the most consequential exposure decision is _when_ vulnerability information becomes public. The industry standard is **Coordinated Vulnerability Disclosure (CVD)** — used by every PSIRT-running vendor we examined ([Palo Alto Networks](https://www.paloaltonetworks.com/security-disclosure), [Qualys](https://cdn2.qualys.com/docs/responsible-disclosure-policy.pdf), [Zscaler](https://www.zscaler.com/security/vulnerability-disclosure-program)).

Convergent CVD principles relevant to public KB scope:

1. **Sensitive non-public vulnerability information is "highly confidential"** and is restricted to the PSIRT and engineering staff with a legitimate need to know. It does not appear in any KB article, blog post, or support reply until an advisory ships.
2. **Reporters are asked not to disclose publicly** until the vendor has fixed the issue and published an advisory. The vendor commits to a reasonable timeline (Palo Alto Networks: investigation, fix, advisory — all coordinated).
3. **Advisories omit information that would help miscreants exploit** the issue. They state: affected products and versions, severity, fix version, mitigation steps. They do _not_ state: exploit code, the precise vulnerable code path, or step-by-step reproduction (these stay in the internal record).
4. **A dedicated reporting channel** (typically `psirt@<vendor>` with a PGP key, plus a public report form) is published prominently — usually at `/.well-known/security.txt` and from a Security page linked off the help-center footer.
5. **Out-of-scope items are listed publicly** so researchers don't waste time and the vendor doesn't get noise: typically DoS testing, social engineering, third-party services, end-of-life browsers.
6. **A bug-bounty programme (optional)** sits alongside the disclosure policy and has its own published scope.

**What goes in the public KB vs the Security Advisory page:**

| Information                                                                        | Public KB | Security Advisory page                |
| ---------------------------------------------------------------------------------- | --------- | ------------------------------------- |
| The user-facing security control (what watermarking does, how verification works)  | Yes       | No                                    |
| The boundary of the control ("Watermarking does not prevent re-photographing")      | Yes       | No                                    |
| The disclosure policy itself ("How to report a vulnerability")                     | Linked    | Yes (canonical)                       |
| Past vulnerabilities with CVEs (affected versions, severity, fixed version)        | No        | Yes                                   |
| Mitigation steps for past CVEs                                                     | Linked    | Yes                                   |
| Exploit details, bypass techniques, PoC code                                       | No        | No (kept internal even after fix)     |
| In-flight investigations of reported vulnerabilities                               | No        | No                                    |
| The contact channel and PGP key                                                    | Footer    | Yes                                   |

**For SpecterX specifically**, this means publishing — even as a one-pager today — a Security Disclosure article that contains: the coordinated-disclosure policy, the reporting channel (email + PGP key + form), out-of-scope items, and a placeholder for the CVE archive. Link it from the KB footer. Do not let the lack of an Advisory archive be a reason to defer the policy publication.

---

## 10. Public KB vs internal knowledge base — the boundary

A point that runs through every 2026 industry write-up ([HappySupport](https://happysupport.ai/blog/how-to-build-help-center), [Pylon](https://www.usepylon.com/blog/effective-customer-knowledge-base-2026), [eesel](https://www.eesel.ai/blog/how-to-build-knowledge-base)) and that the five-platform crawl could not surface: **the public help center is a strict subset of the broader knowledge base**. The internal half stays private.

| Content class                                          | Public KB | Internal KB (Confluence / Notion) |
| ------------------------------------------------------ | --------- | --------------------------------- |
| Customer-facing how-to, troubleshooting, reference     | Yes       | Mirror for support agents         |
| Internal SOPs (escalation paths, on-call runbooks)     | No        | Yes                               |
| Sales playbooks, battle cards, competitive analysis    | No        | Yes                               |
| Support agent training, canned responses, macros       | No        | Yes                               |
| Internal product specs, design docs, ADRs              | No        | Yes                               |
| Roadmap details, customer commitments, deal-stage notes | No        | Yes (CRM-gated)                  |
| Incident post-mortems with internal detail             | No        | Yes (public RCA on Status page)   |
| Internal architecture diagrams, deployment topology    | No        | Yes                               |
| Customer-specific configurations and contracts         | No        | Yes (CRM-gated)                   |
| Employee onboarding materials                          | No        | Yes                               |

A useful sanity test for any draft article: **would this still make sense to read if you had never worked at SpecterX?** If no, it belongs in the internal wiki, not the public KB. The same task may need both versions — a customer-facing "How to revoke access" article and an internal "Revocation troubleshooting playbook" — but they are two different documents with two different audiences.

The reverse test catches a different mistake: **would a competitor learn something operationally useful by reading this?** If yes (e.g., the article enumerates the exact email templates we send, the exact thresholds at which we throttle, the exact internal field names we use), strip it down or move it to internal.

---

## 11. Cross-references — sources cited

### Per-platform analyses (the primary evidence base)

- [`sources/hubspot/README.md`](../reference-library/sources/hubspot/README.md) — connector lifecycle (§0), permissions inline (§7), "Before you get started" universal H2 (§2), assumed knowledge (§6)
- [`sources/egnyte/README.md`](../reference-library/sources/egnyte/README.md) — audience splits, prerequisites, known limitations, supported configurations (§§3, 6)
- [`sources/docsend/README.md`](../reference-library/sources/docsend/README.md) — one feature / one page, plan-gate banner, Visitor experience H2, "Things to consider" (§§2, 3, 6)
- [`sources/vera/README.md`](../reference-library/sources/vera/README.md) — User/Admin/Configuration guide split, dedicated Constraints section, release notes, formal admin register (§§1, 6)
- [`sources/virtru/README.md`](../reference-library/sources/virtru/README.md) — Recipient as a top-level audience, disambiguation FAQ, Advanced Products skeleton, per-framework compliance pages (§§1, 6)
- [`compare.html`](../reference-library/site/compare.html) — side-by-side comparison of voice, page anatomy, screenshot density, cross-reference patterns, page-scope rules

### External frameworks and 2026 industry write-ups (synthesised in §§7–10)

- [Diátaxis — the four documentation modes](https://diataxis.fr/start-here/) — the canonical taxonomy distinguishing tutorials / how-to / reference / explanation by user need.
- [How to Build a SaaS Knowledge Base (HappySupport, 2026)](https://happysupport.ai/blog/how-to-build-saas-knowledge-base) — the 5 article-type templates (how-to, troubleshooting, FAQ, feature overview, release notes) and the 4–6 top-level category rule.
- [How to build a knowledge base (eesel AI, 2026)](https://www.eesel.ai/blog/how-to-build-knowledge-base) — public vs internal KB boundary, depth/breadth caps, in-product surfacing.
- [Help center best practices: 2026 playbook (Helpview)](https://helpview.so/blog/help-center-best-practices-2026-deflect-tickets) — ticket-data-driven scope, verb-first titles, fix-first article structure.
- [Customer Knowledge Base 2026 guide (Pylon)](https://www.usepylon.com/blog/effective-customer-knowledge-base-2026) — public/internal split, template-per-type.
- [How to Write Knowledge Base Articles That Stay Current (HappySupport)](https://happysupport.ai/blog/how-to-write-knowledge-base-articles) — one task per article, function-first language, four core types.
- [We Audited 30 SaaS Help Centers (HappySupport)](https://happysupport.ai/blog/audited-30-saas-help-centers) — drift as the root cause of help-center quality decay; review-triggered updates.
- [Palo Alto Networks — Product Security Assurance and Vulnerability Disclosure Policy](https://www.paloaltonetworks.com/security-disclosure) — coordinated vulnerability disclosure as the industry standard for security-product vendors; advisories omit miscreant-useful detail.
- [Qualys — Responsible Disclosure Policy](https://cdn2.qualys.com/docs/responsible-disclosure-policy.pdf) — reporter conduct, vendor commitments, examples of in-scope vulnerability classes.
- [Zscaler — Vulnerability Disclosure Program](https://www.zscaler.com/security/vulnerability-disclosure-program) — out-of-scope enumeration, confidentiality requirements, reporting channel pattern.
