# Prompt: 04-revise-from-pr-comments

Guy reviewed your PR and left comments. Address them and push an
update.

## What you read

- `articles/<NN-slug>/final.md` — the current state on the PR
- `articles/<NN-slug>/pr-comments.json` — comments fetched by the
  orchestrator from GitHub, with line numbers, body text, and resolved
  status
- The PR description and overall body (also in pr-comments.json)

## What you produce

An updated `articles/<NN-slug>/final.md`, plus optionally:
- New screenshots if a comment requested visual evidence
- An update to `test-plan.json` if the comment implies the test should
  re-run
- Changes to nothing else (don't touch sources, don't touch other
  articles)

## How to handle different comment types

### "This step is wrong / unclear / missing"
Fix the step. Re-test it if the fix is non-trivial (the orchestrator
will detect modified `test-plan.json` and re-run the test).

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
Apply the change. No need to re-test.

### "LGTM" / approval
Don't do anything. The orchestrator handles the merge state machine.

## Reply on PR

After making changes, for each comment you addressed, post a brief
reply on the PR thread:
- "Fixed in <commit-sha>"
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
