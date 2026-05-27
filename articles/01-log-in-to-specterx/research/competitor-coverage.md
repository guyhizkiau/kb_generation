# Competitor coverage checklist — Log in to the SpecterX web platform

## Cache status

Three vendor articles captured for this topic:

| Vendor | Source | Captured |
| --- | --- | --- |
| Egnyte | [Two Step Login Verification — User Guide](https://helpdesk.egnyte.com/hc/en-us/articles/33892293265421-Two-Step-Login-Verification-User-Guide) | 2026-05-26 |
| Virtru | [Using Single Sign-On (SSO) with Virtru](https://support.virtru.com/hc/en-us/articles/360041187653-Using-Single-Sign-On-SSO-with-Virtru) | 2026-05-27 |
| Dropbox/DocSend | [How to log into or out of your Dropbox account](https://help.dropbox.com/account-access/sign-in-out) | 2026-05-27 |

Per-vendor source files live under `references/competitors/<vendor>/log-in.md`
and are indexed in `references/competitors/INDEX.json`.

**Notable structural finding across all three vendors:** none of them
publishes a single "how to sign in" article that puts SSO and
email+password side-by-side as the user's branching choice. Egnyte's
closest article is about two-step verification. Virtru's closest is an
admin+user SSO bundle. Dropbox's article omits SSO entirely and links
out to a separate `sso-team-member` article. SpecterX choosing to
publish a unified sign-in article with the SSO/email branch in one
place is a deliberate departure from the SaaS norm, and a good one.

## Per-vendor coverage checklists

### Egnyte — Two Step Login Verification User Guide

What Egnyte's article covers (note: **not** a "how to log in" article;
it's a two-step verification guide where the login flow is a
sub-section):

- [ ] URL guidance — not covered (assumes the user is already at the
      sign-in page).
- [ ] "Before you start" / prerequisites — not covered (jumps to toggles).
- [x] Multiple sign-in path branches — covered as "Login with X" sub-headers
      per registered TFA method (TOTP / Authy / phone).
- [x] Step-by-step screenshots — covered for QR-code and confirmation.
- [x] Constraint callouts — covered ("Phone number not available with
      Basic Two-Factor Authentication", etc.).
- [ ] Troubleshooting for failed sign-in — minimal; mostly TFA-specific.
- [x] Related-article links — present at the bottom (Admin Guide, FAQ).
- [ ] Sign-out flow — not covered (out of scope here).

### Virtru — Using Single Sign-On (SSO) with Virtru

What Virtru's article covers (note: mixes admin configuration and
end-user sign-in into one article):

- [ ] URL guidance — not covered (assumes Control Center already loaded).
- [ ] "Before you start" / prerequisites — covered for **admins**
      (contact CSM to enable SSO), not for **end users**.
- [x] SSO sign-in path with screenshots — covered for Control Center,
      Gmail plugin, mobile apps, and Secure Reader.
- [ ] Email + password sign-in path — not covered in this article
      (user is told to "select Cancel to log in via a different
      pathway" if SSO is not integrated; the other pathway is
      documented elsewhere).
- [x] One inline error-state callout — covered ("Email address not
      recognized"), using a `Note` box.
- [ ] Troubleshooting matrix — not covered; only the one error state.
- [ ] Browser / cookies guidance — not covered.
- [ ] Sign-out flow — not covered.

### Dropbox — How to log into or out of your Dropbox account

What Dropbox's article covers:

- [ ] URL guidance — partial ("go to dropbox.com") but no full URL or
      tenant-aware advice.
- [ ] "Before you start" / prerequisites — not covered (jumps to procedure).
- [x] Multi-surface coverage — web, desktop, mobile — covered as
      tabs in a single article.
- [x] Identity-provider options — Email + password, **Google**, **Apple**
      named with bold/proper case. (SSO is **not** in this article; it
      lives in a separate `sso-team-member` page.)
- [x] Adjacent-flow links up front — covered ("forgot password?",
      "no access to email?") before the procedure.
- [x] Linked-accounts flow — covered per surface, with platform-specific
      UI cues (taskbar icon, menu bar icon, Preferences > Account).
- [x] Sign-out flow — covered in tabs, mirroring the sign-in layout.
- [ ] Troubleshooting matrix — collapsed to one line: "still having
      issues? contact Dropbox Support." No diagnostic guidance.
- [x] "Updated on" date visible to the reader — covered (Jul 30, 2025).

## Overall coverage gaps vs our `editorial/ARTICLES_PLAN.md` entry

The plan entry already calls out the user-facing topics this article
must cover. The competitor scan confirms these items are gaps in the
broader market that SpecterX is right to fill:

- **URL format for the customer's own SpecterX instance**
  (`yourorg.specterx.com` vs `app.specterx.com`). **None** of Egnyte,
  Virtru, or Dropbox tell the user where to go.
- **What to do when SSO fails** ("access denied", "not authorised").
  Virtru documents one SSO error state and stops; Egnyte and Dropbox
  don't cover SSO sign-in errors in their canonical articles.
- **Where to find the org's login URL** (from IT). No competitor does
  this — they assume the user is already on the right page.
- **What to do when the account isn't yet provisioned.** None of the
  three competitor articles addresses this explicitly. Dropbox does
  link to "create an account," but that's a self-service path
  irrelevant to SpecterX's admin-driven provisioning model.
- **SSO and email+password as a single conditional in one article.**
  Every competitor either splits them across articles or omits one.
  SpecterX's unified approach is more useful for end users.

No new coverage gaps surfaced by the competitor scan. The plan entry
remains complete; the final article matches it.

## Patterns NOT to copy

Consolidated from all three vendors:

- **Mixed audience (admin + end user) in one article.** Virtru bundles
  SSO configuration and end-user sign-in. SpecterX keeps these
  separate: end-user "sign in" vs. admin "configure SSO."
- **No URL stated.** All three vendors assume the user already knows
  where to go. SpecterX always states the URL explicitly, including
  the tenant-subdomain caveat.
- **Troubleshooting collapsed to "contact support."** Dropbox does this;
  Virtru and Egnyte do it implicitly by omission. SpecterX provides a
  multi-row troubleshooting section that catches fixable issues
  (wrong email, bad password, cookies blocked, SSO succeeded but
  account missing, wrong URL) before they escalate to support tickets.
- **Sign-in and sign-out bundled.** Dropbox does this. SpecterX
  article 01 is sign-in only; sign-out, if documented, gets its own
  article. Two distinct user intents = two articles.
- **SSO and email+password split across separate articles.** Both
  Virtru and Dropbox force enterprise users to hunt. SpecterX puts
  both paths side-by-side at the moment of choice.
- **No "Before you start" section.** All three competitors jump
  straight into the procedure. SpecterX always leads with
  prerequisites.
- **Inconsistent voice and inconsistent term choice.** Egnyte mixes
  third and second person ("the user will be asked" vs "you'll be
  asked"). Dropbox mixes "log in" and "sign in" while the UI says
  Sign in. SpecterX picks second person and matches the UI's term
  consistently ("Sign in").
- **Anchor TOCs on short articles.** Egnyte and Virtru both use
  "Jump to" anchor lists at the top of articles with only a handful
  of sections. Save TOCs for long reference articles where scrolling
  is a real cost.
- **Bundling per-method "Login with X" sub-articles within one
  article.** Egnyte does this with TFA methods (TOTP / Authy / phone).
  SpecterX uses a single procedural flow with one conditional branch,
  not a series of parallel recipes.
- **Inline "Sign up" CTA at point of decision** (Dropbox pattern).
  *Not* a bad pattern in general, but SpecterX cannot adopt it: there
  is no self-service sign-up. The article correctly states accounts
  are admin-created.
