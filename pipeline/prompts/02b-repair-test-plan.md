# Prompt: 02b-repair-test-plan

You fix a failing `test-plan.json` after an automated browser test run.
You do **not** edit the draft, STATE, or any file outside the test plan.

## What you read (in order)

1. `operator-instructions.md` — if present, read first. Treat operator
   guidance as authoritative. Do not delete applied entries; append a
   line `<!-- applied YYYY-MM-DD -->` under each consumed block.
2. The most recent `test-notes-attempt-*.md` (or `test-notes.md` if no
   archive exists). Focus on the **First failure** step named in the header.
3. `screenshots/` — visual evidence from the failed run.
4. `draft-1.md` — the article's intended flow (derive click targets from
   the draft's literal instruction text).
5. `test-plan.json` — the plan to repair.

## What you produce

An updated `test-plan.json` that fixes the failure modes below without
deleting steps or weakening `verify` conditions to force a pass.

## Known failure modes

| Symptom | Fix |
|---------|-----|
| Clicked dropdown parent instead of revealed option | After a `hover` that reveals a menu item, the next `click` must target the **revealed option's exact label** from the draft, not the parent trigger. |
| `selector_hint` timeout on a label | Replace with `role`+`name` or a `data-testid` from the codebase (grep `~/specterx-codebase/web-client/`). |
| Drawer/modal never opened | Insert a `wait_for` on the drawer's root element before interacting inside it. |
| Wrong `data-testid` | Grep the web-client for the correct test id; use the table in `02-test-plan.md`. |
| Step 18 passed but step 19 can't find "Who has access" | Use `[data-testid='myFiles_WhoHasAccess']` consistently instead of `get_by_text`. |

## Rules

- Fix the plan only — never edit `draft-1.md`.
- Do not remove steps to skip failures.
- Do not change `verify` strings to empty or trivial values.
- Preserve login steps (`00-*`) and cleanup steps (`C*`).
- If operator instructions conflict with test-notes, prefer operator instructions.

## When you're done

Save `test-plan.json` and exit. The pipeline runner clears `NEXT_ACTION`
so the tester can re-run.
