# Competitor coverage checklist — Log in to the SpecterX web platform

## Cache status

- `references/competitors/INDEX.json` was empty at the start of this
  article's research.
- HubSpot, Vera, DocSend, and Virtru have no cached login articles. Out
  of scope to scrape four more vendors for a basic login article;
  pulled one reference vendor (Egnyte) and moved on.
- One scrape performed: Egnyte's
  [Two Step Login Verification – User Guide](https://helpdesk.egnyte.com/hc/en-us/articles/33892293265421-Two-Step-Login-Verification-User-Guide)
  (captured 2026-05-26). Notable finding: Egnyte does **not** publish a
  standalone "how to log in" article. The login mechanics are folded
  into the broader product. SpecterX choosing to publish one is a
  deliberate departure.

## What competitors thought worth covering

From the Egnyte TSLV guide (cached 2026-05-26):

- [x] Distinguish between SSO and non-SSO authentication paths — we
      already plan this (the plan entry calls out both).
- [x] Per-method login flows ("if you registered with X, do Y") —
      we cover this implicitly: SSO redirects vs email+password.
- [x] Explicit constraint callouts ("not available with Basic ...") —
      adopt this for SSO-vs-email-password.
- [x] Link to a "Reset password" / "Set password" article for the
      adjacent flow — already in our cluster as article 02.
- [ ] Anchor TOC at the top of the article — **rejected**: our article
      is short (≤6 steps); a TOC would be visual noise.
- [ ] Bundle multiple methods into one article — **rejected**: SSO and
      email+password are the only two paths; that's not a bundle, it's
      a conditional intro.

## Coverage gaps vs `editorial/ARTICLES_PLAN.md` entry

Plan entry already covers the things Egnyte doesn't:

- URL format for a customer's own SpecterX instance
  (`yourorg.specterx.com` vs `staging-app.specterx.com`).
- What to do when SSO fails ("access denied", "not authorised").
- Where to find the org's login URL (from IT).
- What to do when the account isn't yet provisioned.

No new coverage gaps surfaced by the competitor scrape. Move on.

## Patterns NOT to copy

- **Third-person voice** ("the user will be asked"). Egnyte mixes
  voices; SpecterX uses second person consistently ("you'll be asked").
- **Anchor TOCs on short articles.** Save them for long reference
  articles where scrolling is a real cost.
- **No "Before you start" section.** Egnyte jumps into the toggle.
  SpecterX articles always lead with prerequisites.
- **Bundling SSO and email+password into separate "Login with X"
  sub-articles within one page.** Our article uses a single procedural
  flow with a one-time branch (SSO redirect or credentials form) and
  treats the choice as a conditional, not as a parallel set of recipes.
