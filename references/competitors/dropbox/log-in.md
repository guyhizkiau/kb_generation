---
vendor: dropbox
source_url: https://help.dropbox.com/account-access/sign-in-out
title: "How to log into or out of your Dropbox account"
captured: 2026-05-27
captured_by: VM-Claude
search_query: "sign in"
selected_because: "Top general-purpose Dropbox 'log in' help article — covers web + desktop + mobile, plus linked accounts. Closest Dropbox/DocSend analogue to a 'how to sign in' end-user article."
---

# How to log into or out of your Dropbox account

> Captured for SpecterX KB competitor research. Do **not** paste this
> wording into any SpecterX article. Use the checklist in
> `articles/01-log-in-to-specterx/research/competitor-coverage.md`.

## Coverage summary

What Dropbox's sign-in article covers:

- An "In this article" table of contents at the top: log in, log out,
  problems logging in.
- A short scope note: "applies to all Dropbox customers."
- Account prerequisite: link to "create a Dropbox account" if you don't
  have one yet.
- Adjacent flows: link out to "change or reset your password" if you
  forgot your password; instructions for when you know the password
  but lost access to the email address.
- Three log-in surfaces in a tabbed layout: dropbox.com, desktop app,
  mobile app. Each surface has its own short procedure.
- Identity-provider options listed for each surface: email + password,
  **Google**, or **Apple** (Dropbox does not surface SSO in this
  article — SSO is in a separate `sso-team-member` article).
- "Sign up" branch for users without an account (CTA at point of
  decision, not as a separate flow).
- Linked-accounts ("logged into one, switch to the other") flow
  per surface, with platform-specific UI steps (taskbar icon, menu
  bar icon, avatar, Preferences > Account).
- Log-out instructions per surface, with the same tabbed layout.
- One-line troubleshooting fallback: "still experiencing issues?
  contact Dropbox Support." No troubleshooting matrix.
- An "updated on" date at the top, visible to the reader.

## Patterns worth noting

- **Tabbed multi-surface layout.** dropbox.com vs desktop vs mobile is
  surfaced as tabs in one article rather than three articles. Useful
  for a product available on three runtimes. SpecterX only has the
  web surface for now — not applicable yet.
- **Adjacent-flow links up front**, before the steps: "forgot
  password?", "no access to email?". Reduces the bounce-out rate for
  users who land here but actually need a different article.
- **Sign-up CTA at point of decision** ("If you don't have an account
  yet, click Sign up instead") embedded in the step text, not as a
  separate section. Good pattern for self-service products. SpecterX
  cannot adopt this — sign-up is administrator-driven — but the
  *principle* (mention the adjacent flow where the user is most
  likely to need it) is worth keeping.
- **"Updated on" visible to the reader.** SpecterX uses a
  "Last validated" line at the bottom, which is the same idea.
- **Identity providers named with bold/proper case** ("Google",
  "Apple"). SpecterX already does this.

## Patterns NOT to copy

- **No URL stated.** Dropbox says "go to dropbox.com" but doesn't
  spell out the full URL or the fact that there's a single host. For
  SpecterX, where most users go to `https://app.specterx.com` but
  some orgs use tenant subdomains, the URL must be explicit.
- **Troubleshooting collapsed to "contact support."** The article
  surfaces zero diagnostic guidance ("did you forget your password?
  did you use the wrong email?"). For SpecterX, a multi-surface
  troubleshooting section catches users whose fixable issue would
  otherwise become a support ticket.
- **Sign-in and sign-out bundled.** Two distinct user intents share
  one article. SpecterX article 01 is sign-in only; sign-out, if
  documented, belongs in its own article or as a sub-section *after*
  the primary flow.
- **No SSO coverage in the canonical sign-in article.** Dropbox
  splits SSO into a separate `sso-team-member` article, forcing
  enterprise users to hunt. SpecterX puts SSO and email+password
  side-by-side in the same article because that's the moment of
  choice for the end user.
- **No "Before you start" / prerequisites section.** Like Egnyte and
  Virtru, Dropbox jumps straight to the procedure. SpecterX leads
  with prerequisites.
- **Mixed "log in" / "sign in" wording.** Dropbox uses "log in" in
  the article title and headings, but the UI says **Sign in**. The
  article body uses both. SpecterX picks one term and uses it
  consistently — match the UI.
