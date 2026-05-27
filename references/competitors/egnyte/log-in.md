---
vendor: egnyte
source_url: https://helpdesk.egnyte.com/hc/en-us/articles/33892293265421-Two-Step-Login-Verification-User-Guide
title: "Two Step Login Verification - User Guide"
captured: 2026-05-26
captured_by: VM-Claude
search_query: "log in"
selected_because: "Top user-facing 'log in' search result in Egnyte's helpdesk. Egnyte does not publish a standalone 'how to log in' article — the closest end-user article is this TFA / two-step login guide."
---

# Two Step Login Verification - User Guide (Egnyte)

> Captured for SpecterX KB competitor research. Do **not** paste this
> wording into any SpecterX article. Use the checklist in
> `articles/01-log-in-to-specterx/research/competitor-coverage.md`.

## Coverage summary

What Egnyte's TSLV user guide covers:

- Listing the four available two-step methods (TOTP, Twilio Authy push,
  Twilio Authy app, phone number) at the top with anchor links.
- Enabling the feature from `Settings → My Profile → My Preferences →
  Security` and toggling on.
- Behaviour when an admin enforces TSLV (the user is forced into the
  registration screen at next login).
- Step-by-step registration for each method, with screenshots of the
  QR-code screen and the confirmation screen.
- Constraint callouts (e.g. "Phone number option is not available with
  Basic Two-Factor Authentication", "Authy does not allow Google
  Voice / Magic Jack / Skype virtual numbers").
- Per-method login flows: "Log in with username/email + password, then
  do X" for each of the four methods.
- A short section on how TSLV interacts with the Egnyte Desktop App.
- How to disable TSLV, including the 60-minute identity-confirmation
  window.
- Links to the Admin Guide and FAQ at the bottom.

## Patterns worth noting

- Anchor-link table of contents at the top of a long article (fine, but
  often a sign the article should be split — Egnyte's is borderline).
- Uses `Note` boxes inline rather than appending caveats to the step
  text. Looks tidy in a Zendesk theme; less elegant in plain Markdown.
- Mixes "the user" (third person) and "you" (second person) across
  sections — inconsistent. **SpecterX should pick second person
  consistently.**

## Patterns NOT to copy

- The article is essentially seven articles stapled together. The user
  has to scroll past methods they don't use to find the troubleshooting
  section. SpecterX should split by method when we ship MFA, not bundle.
- No prerequisites section: it jumps straight into the toggle. We want
  an explicit "Before you start" so the reader knows whether the
  feature applies to them.
- The "Login with" sub-headers assume the reader already knows whether
  they registered with TOTP vs Authy. We should add a "Which method
  is this?" cue.
