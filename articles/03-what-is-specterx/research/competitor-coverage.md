# Competitor coverage checklist — What is SpecterX?

## Cache status

Five vendor pages captured. All five vendors have something that fills
the "what is this product?" slot in their KB, but the shapes diverge
sharply.

| Vendor | Source | Captured | Shape |
| --- | --- | --- | --- |
| Egnyte | [Getting Started Guide for Egnyte Connect](https://helpdesk.egnyte.com/hc/en-us/articles/360029184571-Getting-Started-Guide-for-Egnyte-Connect) | 2026-06-01 | First-tasks tour |
| Virtru | [How Virtru keeps files and data secure](https://support.virtru.com/hc/en-us/articles/360039055854-How-Virtru-keeps-files-and-data-secure) | 2026-06-01 | Security model primer |
| DocSend | [What is Dropbox DocSend?](https://help.dropbox.com/plans/what-is-dropbox-docsend) | 2026-06-01 | Definition + capabilities |
| HubSpot | [Get Started](https://knowledge.hubspot.com/get-started) | 2026-06-01 | Navigation hub |
| Vera | [Vera Documentation (home)](https://docs.tricentis.com/vera-latest/content/home.htm) | 2026-06-01 | Docs landing tiles |

Per-vendor cached files live under
`references/competitors/<vendor>/what-is.md` and are indexed in
`references/competitors/INDEX.json`.

## Shape budget

Two patterns dominate:

- **Shape A — definition + capabilities** (DocSend, Virtru). Open with
  a one-paragraph definition, then break the product apart into
  3 to 5 capability sections. Sparse screenshots (0 to 1). Prose-led.
- **Shape B — navigation hub** (HubSpot, Egnyte, Vera). Define the
  product in a sentence, then route the reader to per-job sub-pages.
  Icons instead of screenshots. Treats the overview as a navigation
  problem.

**Recommendation:** Shape A for SpecterX. SpecterX is a single
coherent product (not a suite like HubSpot), and the reader of this
article is usually a sender or recipient who needs to understand the
product end-to-end before doing anything. Fragmenting into tiles
would push the "what is it?" answer onto the reader.

### Target metrics for SpecterX

| Metric | Competitor median | Target for this article |
| --- | --- | --- |
| Word count | 350 to 500 | 400 to 600 |
| Screenshot count | 0 to 1 | 0 to 2 |
| Intro length | 1 paragraph (1 to 3 sentences) | 1 to 2 short paragraphs |
| Capability bullets | 3 to 5 | 3 to 5 |
| "Is NOT" section | None of the five vendors include it | **Include it.** This is SpecterX's main differentiator from the competitor norm. |

## What they thought worth covering

Aggregated across the five vendors:

- [x] One-sentence product definition near the top — all five.
- [x] What the product does (capabilities or "what you can do") —
      all five, framed as either capability sections (Shape A) or
      task tiles (Shape B).
- [x] Who the audience is, implicit in framing — all five.
- [x] How the product fits with existing tools (identity, storage,
      email) — Virtru and Egnyte; DocSend skirts it.
- [x] Concept glossary — only HubSpot links to one as a separate
      page; nobody defines concepts in-page.
- [ ] Explicit "what this is NOT" — none of the five.
- [ ] Comparison to alternatives — none of the five.
- [ ] Recipient-side experience (what a non-account-holder sees) —
      only Virtru hints at it; DocSend covers "viewing experience"
      but only from the sharer's perspective.
- [ ] First steps / next actions inline — Egnyte does this well
      (its overview doubles as first-task onboarding); the others
      either skip or link out.

## Related topics they reference inline

- Setting up an account / first login (all five)
- Sharing a file or document (Egnyte, DocSend, Virtru)
- Recipient access / verification flow (Virtru, DocSend)
- Security policies / access controls (Virtru, Vera)
- Integration with email or identity (Virtru, Egnyte)

For SpecterX, the inline cross-references at points of friction
should be:

- "Log in to the SpecterX web platform" — when the reader is told
  this is a web product, link the login article.
- "Set or reset your password" — when the article mentions accounts,
  link the password article.
- Workspace / file-sharing / Outlook / Gmail articles — when each
  capability is introduced, link out (but only if those articles
  exist; for now they are placeholders).

## Coverage gaps in our plan entry

The `editorial/ARTICLES_PLAN.md` entry (lines 15-26) calls for seven
sub-topics. The competitor scan confirms all seven are worth keeping
and adds two more:

- **Concept set defined in-page.** None of the five competitors
  defines concepts on the overview page itself. HubSpot links out to
  a glossary. SpecterX should define its small concept set (sender,
  recipient, policy, viewer) in-page because the article is the
  first place a reader meets these terms.
- **Two-actor framing (sender + recipient).** The plan calls for it;
  none of the five competitors uses this framing because their
  products mostly have one actor (the user). SpecterX is unusual
  in that the recipient is a first-class user with their own UX,
  and the article should lean on that distinction.

## Coverage decisions for this article

| Item | Include? | Why |
| --- | --- | --- |
| One-paragraph definition | Yes | Universal in competitor set. Lead with it. |
| The problem SpecterX solves | Yes | Plan calls for it. Concrete framing: what goes wrong without it. |
| Two actors: sender and recipient | Yes | Plan calls for it; differentiator vs competitors. |
| Three core use cases (web share, Outlook/Gmail, Workspace) | Yes | Plan calls for it. Use as the "what you can do" section. |
| What a security policy is | Yes | Plan calls for it; SpecterX-specific term. |
| Recipient experience (Recipient Page, Viewer, verification) | Yes | Plan calls for it; competitors mostly skip this. |
| What SpecterX is NOT | Yes | Plan calls for it; biggest editorial gap in the competitor set. |
| How SpecterX relates to identity / storage / email infra | Yes | Plan calls for it. Keep short. |
| Pricing / plan tiers | **No** | Out of scope for KB; not in any competitor article either. |
| Step-by-step "first time" tasks (Egnyte's pattern) | **No** | We have separate procedural articles. Link out. |
| Deep encryption / security model (Virtru's pattern) | **No** | Out of scope for a user-facing overview. Could be a separate article. |
| Glossary as a separate page | **No** | Not yet built. Define the small concept set inline. |
| Mobile or desktop apps | **No** | Mobile is V1-out-of-scope per plan. |

## Patterns NOT to copy

- **DocSend's marketing-led capability framing** ("you can do X, you
  can do Y..."). Capability descriptions should be neutral and
  task-grounded, not sold.
- **Virtru's encryption-heavy lead** (zero trust, AES-256, TDF as the
  opening concepts). SpecterX should not lead with cryptography;
  most readers want to know what to do, not how the math works.
- **HubSpot's hub-page navigation pattern.** SpecterX's overview
  should be a single readable article, not a tile menu.
- **Vera's "you've got this" tone.** Reassurance lines like that
  read as marketing voice in a KB context. The style guide bans them.
- **Vera's no-overview pattern.** Tiles without a definition are
  the wrong default for a first-read article.

## Shape budget summary

- **Length.** 400 to 600 words including the front matter intro.
- **Screenshots.** Up to 2. Use only if a screenshot adds information
  the prose cannot ("here is what the recipient sees" is the one
  candidate; do not screenshot a logo or a dashboard for its own
  sake).
- **Sections.** Intro (1 short paragraph) → Problem → Core concepts
  (sender / recipient / policy) → What you can do → What you see as
  a recipient → What SpecterX is NOT → How it fits with your
  existing tools → Related articles.
- **Voice.** Calm, neutral, second person, present tense. No
  motivational openers. No "easily" or "simply." No claim about
  speed, ease, or modernity.
