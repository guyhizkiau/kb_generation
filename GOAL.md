# Project goal

## In one sentence

Build and publish the SpecterX customer-facing knowledge base — **112
articles across 11 sections** — by running each article through an
auditable, mostly-autonomous authoring pipeline that grounds every claim
in the real product, validates it against the live UI, and learns a
consistent house style as it goes.

## What we are producing

A complete SpecterX help center: end-user, admin, recipient, and
developer articles covering login, file sharing, security policies,
email protection, Workspaces, integrations, compliance, and reference
material. The canonical editorial plan lives in
[`editorial/ARTICLES_PLAN.md`](editorial/ARTICLES_PLAN.md); the final
articles are produced under `articles/NN-slug/` and exported to ZenDesk.

## Why it is built this way

The hard problem is not writing 112 articles — it is writing 112
articles that are **accurate, consistent, and trustworthy** without a
human hand-authoring each one. The pipeline exists to make that possible:

- **Accuracy is verified, not assumed.** Every procedural article is
  driven through the live SpecterX product (Playwright over CDP for the
  web app, computer-use for desktop) so the steps, labels, and
  screenshots reflect what users actually see. Uncertain claims are
  marked `[verify in test]` and resolved by the tester, never guessed.
- **Claims are grounded in source.** Each article is researched against
  internal SpecterX docs, read-only reconnaissance of the product
  codebase (canonical UI strings, feature flags, error text), and at
  least three competitor articles on the same topic — a mandatory gate
  before any drafting begins.
- **Style is learned, not decreed.** There is no pre-existing house
  style. It is extracted from approved articles (the first few establish
  it, then it is refined every five merges) and captured in
  [`editorial/STYLE_GUIDE.md`](editorial/STYLE_GUIDE.md).
- **Review feedback fixes the root cause.** A review comment is resolved
  first in the canonical source of truth (style guide, glossary,
  taxonomy, scope, or a prompt) and only then applied to the article, so
  each fix improves every future article rather than just one.
- **The work is auditable.** A per-article `STATE` machine, one commit
  per pipeline phase, and committed test notes and screenshots make it
  possible to see exactly what the system saw and decided at each step.

## How it runs

Articles move through a five-stage pipeline (research → draft → validate
→ revise → PR & review), specified authoritatively in
[`WORKFLOW.md`](WORKFLOW.md). Phases can be run manually
(`python writer/run_claude_code.py --phase …`) or driven autonomously by
the `ops/pr-watcher/` daemon, which resolves PR comments, watches for
merges, and triggers the next article in a cluster.

## Definition of done

All planned articles are validated against the live product, approved by
review, merged, and published to ZenDesk — produced under a stable,
self-consistent style guide and glossary that the pipeline itself
maintained throughout.

## Out of scope

This goal covers the **KB article pipeline**. The reference-library
scraper and static-site tooling (`tools/`, `kb/`, `reference-library/`)
are a separate concern documented in [`AGENTS.md`](AGENTS.md); they
support the pipeline by supplying competitor research and preview pages
but are not the deliverable.
