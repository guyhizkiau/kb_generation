# SpecterX Component Taxonomy

A canonical naming and categorization scheme for every SpecterX product component — what each component is called, what umbrella category it belongs to, and what each category word means.

Source: distilled from *My statement on workflows — May 2026*. This document is the organized, navigable form of that statement.

---

## 1. Why this exists

SpecterX has accumulated a long list of components — storage integrations, identity integrations, mail add-ins, browser extensions, share connectors, viewers, gateway pieces, policy toggles. Without a shared vocabulary it's hard to keep Jira components, marketing pages, support articles, and engineering tickets aligned.

This taxonomy fixes that by:

- Giving every component a single canonical name.
- Grouping components under a small set of umbrella categories.
- Defining each category with a one-line "decision test" so new components have an obvious home.

> **Naming convention.** Every component is written `<Umbrella> / <Component Name>` — for example `Storage Integration / Amazon S3 Storage` or `Mailflow Integration / Outlook Classic Add-in`. The umbrella is what the *whole product category* is; the component name is the specific deliverable.

---

## 2. Component inventory

Components grouped by their umbrella category. This is the source-of-truth list for Jira components, KB structure, and component records.

### Storage Integration

- Amazon S3 Storage
- SharePoint Storage
- Google Cloud Storage

### Identity Integration

- Okta Identity
- Entra ID
- Google Cloud Identity

### DLP Integration

- DLP Web Client
- DLP Mailflow

### CDR Integration

- Opswat CDR

### Classification Integration

- Microsoft Purview

### Mailflow Integration

- Outlook Classic Add-in
- Outlook New Add-in
- Gmail Browser Extension
- Mail Protection Server

### Share-in-Place Connector

- Google Drive Connector
- SharePoint Connector

### Messaging Connector

- Slack Connector

### Salesforce Report Export

- Salesforce Browser Extension
- Salesforce Reports Connector

### SpecterX Viewer

- SpecterX Office Viewer
- SpecterX PDF Viewer
- SpecterX WOPI Host

### External Open-With

- Open with Adobe Desktop
- Open with Microsoft Edge
- Open with Native Office
- Open with Google Drive

### On-Prem Gateway

- SpecterX Gateway (On-Prem)
- SpecterX Gateway Storage Connector (On-Prem)
- Active Directory

---

## 3. Category definitions

Each section below defines one umbrella word: what it means, the test that decides whether something belongs in it, examples, and edge cases.

### Integration

A background relationship between SpecterX and an external system for exchanging data, identity signals, or policy/classification metadata. The end user typically doesn't choose to use it or even know it's there — it's plumbing configured by an admin and operates automatically once enabled.

- **Decision test.** If you removed it, would a normal user notice immediately, or would things just silently get worse (no SSO, no DLP scanning, no classification labels)? *Silent degradation → Integration.*
- **Examples.** Storage Integration, Identity Integration, DLP Integration, CDR Integration, Classification Integration, Mailflow Integration.
- **Edge case — Mailflow Integration.** This one is on the line. Users *do* see its effects (sharing flow inside Outlook), but the integration itself is admin-configured plumbing that intercepts mail. The Add-ins under it are the user-facing pieces; the Mail Protection Server is pure plumbing. The umbrella stays "Integration" because that's what the whole product category is, even though some sub-components are user-facing.

### Connector

A user-facing surface that lets the user actively do something through SpecterX into a specific third-party app. The user chooses to invoke it, knows which app they're targeting, and the third-party app's name shows up in the UI.

- **Decision test.** Does the end user click a button that mentions the third-party app by name (Slack, Google Drive, Salesforce)? *Yes → Connector.*
- **Examples.** Share-in-Place Connectors (Google Drive, SharePoint), Messaging Connectors (Slack), Salesforce Reports Connector.
- **vs. Integration.** Integration is "SpecterX silently talks to Okta in the background." Connector is "user clicks 'Share to Slack' and SpecterX hands it off."

### Share-in-Place Connector

