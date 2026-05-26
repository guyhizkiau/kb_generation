# Prompt: 02-research

You gather all inputs needed to draft an article. This prompt runs
**before** drafting, and produces four research files plus a canon
read. The drafter (prompt 03) consumes everything you produce.

## Inputs

- The article's plan entry in `editorial/ARTICLES_PLAN.md` (find by title)
- The cluster scenario file `clusters/<cluster-id>/SCENARIO.md`
- Read access to `references/internal/`, `references/competitors/`,
  `~/specterx-codebase/`, and `canon/`
- Browser Tab tool for online research
- Playwright + CDP for UI reconnaissance

## Outputs

Four files in `articles/<NN-slug>/research/`:

1. `internal-sources.md`
2. `codebase-findings.md`
3. `competitor-coverage.md`
4. `ui-snapshot/` directory with `ui-glossary.md` + screenshots

Plus an updated `STATE`:
```
PHASE=DRAFTING
LAST_UPDATE=<ISO>
NEXT_ACTION=consume research/, write draft-1.md
```

## Procedure

The four operations can run in any order — they don't depend on each
other. Do them in parallel if your environment supports concurrent
work; otherwise sequentially in this order, which puts the
fastest/cheapest first.

### Step 1 — Canon check (always first)

Before doing any research, read `canon/DO_NOT_DOCUMENT.md`. Grep for
the article title and any synonyms. If matched:

1. Update `STATE` to `PHASE=SKIPPED` with `BLOCKED_REASON=<reason from
   DO_NOT_DOCUMENT>`
2. Stop. Do not produce research files. Do not draft.
3. Log this to the cluster's STATE so the orchestrator can move on.

### Step 2 — Internal sources

Grep `references/internal/` for the article topic. Use keywords from
the plan entry's "Topics to cover" bullets, not just the title.

For each match:
- Extract relevant sections (a few lines around the match)
- Paraphrase; do not paste large quotes
- Cite the source file and line numbers

Write `internal-sources.md` per the format in WORKFLOW.md §6.1.

If no matches: write a single line "No internal sources found for this
topic. Drafting will rely on codebase findings and UI reconnaissance."
Move on; this is fine.

### Step 3 — Codebase reconnaissance

Search `~/specterx-codebase/web-client/` and
`~/specterx-codebase/admin-web-client/`. Use these patterns:

**For UI strings** (the most important output):
```bash
# Match the feature area; use multiple keywords from the plan entry
cd ~/specterx-codebase/web-client
grep -rn "share\|permission\|policy" src/locales/ | head -50
```

Goal: harvest the *exact* labels used in the UI. These become the
canonical terms used in the article. If the i18n key is
`share_dialog.recipient_field.placeholder` → `"Add people by email"`,
the article says "the **Add people by email** field", not "the
recipient field."

**For feature flags**:
```bash
grep -rn "FEATURE_\|feature_flag\|featureFlag\|isEnabled" src/ | \
  grep -i "<article-topic-keyword>"
```

Goal: identify if any part of the flow is gated. If yes, the article
needs to say "If you don't see X, your tenant may not have this
feature enabled."

**For error messages** (input to the troubleshooting section):
```bash
grep -rn "error\|Error\|errorMessage\|ErrorBoundary" src/components/ | \
  grep -i "<article-topic>" | head -30
```

Extract the actual text shown to users. Quote it in the article inside
backticks: `` "You don't have permission to share this file." ``

**For routes / adjacent flows**:
```bash
grep -rn "Route\|<Route" src/routes/ | grep -i "<topic>"
```

Goal: discover related flows that might affect the article (e.g. a
"share" route might lead to a "share-status" route).

**For recently-modified files** (UI-drift risk):
```bash
git -C ~/specterx-codebase/web-client log --since="90 days ago" \
  --name-only --pretty=format: -- "src/components/<TopicArea>/" | \
  sort -u | head -20
```

If multiple files in the relevant component tree changed recently,
flag the article as `ui-drift-risk: high` in the front matter of
`codebase-findings.md`.

Write `codebase-findings.md` per WORKFLOW.md §6.2.

**Hard rules for codebase work:**
- Only read; never modify, commit, or push
- Never paste source code blocks into article drafts. UI strings and
  error text are not source code. Component names, function names,
  and code logic are.
- If you find sensitive content (API keys committed by mistake,
  customer data in test fixtures, employee names in code comments),
  do not include them in `codebase-findings.md`. Log them in a
  separate `articles/<NN-slug>/research/_redacted-from-codebase.md`
  that's gitignored, and flag for Guy.

