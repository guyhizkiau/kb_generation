# Competitor coverage checklist — Set or reset your password

## Cache status

Three vendor articles captured for this topic. Virtru does not publish
a public end-user "reset your Virtru password" article (the closest
hits — 360051427613, 13716708311447, 115012864108 — all 404 as of
2026-05-27). Skipping Virtru.

| Vendor | Source | Captured |
| --- | --- | --- |
| Egnyte | [Forgot Password](https://helpdesk.egnyte.com/hc/en-us/articles/201637054-Forgot-Password) | 2026-05-27 |
| Dropbox | [How to change or reset your Dropbox password](https://help.dropbox.com/security/password-reset) | 2026-05-27 |
| HubSpot | [Reset user passwords](https://knowledge.hubspot.com/account-security/reset-user-passwords) | 2026-05-27 |

Per-vendor source files live under `references/competitors/<vendor>/reset-password.md`
and are indexed in `references/competitors/INDEX.json`.

**Structural finding across the three vendors.** All three publish a
short procedural article focused on the forgot-password flow from the
login page. Two of the three (Egnyte, HubSpot) also include an
explicit SSO carve-out: if your organization uses an identity
provider, the article doesn't apply — see your admin. Dropbox covers
the team-admin-driven reset path. None of the three describes the
first-time activation flow as a distinct topic, even though all three
products send activation emails. SpecterX choosing to cover both
first-time setup and reset in one article (because they share the same
UI) is a deliberate departure from the SaaS norm. It mirrors how the
codebase actually works (one component for both flows).

## Per-vendor coverage checklists

### Egnyte — Forgot Password

- [x] Step-by-step from the login page — covered (open WebUI, enter
      email, select Forgot password?, click Continue).
- [x] Email expectation — covered ("Once you receive the email, click
      the Change Password button").
- [x] Link expiry — covered ("can only be pressed once and will only
      be active for two hours").
- [x] SSO carve-out — covered as a Note: if the email says your
      account is configured for Active Directory or SSO, contact your
      administrator.
- [ ] Password rules — not covered.
- [ ] Not receiving the email / spam guidance — not covered.
- [ ] Lockout after repeated attempts — not covered.
- [ ] Verification code format (length, expiry) — not covered.
      Egnyte uses a link, not a code; this is a flow difference.
- [ ] First-time / activation flow — not covered as a distinct topic.

### Dropbox — How to change or reset your Dropbox password

- [x] Step-by-step from the login page — covered.
- [x] Step-by-step from inside the app (logged in) — covered.
- [x] Mobile guidance — covered ("you can't reset or change in the
      mobile app; use the browser").
- [x] Email-account loss carve-outs — covered (links to "sign in
      without access to your email").
- [x] Team-admin carve-out — covered (Standard / Advanced teams may
      need an admin to reset).
- [x] Not receiving the email — covered (check spam; add
      no-reply@dropbox.com to contacts).
- [x] Expired password — covered as a linked sub-flow.
- [ ] Password rules — not covered (link out to "strong password" tip).
- [ ] Verification code — Dropbox uses a link, not a code; this is a
      flow difference.
- [ ] First-time / activation flow — not covered.
- [ ] Lockout / attempt limit — not covered.

### HubSpot — Reset user passwords

- [x] Forgot password from login — covered (Navigate, click Forgot
      password, email arrives, link expires in 24 hours).
- [x] In-app change while logged in — covered (Profile & Preferences
      → Security → Reset password).
- [x] Admin-driven reset for another user — covered (Settings → Users
      & Teams → Actions → Reset password). **Note:** this is the
      admin-portal flow; SpecterX's equivalent lives in a different
      article (admin guide) — out of scope here.
- [x] Lockout after failed attempts — covered (10 consecutive fails →
      automatic reset email).
- [x] Leaked-password check — covered (publicly leaked passwords are
      blocked).
- [x] Not receiving the email — covered (check spam, add hubspot.com
      to allowlist, work with Super Admin if bounced).
- [x] Password rules — implicit via the leaked-password check; not a
      complexity rule list.
- [ ] Verification code format — HubSpot uses a link, not a code.
- [ ] First-time / activation flow — not covered.

## Overall coverage gaps vs our `editorial/ARTICLES_PLAN.md` entry

The plan entry calls out seven sub-topics (lines 49–55). The
competitor scan confirms the gaps SpecterX is right to fill:

- **First-time activation** as part of the same article. None of the
  three competitors cover it; SpecterX should, because the UI is the
  same component as reset.
- **Verification-code flow** (not link-based). Egnyte, Dropbox and
  HubSpot all use a link in the email. SpecterX uses a 6-digit code,
  which changes the user-facing instructions — explicitly name the
  code, its length, and the resend behavior.
- **Password complexity rules** as an explicit list. Dropbox and
  HubSpot link out; Egnyte doesn't cover it. SpecterX's UI shows the
  rules inline; the article should state all five.
- **SSO carve-out wording.** Egnyte's "Active Directory or SSO →
  contact your admin" pattern is the right template. SpecterX should
  do the same, naming Google Workspace, Microsoft / Entra ID, and
  Okta as the supported providers.
- **Email not arriving.** Dropbox and HubSpot cover the spam +
  allowlist case explicitly. Worth doing.
- **Self-service reset disabled.** Plan asks for it; no competitor
  covers it explicitly. SpecterX should, because admin-driven
  provisioning means self-service can be turned off per tenant.

## Coverage decisions for this article

| Item | Include? | Why |
|---|---|---|
| Reset from login page (procedure) | Yes | Core flow; matches all three competitors. |
| First-time activation entry point | Yes | Plan calls for it; same UI; competitors omit it but SpecterX users need it. |
| 6-digit code + resend cooldown | Yes | Codebase-confirmed; differs from competitor link-based flows; user-visible. |
| Password complexity rules (all five) | Yes | Codebase-confirmed; UI shows them inline; readers will look here to understand the requirements. |
| Allowed special characters list | Yes | Codebase-confirmed and finite; saves a guess-and-fail loop. |
| SSO carve-out (Google / Microsoft / Okta) | Yes | Plan calls for it; consistent with `COMPONENT_TAXONOMY.md`. |
| Spam / allowlist guidance | Yes | Plan calls for it; matches HubSpot + Dropbox patterns. |
| Code expiry | Yes (1 hour, Cognito default) | Plan calls for it. |
| In-app password change while signed in | **No** | SpecterX has no in-app change-password UI in the end-user web client; the reset flow is the only path. Out of scope. |
| Admin-driven reset for another user | **No** | That's an admin-portal article (out of scope for this end-user article). |
| Leaked-password check (HubSpot pattern) | **No** | Not implemented in SpecterX. |
| Account-lockout details | **No** | Cognito-managed; not exposed in the codebase. Mention attempt limit only as observed (3 wrong codes → restart). |
| Mobile guidance | **No** | SpecterX V1 mobile flows are out of scope per `ARTICLES_PLAN.md`. |

## Patterns NOT to copy

- **HubSpot's "Wrong password error" framing** as the entry point.
  We frame the article around the user's intent ("you forgot your
  password" / "you're setting your password for the first time"),
  not around a specific error message.
- **Egnyte's two-hour link expiry** wording. SpecterX uses Cognito's
  default 1-hour code expiry; do not borrow Egnyte's number.
- **Dropbox's "click your avatar → Settings"** in-app path. SpecterX
  has no equivalent for end users.
- **Marketing voice** in any of the three vendors' opening paragraphs
  ("Manage your account security…"). SpecterX leads with what the
  reader is here to do, not the value proposition.