A specific kind of Connector where the user shares a file that *stays in its original storage location* — SpecterX adds protection and access control without moving or copying the file out. Google Drive and SharePoint Share-in-Place Connectors let users share existing Drive/SharePoint files under SpecterX policy, rather than uploading a fresh copy to SpecterX storage.

- **Decision test.** Does the file remain where it was, or does it move into SpecterX's custody? *Stays in place → Share-in-Place Connector.*
- **Why it earns its own sub-type.** The security model and the integration mechanics are genuinely different from "user uploads a file to SpecterX and shares it." Customers also recognize "share in place" as a distinct product capability — it's not just an implementation detail.

### Messaging Connector

A Connector where the destination is a chat/messaging platform (Slack, Teams, eventually maybe Discord/WhatsApp/etc). Worth its own sub-type because messaging targets have different UX patterns than file storage — ephemeral channels, DMs, bot installation, etc.

- **When to keep this category.** If you only ever have Slack and Teams here, this could collapse back into "Connector" without loss. The category earns its keep if you see yourselves adding more messaging targets.

### Extension / Add-in / Plugin

These three words mean essentially the same thing technically — code that runs inside a third-party host application — but each ecosystem has settled on its own term, and using the host's term matters because that's what customers, marketplaces, and support tickets will use.

| Term | Ecosystem | When to use it |
| --- | --- | --- |
| **Add-in** | Microsoft Office | Anything that runs inside a Microsoft Office host (Outlook Add-in, Word Add-in, Excel Add-in). |
| **Extension** | Browser | Anything that injects into a web page or browser chrome (Salesforce Browser Extension, Gmail Browser Extension — even though Gmail is "in" Google's product, your client runs in the browser). |
| **Plugin** | Catch-all | When the host product itself calls them plugins (Box plugin) or when neither Add-in nor Extension fits the host's own terminology. |
| **App** | Marketplace | What most marketplaces call third-party software (Slack App, Teams App, Salesforce AppExchange). Worth considering if you build a true installable Slack/Teams app rather than just a connector that talks to their APIs. |

> **Important.** These are *sub-component* names, not umbrellas. An Outlook Add-in is one piece of Mailflow Integration. A Salesforce Browser Extension is one piece of Salesforce Report Export. The Extension/Add-in word answers *"what kind of client is it?"*, not *"what does it do?"*

### Engine

The renderer/processor underneath a SpecterX product surface, where the surface is what the customer sees and the engine is implementation. Used for Viewer sub-components today (SpecterX Office Engine, SpecterX PDF Engine).

- **Decision test.** Could you swap this out for a different vendor's technology without the customer noticing? *Yes → Engine.*
- **What the word signals.** "Implementation detail, not a customer-facing product." Useful where you want to track work against a specific underlying technology (PSPDF, Office Online, etc.) without elevating that technology to product status.

### Open-With Target (External Open-With)

A third-party app the user chooses to open a SpecterX-protected file in, where the file leaves SpecterX's rendering context. Adobe Desktop, Native Office, Microsoft Edge as a PDF reader, Google Drive as a viewer.

- **Decision test.** Does the user pick this from an "Open with…" menu, and does the file get handed off to an app outside SpecterX's direct control? *Yes → External Open-With.*
- **vs. Viewer.** Viewer is "SpecterX renders the file in-house (possibly via an embedded engine)." External Open-With is "SpecterX hands the file to someone else's app and trusts the protection mechanism to follow it." Very different security models.

### Service

The backend SpecterX operates to power any of the above. Internal-facing word — customers rarely see it. Used when you need to talk about the server side of something as a distinct component (Salesforce Reports Connector backend, Mail Protection Server).

- **When to split off a Service component.** Don't break every product into Client + Service components by default. Only do it when the two pieces have genuinely separate deployment / release / ownership cycles. Most integrations don't need this — the backend lives in the same component as the rest of the integration unless there's a reason to split it.

### Policy Protection

A file-level security measure that admins enable through the policy management UI, applied automatically to files governed by that policy. In the policy editor: anything that appears as a toggle in the **Data Protection** or **Access Control** sections.

- **Decision test.** Is this configurable per-policy in the policy management UI? *Yes → Policy Protection.*
- **Examples.** Watermarking Policy Protection, Password Policy Protection, Rights Management Policy Protection. (Possible future Policy Protections if/when they become Jira components: Download Blocking, Recipient Verification, Time-Limited Access, …)
- **Not Policy Protection.** Features that aren't policy-controlled. Digital Signature is a standalone capability — users sign documents, it's not a toggle an admin turns on for a policy. So it sits in Jira without the suffix.

### Gateway

A self-contained SpecterX deployment that runs in a customer's environment, rather than in SpecterX's cloud. **On-Prem Gateway** is the umbrella; sub-components are the pieces of it (core service, storage connector for on-prem).

- **Why it earns its own type word.** The deployment model is fundamentally different — release cadence, support model, version skew, all distinct from cloud.

---

## 4. Quick decision flow

When a new component shows up and you're unsure which category it belongs to, walk these tests in order:

1. **Is it on-prem deployed in the customer's environment?** → **Gateway** (it's part of On-Prem Gateway).
2. **Is it a per-policy toggle in the policy editor?** → **Policy Protection**.
3. **Does the user click a button that names a third-party app (Slack, Drive, Salesforce)?**
   - File stays put in third-party storage → **Share-in-Place Connector**
   - Destination is a chat/messaging platform → **Messaging Connector**
   - Otherwise → **Connector**
