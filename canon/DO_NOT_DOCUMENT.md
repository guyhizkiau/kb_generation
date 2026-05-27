# Do not document

Articles that look documentable but should not be written yet. Before
drafting any article, grep this file for the candidate article title or
its subject matter. If matched, skip the article and log it in the
cluster's STATE as `skipped: do-not-document`.

## Deferred features (from `editorial/ARTICLES_PLAN.md`, "Deferred until shipped")

- **Configure email body encryption via a Platform Governance Rule** — V2 PAR capability; not shipped in V1.
- **Lock a policy so users cannot override it** — superseded by PAR policy-locking; the standalone "Lock Policies" feature was not shipped.
- **Extend governance rules to Workspaces and Slack** — PAR enforcement across Workspaces / Slack / Salesforce not shipped in V1.
- **Transport-rules-based MPS setup** — superseded by current Mail Protection architecture; covered by existing MPS articles when updated.
- **Policy Assignment Rules (original PRD)** — superseded by V1 PAR PRD; content absorbed into V1 articles.
- **Tour the redesigned SpecterX Recipient Page** — Recipient Link Experience 3.0 redesign not yet shipped.
- **Edit a protected file directly in SpecterX** — in-platform file editing in planning; not shipped.
- **Request files without creating a workspace** — standalone Request Files action still tied to Workspace creation in V1.
- **Manage folder-level permissions (new model)** — proposed folder permission standardization not yet shipped.
- **Redesigned upload flow** — planning stage; existing share-a-file article to be enhanced when shipped.
- **Manage file lifecycle and automatic expiry policies** — Lifecycle Management Epic planned for Q2 2026.
- **Platform UX overhaul** — broader UX redesign in planning; existing articles will need updating when shipped.
- **Progressive file lifecycle management** — roadmap planning; updates to existing lifecycle articles when shipped.
- **Access multiple SpecterX tenants with single sign-on** — multi-tenant SSO not yet shipped.
- **Sync groups from your identity provider to SpecterX** — IDP-synced group management not shipped in V1.
- **Send SpecterX notifications from your organisation's email domain** — customer-domain notifications not yet shipped.
- **Workspaces 2.0 redesign** — planned redesign with additional capabilities; not yet shipped.
- **Share a SharePoint folder with SpecterX protection** — SharePoint Connector folder-sharing / inbound capabilities not in V1.
- **Send a protected file in a Slack Direct Message** — Slack Connector PAR integration, filename display, DM support not in V1.
- **Audit Logs future versions** — current share-flow events doc is V1; future audit-log capabilities deferred.
- **Track recipient activity directly from Outlook** — in-Outlook activity tracking from the add-in side panel not shipped.
- **Test a Platform Governance Rule before activating it** — PAR test mode not shipped in V1.
- **Configure sender, recipient, and admin notifications** — notification configuration UI does not exist in V1.
- **Request files from recipients without creating a workspace** — standalone Request Files action not yet shipped.

## Internal-only flows discovered during research

*(empty; add as you discover things in the codebase that shouldn't be public)*
