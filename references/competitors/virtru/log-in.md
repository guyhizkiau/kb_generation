---
vendor: virtru
source_url: https://support.virtru.com/hc/en-us/articles/360041187653-Using-Single-Sign-On-SSO-with-Virtru
title: "Using Single Sign-On (SSO) with Virtru"
captured: 2026-05-27
captured_by: VM-Claude
search_query: "sign in"
selected_because: "Top user-facing 'sign in' search result in Virtru's Zendesk help portal. Virtru does not publish a standalone 'how to sign in to Virtru' article — the closest article covers how SSO sign-in works across Virtru's Control Center, Gmail/Outlook plugins, and Secure Reader."
---

# Using Single Sign-On (SSO) with Virtru

> Captured for SpecterX KB competitor research. Do **not** paste this
> wording into any SpecterX article. Use the checklist in
> `articles/01-log-in-to-specterx/research/competitor-coverage.md`.

## Coverage summary

What Virtru's SSO article covers:

- A short "About" intro: when SSO applies (organisations using SAML)
  and that this article covers configuration plus end-user impact.
- A "Jump to" anchor list (4 sections) at the top.
- Configuration prerequisites: link to the SAML admin guide; note that
  Virtru must enable the feature for the account before configuration
  starts; instruction to contact Customer Success Manager or Support.
- Signing into the Control Center with SSO: step-by-step UI walkthrough
  with screenshots of the "Use Single Sign-On (SSO)" option, the email
  entry page, and the redirect to the org's SSO provider.
- Error-state callout (`Note` box): what happens when Virtru and the
  customer's SAML are not yet integrated — user sees "Email address
  not recognized" and must select **Cancel** to use a different path.
- Activating Virtru products via SSO: separate sub-sections for the
  Gmail browser plugin and mobile apps, each showing the activation
  prompt and how SSO redirects work during product activation.
- Signing into the Secure Reader with SSO: a one-paragraph mention
  that configured organisations get auto-routed to SSO from the
  verification page.

## Patterns worth noting

- Bundles **configuration** (an admin task) and **end-user sign-in**
  (a user task) into one article. Mixing audiences in a single article
  is a common but bad pattern.
- Uses inline `Note` callout for the most common error state. Useful
  pattern: an inline error callout where the error is likely to appear.
- Screenshots show actual UI states (entry page, redirect, error).
  Good pattern — SpecterX already does this.
- "Jump to" anchor list at top, even though only 4 sections.

## Patterns NOT to copy

- **Mixed audience.** This article tells SSO admins how to configure
  AND tells end-users how to sign in. SpecterX keeps these separate:
  end-user "sign in" article vs. admin "configure SSO" article.
- **No URL guidance.** Virtru never tells the user *where* to start
  (the Control Center URL). It assumes the user is already there.
  SpecterX should always state the URL.
- **No "Before you start" section.** Like Egnyte, Virtru jumps
  straight into the procedure. We lead with prerequisites.
- **"Email address not recognized" is the only failure surfaced.**
  No troubleshooting for SSO succeeding but Virtru account missing,
  no guidance for browsers blocking cookies, no guidance for the
  wrong URL. SpecterX's troubleshooting matrix is more complete.
- **No mention of email+password sign-in path** in this article. The
  user is expected to "select Cancel to log in via a different
  pathway" but the other pathway is documented elsewhere. Splitting
  the two sign-in paths across separate articles forces the user to
  hunt; SpecterX puts both paths in one article with a clear branch.
