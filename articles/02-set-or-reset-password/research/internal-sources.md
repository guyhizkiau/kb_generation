# Internal sources — Set or reset your password

## What was searched

- `references/internal/` — empty.
- `product/components-inventory.txt` — checked for "Reset Password",
  "Authentication", "Password".
- `product/COMPONENT_TAXONOMY.md` — checked for password / identity /
  authentication entries.
- `component-records/` recursively — searched for password / reset /
  invite / activation content.
- `editorial/ARTICLES_PLAN.md` (lines 44–55) — the plan entry for this
  article.
- `editorial/PUBLIC_KB_SCOPE.md` — searched for password-related scope.

## What was found

### Reset Password is a real first-class component

`product/components-inventory.txt` line 75 lists **Reset Password** as
a standalone SpecterX component, alongside **Authentication**. Both
are inventory entries; neither has a `component-records/` folder of
its own. For an end-user procedural article this is not a blocker, but
it's a documentation gap worth flagging: there is no PRD or product
record for either Authentication or Reset Password under
`component-records/`.

> **Note:** the `component-records/policy-controls/password-protection/`
> folder is **not** about user-account passwords. It's the
> **Password — Policy Protection** entry from the inventory (line 61):
> an admin-configurable file-level password applied to downloaded
> copies. Out of scope for this article.

### Identity providers: three are first-class for SSO

`product/COMPONENT_TAXONOMY.md` §2 defines an **Identity Integration**
umbrella with three named sub-components: **Okta Identity**, **Entra
ID**, **Google Cloud Identity**. The taxonomy classifies these as
Integration (silent, admin-configured plumbing). When a user belongs
to an SSO-enabled organization, the password is managed by the
identity provider, not by SpecterX. The article's "If you use SSO"
section is consistent with this taxonomy.

### Admin-driven user provisioning

`component-records/admin-platform/user-and-groups/User Roles &
Functions_.xlsx` and the surrounding folder confirm that user
provisioning is admin-driven from the admin portal. Self-service
sign-up is not enabled in production — confirmed by the codebase
error string `signUpForbidden`: "You must be invited before you can
sign in" (`web-client/src/content/general.json:141,456`). First-time
password creation therefore happens after an admin invitation, not
through a public sign-up form.

### Off-boarding (deprovisioning) is a separate flow

`component-records/admin-platform/project-off-boarding-tier-1-support/
SpecterX - Handing Off 3rd Party Support Planning_.docx` covers
deprovisioning. If self-service password reset stops working for a
user, one likely cause is that their account has been disabled. This
article points users at their administrator rather than diagnosing it
in-line — consistent with the off-boarding model.

### Plan entry calls out seven sub-topics

`editorial/ARTICLES_PLAN.md` lines 44–55 lists what the article must
cover:

- First-time password creation (activation flow for non-SSO users)
- Triggering a reset from the login page
- What the reset email looks like and where it comes from
- Link / code expiry
- SSO users: password is managed by the IdP, not SpecterX
- Not receiving the email (spam, provisioning)
- Contacting the administrator if self-service is disabled

All seven items map to sections of the final draft.

## Conclusions

- The article's procedural shape (login page → "Reset password" link →
  email with code → enter code + new password) matches the codebase
  exactly. See `research/codebase-findings.md` for exact UI strings.
- The article's SSO carve-out is consistent with `COMPONENT_TAXONOMY.md`.
- The article's "contact your administrator" guidance is consistent
  with the admin-driven provisioning model and the off-boarding PRD.
- Gap flagged for future work: there is no PRD folder for the
  **Authentication** or **Reset Password** components. Worth raising
  with whoever owns these components.