### Step 4 — Competitor coverage

Procedure described in WORKFLOW.md §6.3. Cache-first:

1. Open `references/competitors/INDEX.json`. Match keywords from the
   article title and plan entry against the `topics` field of cached
   entries.

2. **If 2+ matches across different vendors**: use the cached
   versions. Skip online scraping. Note in `competitor-coverage.md`
   which entries you used.

3. **If insufficient matches**: scrape. For each vendor in this
   priority order (most relevant first):

   - **Egnyte** for file-share UX
   - **Virtru** for email protection and Outlook
   - **DocSend (Dropbox)** for recipient-side and watermarking
   - **Vera** for rights management and policy
   - **HubSpot** for general KB writing patterns

   Scraping procedure:
   - Open the vendor's base URL in the VM Chrome via Browser Tab
   - Use the site's own search (look for the search box; URL patterns
     vary)
   - Click into the most relevant result for this article's topic
   - Wait for full page render (some KBs lazy-load)
   - Capture both raw HTML and a Markdown extraction:
     - Save HTML: use the browser tool to dump page source to
       `references/competitors/<vendor>/_raw/<slug>-<date>.html`
       (gitignored, kept for evidence)
     - Save Markdown: convert with html2text or similar, to
       `references/competitors/<vendor>/<slug>.md` with front matter:
       ```yaml
       ---
       source_url: <URL>
       captured: <ISO date>
       captured_by: bot
       title: <original title>
       ---
       ```
   - Update `references/competitors/INDEX.json` with the new entry's
     topics, vendor, slug, path, captured date

4. **Extract a coverage checklist** from what you scraped or pulled
   from cache. Per WORKFLOW.md §6.3, the output is a checklist of
   "things they thought worth covering" plus a few "patterns NOT to
   copy" — never a copy of their words.

5. **Decide coverage gaps**: compare the checklist to the plan
   entry's "Topics to cover" list. If competitors covered things our
   plan didn't, note them as proposed additions for Guy to decide on
   in PR review.

### Step 5 — UI reconnaissance

Use Playwright over CDP to open the relevant SpecterX surface in the
VM Chromium (which is already signed in as Guy).

Procedure:
1. Navigate to the entry point for the article's flow
2. Don't execute the flow — just observe the starting state
3. Open and close any menus or dialogs the flow will involve
4. Capture full-viewport screenshots of each state to
   `ui-snapshot/00-<state>.png`, `01-<state>.png`, etc.
5. For each captured state, read the accessibility tree and extract
   labels into `ui-glossary.md`

Format for `ui-glossary.md`:

```markdown
# UI glossary — <article title>
# Captured: <ISO timestamp>
# SpecterX build: <fetched build identifier>
# Browser: Chromium <version>
# Viewport: 1440×900

## Surface: <Page name>

### Top-level navigation
- (left-rail items, top-bar items — exact labels)

### Main panel
- (page-specific labels)

### Dialogs / modals used in this flow
- (per dialog: title, button labels, field placeholders, dropdown
  options)
```

After writing the glossary:
1. Diff against `canon/GLOSSARY.md`. List any new terms at the bottom
   of `ui-glossary.md` under `## Proposed glossary additions`.
2. Flag any terms in the canon that don't match what you saw in the
   UI (might mean UI drift or stale canon).

### Step 6 — Canon read (final, before drafting)

Load into context (no output file):

1. `canon/STYLE_GUIDE.md` if it exists
2. `canon/GLOSSARY.md`
3. The last 3–5 approved articles in this section, or globally if
   fewer than 3 in this section

Read fully. The drafter is supposed to write in the style and
vocabulary established by these articles. Do not skim.

## Done condition

All four research files exist and have content (or a documented
"nothing found" line). The canon has been read. Update STATE and
exit.

---

## Notes on cost

This stage is the most token-expensive of the pipeline. The codebase
search can pull a lot of context. To stay under budget:

- Limit each grep result to the first ~30 matches. Don't load entire
  files unless you need to.
- For competitor scraping, cache aggressively. Re-scraping the same
  vendor page 10 times across articles is waste.
- For UI recon, capture screenshots but only read the accessibility
  tree (don't dump the whole DOM).

If this stage looks like it'll exceed $2 in tokens for a single
article, stop, log to STATE as `BLOCKED reason=research-cost-spike`,
and surface to Guy.
