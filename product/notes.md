# Product notes — SpecterX

A running notebook of facts learned about SpecterX while writing articles. Append per-article sections as new things come up. Use this when an article needs context the public KB doesn't capture but that you've worked out from internal sources (taxonomy, component records, reviewer feedback).

For canonical component names and category definitions, see [COMPONENT_TAXONOMY.md](COMPONENT_TAXONOMY.md). This file is for narrative facts about how the product works, not the inventory itself.

---

## From article 03 — What is SpecterX (2026-06-03)

### Positioning

- SpecterX is a **data governance and secure collaboration platform**. Two-line pitch: protection travels with the file across applications, devices, and storage; the sender keeps revoke / expire / audit control after the file leaves their environment.
- The product replaces the raw attachment / public link pattern with a **protected link** that is governed by a named policy.

### Sender and recipient model

- A **sender** is a licensed SpecterX user at the customer organisation. A **recipient** is anyone the sender shares with — recipients do not need a SpecterX account and are provisioned implicitly at share time.
- Recipients verify themselves **per share**, not per session. Default verification is a 6-digit email code; SMS code or a sender-supplied personal secret (out of band) are policy-configurable alternatives.
- Inside a Workspace the sender/recipient relationship becomes a **named role**: Owner, Co-Owner, Contributor, Viewer. The role persists for the lifetime of the Workspace.

### Security policy — what it controls

A security policy is an admin-defined bundle. The dimensions the sender effectively controls at share time (by picking a policy from a dropdown):

- Recipient verification (email code / SMS / shared secret)
- Forwarding restrictions
- Download blocking
- Watermarking
- Encryption with a password
- Encryption via Microsoft Rights Management
- Link expiry (days)

Watermarking, Password, and Rights Management each appear in the inventory as `- Policy Protection` toggles (see [COMPONENT_TAXONOMY.md §3 Policy Protection](COMPONENT_TAXONOMY.md)). Download Blocking, Recipient Verification, and Time-Limited Access are described as toggles but are not yet tracked as standalone Policy Protection components.

### Where SpecterX adds protection (the "What SpecterX protects" surface)

This is the bullet list customers see in the intro article. Maps to component categories:

| Surface in the article | Component category |
| --- | --- |
| Files shared from the web | SpecterX web platform (user-facing core) |
| Email and attachments | Mailflow Integration — Outlook Classic / New Add-in, Gmail Browser Extension, Mail Protection Server |
| Workspaces | User-facing core (Workspaces component) |
| Files in Google Drive and SharePoint | Share-in-Place Connector |
| Messages and files in Slack | Messaging Connector |
| Data exported from Salesforce | Salesforce Report Export (Browser Extension + Reports Connector) |

> **Lesson from PR#5 review (2026-06-03).** The first draft of this article only mentioned Google Drive and SharePoint under share-in-place, and skipped the messaging and Salesforce connectors entirely. Reviewer flagged this and pointed at COMPONENT_TAXONOMY as the source of truth. **Future articles that enumerate "what SpecterX covers" must check the full Connector list in §2 of COMPONENT_TAXONOMY**, not just the share-in-place ones.

### Mail protection has two distinct surfaces

- **Client-side**: Outlook Add-ins (Classic + New) and the Gmail Browser Extension add a SpecterX panel to the user's compose window. Policy + per-recipient permissions are picked manually before sending.
- **Server-side**: the **Mail Protection Server** applies policies automatically as messages leave the org. Can be driven by DLP signals (DLP Mailflow Integration) or Purview classification labels — i.e., policy assignment becomes automatic based on content classification.

### Storage backing for Workspaces

- SpecterX always uses the customer organization's own storage. The admin configures which one tenant-wide: Amazon S3, SharePoint, or Google Cloud Storage.
- There is no "SpecterX-managed storage" default that competes with customer storage. Don't write copy that suggests SpecterX has its own storage tier that customers opt out of.
- Don't claim SpecterX adds additional encryption inside the customer's storage, and don't claim it doesn't. Side-step the question in customer-facing copy (see [COMPONENT_TAXONOMY.md §3 Storage Integration](COMPONENT_TAXONOMY.md)).
- Storage Integrations are admin plumbing (see [COMPONENT_TAXONOMY.md §3 Integration](COMPONENT_TAXONOMY.md)); users do not pick storage at share time.

### Identity integration

- Supported IdPs: Microsoft Entra ID, Google Cloud Identity, Okta.
- Supported protocols: SAML 2.0, OAuth, LDAP.
- Identity Integration only affects the **sender** side. Recipients verify per share and bypass the IdP entirely.

### Classification and DLP plumbing

- **DLP Integration** has two flavours: DLP Web Client (UI / share-time scans) and DLP Mailflow (gateway-side scans). Either can trigger on recipient access.
- **Classification Integration** is currently Microsoft Purview only — Purview sensitivity labels can drive automatic policy assignment.
- Third-party DLP headers and custom Exchange Online headers can also feed policy assignment on the mail path.

### Deployment models

- Default: SpecterX cloud (multi-tenant).
- **On-Prem Gateway**: customer-environment deployment. Its own release cadence and support model — distinct enough from cloud that COMPONENT_TAXONOMY gives it a top-level umbrella ("Gateway").
- On-Prem Gateway sub-components: SpecterX Gateway, SpecterX Gateway Storage Connector, Active Directory binding.

### Recipient-side rendering

- Files render in the **Secure Viewer** by default — in-browser, no install.
- For richer editing or formats the Viewer doesn't cover, the recipient picks from an **External Open-With** menu: Adobe Desktop, Microsoft Edge (PDF), Native Office, Google Drive.
- External Open-With is distinct from Viewer because the file leaves SpecterX's direct rendering control — different security model (taxonomy §3 External Open-With).

### What SpecterX is explicitly *not*

- Not a storage product (storage is pluggable; SpecterX adds governance on top).
- Not a defence against a determined insider with screen/camera access — watermarks deter, they do not block.

### Audit and post-share control

Every protected interaction emits an audit trail. From the same interface that sent the file the sender can: revoke, change recipient permissions, or expire the link instantly. This is the "control after the file leaves" promise that distinguishes SpecterX from raw attachments + ACLs.

---

*Append a new `## From article NN — title (date)` section per article going forward. Don't duplicate facts that already live in COMPONENT_TAXONOMY or components-inventory — link there instead.*
