# Prompt: 04-revise-from-pr-comments

Guy reviewed your PR and left comments. Address them and push an
update — **fixing the root cause first** (WORKFLOW.md §9.5), so each fix
holds for every future article, not just this one.

## What you read

- `articles/<NN-slug>/final.md` — the current state on the PR
- `articles/<NN-slug>/pr-comments.json` — comments fetched from GitHub
  (e.g. `gh pr view`), with line numbers, body text, and resolved status
- The PR description and overall body (also in pr-comments.json)
- The canonical file the comment points at (see the map below) — you read
  this **before** touching the article.

## The order of work (root cause first)

This is the inversion that matters: do **not** start by editing the
article. Follow WORKFLOW.md §9.5:

1. **Classify** the comment against the canonical-target map:

   | Comment is about… | Fix-first file |
   |---|---|
   | Voice / tone / wording / structure / anti-pattern | `editorial/STYLE_GUIDE.md` |
   | A product term, definition, or canonical phrasing | `canon/GLOSSARY.md` |
   | A component's name or category | `product/COMPONENT_TAXONOMY.md` |
   | Public-vs-internal scope, audience split | `editorial/PUBLIC_KB_SCOPE.md` |
   | "We shouldn't document this / not shipped" | `canon/DO_NOT_DOCUMENT.md` |
   | Article scope, topics, sequencing | `editorial/ARTICLES_PLAN.md` |
   | A process / pipeline-instruction gap | the relevant `pipeline/prompts/*.md` or `WORKFLOW.md` |
   | A one-off product fact, blurry screenshot, single factual fix | **none** — article-only, with a justification |

2. **Generalize when applicable, else justify.** If a canonical file
   applies, edit *that file first* and commit it alone
   (`docs(canon|style|taxonomy|scope): …`). If the comment is genuinely
   article-specific, write a one-line justification in the PR reply and
   skip to the article fix — don't invent a contrived canon edit.

3. **Apply to the article from the updated canon.** Re-read the file you
   just edited and fix `final.md` *from it*, not from memory. Commit the
   article separately (`fix(article): …`). Two commits, in this order.

4. **Validate against the original comment** (always, the closing step):
   re-check the fix against what the reviewer asked — quote the ask, point
   to the resolved text. If it does **not** resolve the ask: diagnose why,
   then **expand** the canonical rule (add a clause / example / precise
   label — never replace the general rule with an article-only
   instruction), re-apply, and re-validate. Bound to 2 retries; then escalate
   (BLOCKED) with the diagnosis and the current expanded-rule state.

## What you produce

- An update to the relevant **canonical file** (unless the comment is
  genuinely article-specific — then a one-line justification instead).
- An updated `articles/<NN-slug>/final.md` applying that canon.
- New screenshots if a comment requested visual evidence.
- An update to `test-plan.json` if the comment implies the test should
  re-run.
- Do not touch other articles or sources beyond the canonical file the
  comment routes to.

## How to handle different comment types

Each type names its fix-first file. Always run the validate step (§9.5
step 4) after applying the fix.

### "This step is wrong / unclear / missing"
Usually article-specific (a fact about one flow) → article-only with a
one-line justification. But if the error came from a wrong canonical label
or a missing process check, fix that first (`COMPONENT_TAXONOMY.md`,
`GLOSSARY.md`, or the relevant `pipeline/prompts/*.md`). Re-test if the fix
is non-trivial (re-run `python tester/runner.py` after updating
`test-plan.json`).

### "Add a screenshot showing X"
If the screenshot exists in `screenshots/_all/` (the unfiltered set the
tester captured), add it. Otherwise, modify the test plan to capture
that screenshot, and let the test re-run.

### "Remove this section / consolidate steps N and N+1"
Do it. Don't re-test unless the changes affect the actual flow.

### "This contradicts <other article>"
Read the other article. If your article is correct and the other is
stale, leave a comment on the PR saying so and asking Guy to choose.
Do not silently change one to match the other.

### "Question: does this also work for <variation>?"
You generally don't know without testing. Options:
- If trivial to test: extend the test plan to cover it, re-run, fold
  the result into the article
- If non-trivial: reply to the comment saying "Out of scope for this
  article; logged as #<issue>" and open a separate GitHub issue

### "Nit: wording / formatting"
Fix the **rule** first. A wording/formatting nit almost always reflects a
`STYLE_GUIDE.md` rule that is missing or too vague — add or sharpen it
there, then apply it to the article. No need to re-test. If the style guide
already covers it and was simply not followed, note that in the reply and
just apply the existing rule (no canon edit needed).

### "LGTM" / approval
Don't do anything. Update `STATE` when Guy merges the PR on GitHub.

## Reply on PR

After making changes, for each comment you addressed, post a brief
reply on the PR thread. State **both** the canonical change and how it
resolved the article (this is the visible test result):
- "Rule: added <clause> to STYLE_GUIDE.md §13. Applied in <article-sha>;
  validated against the comment."
- "Article-specific (no canon change): <one-line justification>. Fixed in
  <commit-sha>."
- "Expanded GLOSSARY.md after first attempt didn't resolve it — <what was
  sharpened>. Re-applied in <sha>."
- "Couldn't reproduce — see <screenshot>"
- "Logged as #<issue> for follow-up"

Use `gh pr comment` for top-level replies and the GitHub API for
inline replies (via `gh api` POSTing to the review comment endpoint).

## When you're done

If the changes were small (text only):
```
PHASE=PR_OPEN
LAST_UPDATE=<ISO>
NEXT_ACTION=push and request re-review
```

If the changes touched the test plan:
```
PHASE=TESTING
LAST_UPDATE=<ISO>
NEXT_ACTION=re-run modified test plan
```

If you couldn't address a critical comment and need Guy's input:
```
PHASE=BLOCKED
LAST_UPDATE=<ISO>
BLOCKED_REASON=<short summary>
NEXT_ACTION=wait for Guy
```
