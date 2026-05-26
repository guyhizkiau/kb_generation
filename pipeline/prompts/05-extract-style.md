# Prompt: 05-extract-style

You analyze every approved article and produce or update
`editorial/STYLE_GUIDE.md`. This is the most consequential prompt in the
pipeline; the resulting style guide governs every future article.

## When you run

- **First refresh: after article 3** (end of cluster 1 — special case)
- **Subsequent refreshes: every 5 approved articles** thereafter
  (after article 8, 13, 18, 23, ...)

## What you read

1. Every `final.md` in `articles/*/` whose corresponding STATE is
   `MERGED`. Read them in merge order (oldest first).
2. The PR review comments on each (fetch via
   `gh pr view <num> --json comments,reviews`). The comments tell you
   what reviewers cared about — which is at least as informative as
   the final text.
3. The previous `editorial/STYLE_GUIDE.md` if one exists.

## What you produce

A new `editorial/STYLE_GUIDE.md`. Not an append — a fresh write that
incorporates everything you observe.

## How to extract patterns

For each of the categories below, observe with care. Cite specific
articles by slug. Where you see drift or inconsistency between articles,
flag it as "needs review" rather than picking one.

### Category 1 — Voice

- **Person**: which articles use "you", "the user", or other? When
  does the choice change? Pick the dominant pattern and call out
  exceptions.
- **Tense**: present tense throughout? Future tense for results?
- **Tone**: read a paragraph aloud (figuratively). Crisp? Warm?
  Cautious? Find the adjectives that describe how the prose sounds.
- **Contractions**: do approved articles use "don't" / "you'll" or
  "do not" / "you will"? Count and decide.
- **Sample sentences**: cite 3–5 sentences from approved articles
  that exemplify the voice. These are the gold standard.

### Category 2 — Structural rhythm

- **Intro paragraph length**: count words across approved articles.
- **When intro uses 1 paragraph vs 2**: what determines it?
- **Step density**: average steps per article? Short articles (≤5
  steps) vs long?
- **Prose-to-bullets ratio**: rough proportion of running prose vs
  bullet points.
- **When to use callouts** (`> Note:`, `> ⚠ Warning:`, etc.): which
  approved articles use them, for what?
- **Section ordering**: do all procedurals follow the same
  before-you-start → steps → troubleshooting → out-of-scope → related
  order? Document deviations.

### Category 3 — Screenshot conventions

- **Density**: average screenshots per article?
- **What gets a screenshot**: every UI change? Only the dialog
  openings? Only the final result?
- **Cropping**: full viewport, or zoomed to the relevant area?
- **Annotations**: are arrows, boxes, highlights used? Which articles?
- **Caption format**: what goes under the screenshot, if anything?
- **Filename conventions**: NN-action.png? action.png?

### Category 4 — Step format

- **Step naming**: imperative ("Click Share") or descriptive ("The
  Share dialog")?
- **Step length**: words per step on average?
- **When a step is a sub-step vs a top-level step**: what's the rule?
- **Verb choices**: do we say "click" or "select" or "choose"? Pick
  one per UI action. Document the canonical verb per action type:
  - click: ...
  - type into field: ...
  - select from dropdown: ...
  - drag-and-drop: ...
  - hover: ...

### Category 5 — Vocabulary

Cross-reference with `canon/GLOSSARY.md`. Identify:
- Terms used inconsistently across articles
- Terms that appear in articles but not in glossary (proposals to add)
- Synonyms used (which to canonicalize)

### Category 6 — What we explicitly don't do

This is best learned from PR comments. Read every "this is wrong" or
"please remove" comment. Each is evidence for an anti-pattern. Build
a list of:
- Words/phrases that have been requested out (e.g. "simply",
  "easily", "just")
- Structural moves that have been rejected (e.g. "don't introduce
  multiple actions in one step")
- Visual decisions that have been undone (e.g. "don't annotate
  screenshots with red boxes")

### Category 7 — Article archetypes

After 10+ approved articles, you should be able to identify distinct
skeletons:
- **Procedural how-to** — most common, has the step-by-step pattern
- **Overview / concept** — explains what something is, no steps
- **Reference table** — capability matrices, browser support tables
- **Troubleshooting** — symptom → cause → fix
- **Integration setup** — multi-part, often spans days; different
  rhythm
- (others as you observe them)

For each archetype, identify which approved articles are examples,
and what's distinct about its structure.

## Output format

```markdown
# SpecterX KB — Style Guide

*Generated from <N> approved articles on <ISO date>. Next regeneration
after article <N+5> is approved.*

## Approved articles informing this guide

- 01-log-in-to-specterx (merged 2026-05-26)
- 02-set-or-reset-password (merged 2026-05-27)
- ...

## 1. Voice
...

## 2. Structural rhythm
...

## 3. Screenshot conventions
...

## 4. Step format

### Canonical verbs
- Click a button: "Click <Label>"
- Type into a field: "Enter <value> in the <Field name> field"
- Select from a dropdown: "Select <Option> from <Dropdown name>"
- ...

## 5. Vocabulary
(refer to GLOSSARY.md for the full list; this section notes
inconsistencies and resolution)

## 6. Anti-patterns

### Forbidden words
- "simply" — flagged in PR comments on articles 02, 04
- "easily" — flagged on 03
- ...

### Forbidden structures
- ...

## 7. Article archetypes

### Procedural how-to (default for §2–§8)
Skeleton: ...
Examples: 01-log-in-to-specterx, 03-share-a-folder, ...

### Overview / concept
Skeleton: ...
Examples: 02-what-is-specterx, ...

## 8. Things still under discussion

(Flag any genuine inconsistency you couldn't resolve; let Guy pick
in the style-guide PR review.)

- Articles 03 and 05 use different terms for the "Share & Permissions
  Drawer" (one calls it that, one calls it "Sharing panel"). Choose
  one.
- ...

---
*This document is the canonical style reference for the SpecterX KB.
Articles that conflict with it should be updated; the guide should
not be updated to accommodate one-off article choices unless those
choices are explicitly approved.*
```

## Important constraints

1. **Do not invent rules.** If a pattern isn't yet established across
   approved articles, do not claim it as canon. Mark it "no consensus
   yet" instead.

2. **Cite specific articles for every claim.** "Approved articles use
   'Click' for button presses" should be backed by "(see 01, 03, 04)".
   This makes the guide auditable.

3. **PR comments are gold.** The text in `final.md` is the final
   answer; the PR comments show *why* it's the final answer. Mine
   them aggressively.

4. **When in doubt, flag rather than decide.** It's better to leave a
   "needs review" note for Guy than to lock in a choice that wasn't
   actually made yet.

5. **Open a PR for the new STYLE_GUIDE.md.** Title:
   `style-guide: refresh after article <N> approved`. The PR body
   should highlight what changed since the previous version (use a
   diff-aware summary). After the first style guide (after article 5),
   PAUSE the pipeline until Guy approves the PR — no new articles
   should start until the canon is confirmed.

6. **Subsequent style guide refreshes** (after articles 8, 13, 18, ...)
   do not pause the pipeline. They open a PR; the pipeline continues
   using the previous version until the new one merges.
