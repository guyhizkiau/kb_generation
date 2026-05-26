# Prompt: 03-revise-from-test

You revise `draft-1.md` based on what actually happened when the tester
executed it. Produce `draft-2.md`.

## What you read

- `articles/<NN-slug>/draft-1.md` — your original draft
- `articles/<NN-slug>/test-notes.md` — what the tester observed
- `articles/<NN-slug>/screenshots/` — the visual evidence

## What you produce

`articles/<NN-slug>/draft-2.md` — a revised version that matches
reality.

## How to revise

Read `test-notes.md` start to finish. For each step in your draft:

1. **If the tester succeeded and the UI matched your description**:
   leave the step alone. Just replace the screenshot placeholder with
   the real screenshot path.

2. **If the tester succeeded but the UI was different than you wrote**:
   update the step text to match what the tester actually saw. Don't
   pretend you knew all along; just write the correct version.

3. **If the tester failed at this step**: read their failure mode
   carefully.
   - Did they fail to find a UI element? → your selector hint was
     wrong. Update the step with the actual UI element name from
     the screenshot.
   - Did the step have unstated prerequisites? → add a preceding step.
   - Did the step take longer than expected (loading state)? → add a
     "Wait for X to appear" note in the step.
   - Did the step produce an unexpected modal/dialog? → add it as an
     intermediate step.
   - Did the step fail because the feature doesn't work that way at
     all? → flag this in a `> NOTE` block for the human reviewer. Do
     not silently rewrite the article into something different.

4. **If the tester observed something you didn't anticipate** (e.g. a
   permissions prompt, a tutorial overlay, a "what's new" banner):
   either add a "First time only:" sidebar to handle it, or add it as
   an explicit step.

## Format additions

Real screenshots use `![](screenshots/NN-filename.png)` Markdown image
syntax, immediately under the step they illustrate. No more `>
Screenshot: ...` placeholders in draft-2.

## When tests flagged "couldn't verify"

If the tester marked a step as `verified=false` or `couldn't verify`,
keep the step but add:

```markdown
> ⚠ Verification incomplete: <what the tester couldn't confirm>.
> Please confirm during review.
```

This becomes a flag for Guy to look at carefully in the PR.

## When you're done

Save `draft-2.md`. Update STATE:

```
PHASE=FINALIZING
LAST_UPDATE=<ISO>
NEXT_ACTION=tester does final pass to capture clean screenshots
```
