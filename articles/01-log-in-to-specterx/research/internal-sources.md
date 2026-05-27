# Internal sources — Log in to the SpecterX web platform

## What was searched

- `product/COMPONENT_TAXONOMY.md` — the canonical component taxonomy.
- `product/components-inventory.txt` — the flat inventory list.
- `component-records/` recursively, with `find` for `*auth*`, `*login*`,
  `*sign*`, `*sso*`, `*saml*`, `*password*`, and a grep across files
  for the same keywords.
- `references/internal/` — confirmed empty.

## What was found

### Authentication exists as a SpecterX component, but has no record folder yet

`product/components-inventory.txt` lists **Authentication** as a top-level
component (alongside Reset Password, Mail Protection Service, etc.). There
is no corresponding folder under `component-records/`, i.e. no PRD, no
spec, no internal docs explicitly named "Authentication." For this
article — a basic end-user sign-in walkthrough — the absence isn't a
blocker, but it is a documentation gap worth flagging for whoever owns
the Authentication component.

### Identity providers: three are first-class

`product/COMPONENT_TAXONOMY.md` defines an **Identity Integration**
umbrella category with three named sub-components:

- Okta Identity (`Okta Identity Integration`)
- Entra ID (`Entra ID Integration`)
- Google Cloud Identity

These are classified as Integration, meaning silent admin-configured
plumbing. The decision test in the taxonomy: "If you removed it, would
a normal user notice immediately, or would things just silently get
worse (no SSO, no DLP scanning, …)?"

**Implication for the article.** The final article already names
"Microsoft Entra ID or Okta" as example identity providers and offers
a **Sign in with Google** button as the canonical SSO example. The
taxonomy confirms these three are the supported IDPs today; the article
is accurate. We do not need to claim or imply support for any other
IDP. If the customer's IT team has integrated a SAML provider that is
not Okta/Entra/Google Cloud Identity, the support path is "contact
your administrator" — which the article already covers.

### Multi-tenant admin auth is a separate concern, not in scope

`component-records/admin-platform/project-sso-multi-tenant-access/
PRD_ Multi-Tenant Access Across Portals_.docx` (last updated
2026-02-21) covers MSP/multi-tenant authentication for the **admin
portal**, not the end-user web platform. Key facts: the admin portal
currently restricts to a single Entra instance per admin portal
domain; the broader multi-tenant auth platform is still PRD-stage,
not shipped. None of this affects the end-user sign-in flow this
article documents.

### IDP sync is a future feature, not relevant yet

`component-records/admin-platform/user-and-groups/
project-group-management-through-idp-sync/` contains future-version
PRDs for syncing user/group membership from the customer's IDP. This
is admin-facing and not yet shipped. No impact on the article.

### Reset Password is a real adjacent component

`product/components-inventory.txt` lists **Reset Password** as a
standalone component. The article already links to "Set or reset
your password" under Related articles — consistent with the inventory.

## Conclusions

- The article's claims about supported identity providers are
  consistent with the official taxonomy.
- No internal source disagrees with the article's current copy.
- One gap surfaced for future work (not this article): the
  **Authentication** component has no record folder. Worth raising
  with whoever owns it before article 02 (password reset) or any
  future SSO-specific article is written.