4. **Does the user pick it from an "Open with…" menu and hand the file to an outside app?** → **External Open-With**.
5. **Does it run inside a third-party host application as injected code?** → name it by host ecosystem: **Add-in** (MS Office), **Extension** (browser), **Plugin** (catch-all), **App** (marketplace).
6. **Is it the renderer/processor underneath a SpecterX surface, swappable without the customer noticing?** → **Engine**.
7. **Is it a backend you only need to call out because it has its own release/ownership cycle?** → **Service**.
8. **Is it admin-configured plumbing whose absence would cause silent degradation rather than a visible UX change?** → **Integration**.

If two tests fire, prefer the more specific one (Share-in-Place over Connector, Messaging over Connector, Gateway over Service, etc.).

---

## 5. Open questions and future evolution

Things the source statement explicitly flagged as worth revisiting:

- **Messaging Connector may collapse.** If SpecterX never ships beyond Slack/Teams, this category can fold back into plain Connector.
- **"App" as a real category.** Worth elevating if SpecterX ever ships a true installable Slack/Teams marketplace app instead of an API-driven connector.
- **More Policy Protections.** Download Blocking, Recipient Verification, Time-Limited Access, etc. — only get the `- Policy Protection` suffix once they exist as Jira components.
- **Service splits.** Most integrations should not have separate Client + Service components. Re-evaluate per integration only when ownership/release cycles diverge.
- **Naming Viewer vs. Engine.** The current inventory uses *Viewer* as both umbrella (`SpecterX Viewer`) and surface name (`SpecterX Office Viewer`). The Engine definition alludes to `SpecterX Office Engine` / `SpecterX PDF Engine` as the under-the-hood implementations. Confirm whether engines are tracked as Jira components or only mentioned in docs.

---

## 6. How to use this document

- **Adding a new component.** Walk the decision flow in §4, then add it to the inventory in §2 under the matching umbrella, written as `<Umbrella> / <Component Name>`.
- **Renaming an existing component.** Update the inventory entry first, then propagate to: Jira components, KB article titles, the component records under `Active Platform Component Records/`, and `all-compontents.txt`.
- **Coining a new category word.** Don't, unless an existing umbrella genuinely doesn't fit. If you do, add a §3 definition with a one-line decision test, examples, and a "vs. nearest neighbor" note — same shape as the existing definitions.

---

*Last reviewed against source: May 2026.*
