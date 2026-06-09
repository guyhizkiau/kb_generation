# Phase: revise-from-feedback

You are VM-Claude resolving SME feedback annotations on a published KB article.

## Inputs

- `articles/<slug>/final.md` — the current article text
- Ghostwriter feedback store: `.ghostwriter/feedback/<slug>.json` (on the VM:
  `/home/ubuntu/ghostwriter-feedback/<slug>.json`) — W3C Web Annotation JSON array;
  each item has:
  - `id` — annotation URI
  - `body[].value` — the reviewer's comment text
  - `target.selector` — one of:
    - `TextQuoteSelector`: `{ type, exact, prefix, suffix }`
    - `FragmentSelector`: `{ type, value }` (e.g. `xywh=160,120,300,80` on a screenshot)
  - `creator.name` — reviewer name (include in commit message attribution)

## Resolution rules

### TextQuoteSelector annotations

1. Use `exact` (with `prefix`/`suffix` for disambiguation) to locate the text in `final.md`.
2. Apply the reviewer's comment to that passage — reword, expand, correct, or restructure as needed.
3. If you can locate the text but the change is unclear: note the ambiguity in your resolution
   summary and leave the passage unchanged.
4. If the selector no longer matches (orphaned — the text was already edited): log it as ORPHANED
   and skip.

### FragmentSelector annotations (image regions)

The `value` field is a CSS Media Fragments string like `xywh=160,120,300,80` anchored to the
screenshot referenced in the annotation's `target.source`.

1. Identify which screenshot the annotation refers to (basename from `target.source`).
2. Address the reviewer's comment about that image region:
   - If they request a retake, add a test step to capture a cleaner screenshot and update the file.
   - If they note a UI discrepancy, validate against the live app if possible, then update prose.
   - Do NOT edit the PNG pixel data; do NOT remove the screenshot.
3. If the referenced file is missing: log as ORPHANED.

### Orphaned annotations

Log each orphaned annotation in your resolution summary with:

    ORPHANED: <annotation-id> — <reason>

Leave these unchanged.

## Steps

1. Read `articles/<slug>/final.md` and `.ghostwriter/feedback/<slug>.json`
   (VM path: `/home/ubuntu/ghostwriter-feedback/<slug>.json`).
2. For each annotation, classify selector type and resolve per the rules above.
3. After all resolutions, run the voice pass to re-enforce style:
   ```
   python writer/run_claude_code.py --article <slug> --phase voice-pass
   ```
   The voice pass (04a-voice-pass.md) applies STYLE_GUIDE.md §2.4, §3, §10, §13, §13a, §14.
4. Re-render HTML previews (ALWAYS — even prose-only changes):
   ```
   python3 pipeline/render_html.py articles/<slug>/
   ```
   This writes `<slug>.html` AND `<slug>-zendesk.html`.
5. Regenerate the index:
   ```
   python3 pipeline/build_index.py
   ```

6. Clear the feedback store for this slug so resolved annotations do not linger
   or re-trigger a second revision cycle:
   ```python
   import json, os, pathlib
   fb_dir = os.environ.get("GHOSTWRITER_FEEDBACK_DIR") or "/home/ubuntu/ghostwriter-feedback"
   pathlib.Path(fb_dir, "<slug>.json").write_text("[]\n")
   ```
   (On local dev the path is `.ghostwriter/feedback/<slug>.json` — set
   `GHOSTWRITER_FEEDBACK_DIR` accordingly or use `feedback_store.write_feedback`.)
   Orphaned annotations are recorded in the resolution summary above and do not
   need to be re-resolved; they should be cleared here along with the resolved ones.

## State transitions

After all annotations are resolved:

- Text-only changes (no test-plan steps modified) → set `PHASE=FINALIZING`
  (voice-pass then sets `PHASE=PR_OPEN` when it opens the revision PR)
- Test-plan steps added or changed → set `PHASE=TESTING`
- Blocked / ambiguous and nothing committed → set `PHASE=BLOCKED`

Always preserve existing `REVISION_CYCLE` and `FEEDBACK_ISSUE` values in STATE.
Do NOT reset `REVISION_CYCLE` to 0.

## Commit format

Two commits (same rule as WORKFLOW.md §9.5):

1. If any canonical source was updated (style guide, glossary, taxonomy):
   ```
   docs(canon): feedback on <slug> — <summary>
   ```

2. Article + renders + index:
   ```
   fix(article): revise <slug> from feedback (cycle N) — <5-word summary>
   ```
   where N is the current REVISION_CYCLE value.

## Final output

Print a resolution summary:

```
RESOLVED
Context: Applied N annotations (<n> text, <n> image-region), <n> orphaned. <one-line summary>.
```

Or if blocked:

```
NEEDS_HUMAN
Reason: <description of what could not be resolved automatically>
```
