# Prompt: 01-draft

You are writing the first draft of a SpecterX knowledge-base article.

## Context

You have these inputs (read them before writing):

1. The article entry in `editorial/ARTICLES_PLAN.md` — title, intent, scope
2. Any reference docs listed under `sources/` that the plan entry
   references
3. Any prior articles in `articles/` that touch the same product area
   (read at least their `final.md` to match voice and structure)

## What you produce

A file at `articles/<NN-slug>/draft-1.md` containing the article in its
first form. Structure:

```markdown
---
title: <Article title>
audience: <admin | end-user | developer>
estimated-reading-time: <N min>
prerequisites:
  - <prereq 1>
  - <prereq 2>
---

# <Article title>

<One-paragraph intro: what this article teaches, who it's for, what
they'll have at the end.>

## Before you start

<Prerequisites in prose; what the reader needs set up first.>

## Steps

### 1. <Step name>

<What the user does. Active voice. One action per step.>

> Screenshot: <placeholder describing what should be shown>

### 2. <Step name>

...

## Troubleshooting

<Common things that go wrong, with fixes. Optional if not applicable.>

## What's next

<Links to related articles, optional.>
```

## Rules

- **One action per step.** "Click Share, then enter the recipient's
  email" is two steps, not one.
- **Screenshot placeholders are mandatory.** Every step that involves a
  UI change gets a `> Screenshot: ...` line. The tester will fill these
  in. Be specific about what should be visible: not "screenshot of
  dashboard" but "screenshot of dashboard with the Share button
  highlighted in the top-right".
- **Active voice, second person.** "Click Share", not "The Share button
  should be clicked".
- **No marketing copy.** This is a how-to, not a product page. Don't
  write "SpecterX's powerful sharing engine makes it easy to..."
- **Don't invent UI elements.** If you don't know whether a button is
  labeled "Share" or "Send" or "Distribute", write
  `<unknown label — verify in test>` and move on. The tester will fix
  it.
- **Don't pad.** A 4-step article is 4 steps. Don't add ceremonial
  steps like "Open your browser" unless they're actually necessary.

## Anti-patterns to avoid

- Recursive screenshots (a screenshot of you taking a screenshot)
- "Note:" boxes for things that should just be in the step itself
- Conditional branching at top level (split into multiple articles
  instead)
- Reproducing source material verbatim — synthesize, don't paste

## When you're done

Save `draft-1.md`. Update `articles/<NN-slug>/STATE` to:

```
PHASE=TESTING
LAST_UPDATE=<ISO timestamp>
NEXT_ACTION=execute draft against live SpecterX
```

Then exit. The orchestrator picks up from STATE.
