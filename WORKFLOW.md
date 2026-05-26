# WORKFLOW.md — SpecterX KB Article Pipeline

> **Read this fully before writing any article.** This document is the
> authoritative spec for how the pipeline produces articles. It supersedes
> any earlier handoff document.
>
> You are a Claude Code instance running on the EC2 Windows VM, inside
> WSL2 Ubuntu. You have hands on: the SpecterX web tenant (via Chromium
> with CDP), the SpecterX desktop apps (via computer-use), git, gh,
> Bitbucket repos, and the local filesystem.

---

## 1. The big picture

You are producing 109 knowledge-base articles across 11 sections, listed
in `editorial/ARTICLES_PLAN.md` (already in this repo). Each article is the
output of a 5-stage pipeline:

```
Stage 0  ─►  Stage 1   ─►  Stage 2   ─►  Stage 3  ─►  Stage 4  ─►  Stage 5
once       per-cluster   per-article    draft       validate    PR + review
                         (parallel)
```

- Stage 0 is **done once** at project start
- Stage 1 is **done once per cluster** (a cluster is up to 5 articles)
- Stages 2–5 are **done per article**

There is no pre-existing house style. **You build the style as you go**,
from approved articles. The first 3 approved articles establish it; the
first 8 settle it; everything after extends it.

The 4 "POC articles" in the plan marked `(POC — live)` are AI-generated
prototypes from an earlier attempt. **Do not use them as style references.**
Treat them as if they don't exist for purposes of canon. They will be
rewritten later as regular articles.

---

## 2. Repository layout

Initialize the GitHub repo `specterx/specterx-knowledge-base` (confirm
the org with Guy on first run; it might be `specterx-cloud` or similar)
with this structure:

```
specterx-knowledge-base/
├── README.md
├── WORKFLOW.md                      # this document (copy from bootstrap)
├── CLAUDE.md                        # short workflow rules for any
│                                    # Claude Code session
├── editorial/
│   └── ARTICLES_PLAN.md             # the queue (already exists)
│
├── canon/                           # the growing house style
│   ├── STYLE_GUIDE.md               # empty until article 5
│   ├── GLOSSARY.md                  # grows per article
│   ├── DO_NOT_DOCUMENT.md           # pre-seed from Deferred list +
│                                    # add as you discover
│   └── COMPETITOR_PATTERNS.md       # appears around article 5–10
│
├── clusters/
│   ├── PLAN.md                      # the order: which cluster, when,
│                                    # in what order
│   ├── 01-login/
│   │   ├── SCENARIO.md              # how to set up the test world
│   │   ├── articles.txt             # article slugs in this cluster
│   │   └── STATE                    # cluster state: NOT_STARTED |
│                                    # SCENARIO_READY | IN_PROGRESS |
│                                    # COMPLETE
│   └── 02-share-files/
│       └── ...
│
├── articles/
│   └── 01-login-to-specterx/
│       ├── STATE                    # article state machine
│       ├── research/
│       │   ├── internal-sources.md
│       │   ├── codebase-findings.md
│       │   ├── competitor-coverage.md
│       │   └── ui-snapshot/
│       │       ├── ui-glossary.md
│       │       └── *.png            # raw UI recon screenshots
│       ├── draft-1.md
│       ├── test-plan.json
│       ├── test-notes.md
│       ├── draft-2.md
│       ├── final.md                 # the deliverable
│       └── screenshots/
│           ├── 01-*.png             # final screenshots used in article
│           └── _all/                # unfiltered captures from testing
│
├── references/
│   ├── internal/                    # SpecterX docs the bot has digested
│   │   ├── INDEX.md
│   │   └── *.md                     # one per ingested source doc
│   ├── codebase/                    # findings from grep-the-codebase
│   │   ├── INDEX.md
│   │   └── *.md                     # one per article that did codebase work
│   └── competitors/
│       ├── INDEX.json               # search index
│       ├── hubspot/
│       │   └── <slug>.{html,md}     # cached with date stamp
│       ├── egnyte/
│       ├── vera/
│       ├── docsend/
│       └── virtru/
│
├── assets/
│   ├── files/                       # test files for all flows
│   │   ├── quarterly-report.pdf
│   │   ├── vendor-contract.docx
│   │   ├── sales-data.xlsx
│   │   ├── product-mockup.png
│   │   └── archive-sample.zip
│   ├── users/
│   │   └── README.md                # external recipient addresses,
│                                    # test SpecterX accounts
│   └── workspaces/
│       └── README.md                # standard workspace setups
│
├── orchestrator/                    # the polling loop
├── writer/                          # claude -p wrappers
├── tester/                          # Playwright + computer-use
├── pipeline/
│   └── prompts/                     # the prompts you call
└── infra/                           # systemd, cron, scripts
```

---

## 3. External dependencies you need to set up first

Before writing article 1, you need three external things working. Verify
each, and stop and ask Guy if any fail.

### 3.1 Bitbucket codebase access

You need read access to two SpecterX repos for Stage 2b (codebase
reconnaissance):

- `git@bitbucket.org:specterx/web-client.git` — the end-user-facing
  SpecterX web app
- `git@bitbucket.org:specterx/admin-web-client.git` — the SpecterX admin
  console

**Setup procedure** (you do this once on first run; Guy completes step 3):

1. Generate two ed25519 keypairs (one per repo) without a passphrase:
   ```bash
   mkdir -p ~/.ssh/specterx-deploy
   ssh-keygen -t ed25519 -N "" -f ~/.ssh/specterx-deploy/web-client \
     -C "specterx-kb-bot@<vm-hostname>-web"
   ssh-keygen -t ed25519 -N "" -f ~/.ssh/specterx-deploy/admin-web-client \
     -C "specterx-kb-bot@<vm-hostname>-admin"
   ```

2. Configure SSH to use the right key per host:
   ```
   # ~/.ssh/config
   Host bitbucket.org-web-client
     HostName bitbucket.org
     User git
     IdentityFile ~/.ssh/specterx-deploy/web-client
     IdentitiesOnly yes

   Host bitbucket.org-admin-web-client
     HostName bitbucket.org
     User git
     IdentityFile ~/.ssh/specterx-deploy/admin-web-client
     IdentitiesOnly yes
   ```

3. **Stop. Ask Guy to add both public keys as read-only Access Keys** in
   Bitbucket:
   - Print both `~/.ssh/specterx-deploy/*.pub` to the console
   - Tell Guy: "Open Bitbucket repo settings → Access keys → Add key.
     One key per repo. Set permission to read-only. Paste the .pub
     contents. The keys must be read-only — you should never have
     write access to these repos."
   - Wait for Guy to confirm before continuing.

4. Clone both repos to `~/specterx-codebase/`:
   ```bash
   git clone git@bitbucket.org-web-client:specterx/web-client.git \
     ~/specterx-codebase/web-client
   git clone git@bitbucket.org-admin-web-client:specterx/admin-web-client.git \
     ~/specterx-codebase/admin-web-client
   ```

5. Set up a daily `git pull` cron in WSL2 so the codebase stays fresh:
   ```bash
   (crontab -l 2>/dev/null; echo "0 6 * * * cd ~/specterx-codebase/web-client && git pull --ff-only && cd ~/specterx-codebase/admin-web-client && git pull --ff-only") | crontab -
   ```

**Hard rule on the codebase:** you have **read-only** access. Never push,
never commit, never modify anything in `~/specterx-codebase/`. Treat it
as a search corpus. If you find a bug or typo while grepping, log it in
an issue on the KB repo as `codebase-observation-NN.md`; do not file
issues against the codebase repos.

### 3.2 GitHub repo for the KB

Initialize `specterx/specterx-knowledge-base` (private). Push the
structure from §2 with empty placeholders. Add a `.gitignore` covering:
- `**/_all/` (unfiltered screenshots — too many, too noisy)
- `**/.env` and `**/secrets`
- `references/competitors/**/_raw/` (raw HTML before cleanup)

### 3.3 SpecterX tenant access

The browser profile at `C:\specterx-kb\.chrome-profile` should already
be signed in to `app.specterx.com` as `guy@specterx.com`. Verify by
connecting Playwright over CDP and navigating to the dashboard. If the
session is expired, prompt Guy to RDP in and log in manually once; the
profile persists.

---

## 4. Stage 0 — One-time setup

Do these once, before any cluster.

### 4.1 Pre-seed `canon/DO_NOT_DOCUMENT.md`

From the plan's "Deferred until shipped" section (lines ~1901–1932),
extract every candidate article title. Each becomes a "do not write
this yet" entry with the reason from the table. Example format:

```markdown
# Do not document

Articles that look documentable but should not be written yet.

## Deferred features (from plan v2)

- **Email body encryption via Platform Governance Rule** — not shipped in V1
- **Lock Policies as a standalone feature** — superseded by PAR
- **Workspaces / Slack enforcement via PAR** — not shipped in V1
- (continue for the full deferred list)

## Internal-only flows discovered during research

(empty; you'll add to this as you discover things in the codebase that
shouldn't be public)
```

Before drafting any article, grep this file for the article title or
its subject matter. If matched, skip the article and log it in the
cluster's STATE file as `skipped: do-not-document`.

### 4.2 Assets library

Create the standard test files in `assets/files/`:

- `quarterly-report.pdf` — a 3-page PDF, generic content ("Acme Corp
  Q3 2025 Sales Report" or similar). Generate with a small script;
  don't use a real document. Watermarkable, viewable.
- `vendor-contract.docx` — a 2-page Word doc, generic contract text
  with placeholders.
- `sales-data.xlsx` — a 3-sheet workbook with fake quarterly data.
- `product-mockup.png` — a 1920×1080 placeholder image with a label
  "Confidential — Product Mockup."
- `archive-sample.zip` — a zip containing two of the above files.

Document the cast of test users in `assets/users/README.md`:
- Primary sender: `guy@specterx.com` (Guy's working account)
- External recipient 1: a real external address Guy controls, used for
  flows that need recipient-side verification. Ask Guy for which
  address to use.
- External recipient 2: same, for multi-recipient flows.
- Internal collaborator: another `@specterx.com` account if Guy has
  one available, or skip until needed.

Do not commit credentials for these accounts. Reference them by name
("external recipient 1") in articles and test plans, and resolve names
to addresses via `.env` at runtime.

### 4.3 Cluster plan

Generate `clusters/PLAN.md`. Read the full `editorial/ARTICLES_PLAN.md` and
group articles into clusters following these rules:

1. **Hard cap of 5 articles per cluster.**
2. Articles in the same cluster share a scenario (a state of the
   SpecterX tenant) so we set up the world once per cluster.
3. Reference / compliance articles (HIPAA, GDPR, SOC2, release notes,
   capability limits) form their own clusters without a scenario.
4. Cross-cluster dependencies: if cluster B requires that cluster A's
   articles be approved (because B references concepts A defines), list
   the dependency.
5. Order: cluster 1 first, then expand outward.

Cluster 1 is **predetermined**: see §5 below. Plan everything from
cluster 2 onward.

### 4.4 Initialize the canon

Create empty `canon/STYLE_GUIDE.md`, `canon/GLOSSARY.md`,
`canon/COMPETITOR_PATTERNS.md`. They get populated later.

---

## 5. Stage 1 — The first cluster

**Cluster 1 is special.** It's the only cluster you handle one article
at a time, with a deliberate review pause after the third article. No
parallelism, no batching.

### 5.1 What's in cluster 1

Three login articles, in this exact order:

1. **Log in to the SpecterX web platform** (anchor — establishes the
   procedural skeleton)
2. **Set or reset your password** (parallel structure to article 1,
   surfaces variations)
3. **What is SpecterX?** (intentionally different: an overview
   article, not a procedural one — establishes the style for overview
   articles)

After all three are approved and merged, **stop**. Do not start
cluster 2. Run the style extraction (§9) and wait for Guy to confirm
he's happy with `STYLE_GUIDE.md`. Only then continue to cluster 2.

### 5.2 Cluster 2

Pre-planned to be the 5-article Share files cluster:

1. Share a folder
2. Set recipient permissions
3. Update permissions after sharing
4. Revoke access to a shared file
5. Set how long a file stays accessible

Cluster 2 is your first batch — write all 5 in parallel (within bot
limits), open 5 PRs.

### 5.3 Scenario setup for cluster 1

Write `clusters/01-login/SCENARIO.md`:
- The browser starts logged out (open an incognito CDP context, or
  clear the test profile cookies before each article's test)
- Guy's credentials in `.env`
- For "Set or reset your password": Guy needs to trigger a password
  reset email for himself once; you cannot actually reset his real
  password mid-flow. Document this limitation in the test plan and
  capture the visible flow only up to the email-arrived stage.

### 5.4 Scenario setup for cluster 2

Write `clusters/02-share-files/SCENARIO.md`:
- Logged in as `guy@specterx.com`
- A test folder named `KB Test — Share Files` exists in My Files
- The folder contains `quarterly-report.pdf` and `vendor-contract.docx`
  (copies of the assets)
- An external recipient address is available for sharing
- After each article's test, the folder is restored to this baseline
  (no leftover shares, no leftover recipients)

---

## 6. Stage 2 — Per-article research (parallel)

Five inputs gathered in parallel. None depends on the others.

### 6.1 Internal documentation scan → `research/internal-sources.md`

Grep `references/internal/` for the article topic. Match by keywords
from the plan entry. Output a notes file:

```markdown
# Internal sources — <article title>

## Source: PRD-share-permissions-v2.md
**Provenance:** references/internal/PRD-share-permissions-v2.md, lines 47–82
**Relevance:** Defines the three permission levels (Viewer, Contributor,
Co-Owner) and their interactions with the active policy.

Key facts:
- Contributor can view + upload + download (subject to policy)
- Viewer is read-only
- Co-Owner can manage permissions and sub-shares

(quote sparingly; paraphrase liberally; always cite line numbers)
```

If `references/internal/` is empty for this topic, write a one-line
note `no internal sources found` and move on. **Do not invent sources.**

When Guy provides a new set of internal docs (he'll dump them in
`references/internal/_inbox/` periodically), process them: extract
title, topic, date, save to `references/internal/<slug>.md`, update
`references/internal/INDEX.md`.

### 6.2 Codebase reconnaissance → `research/codebase-findings.md`

Grep `~/specterx-codebase/web-client/` and `~/specterx-codebase/admin-web-client/`
for the article topic. Useful patterns:

- **UI strings** (in i18n files, button labels): `grep -r "Share" web-client/src/locales/` —  tells you what the button is *actually* labelled
- **Feature flags**: `grep -r "FEATURE_FLAG\|featureFlag\|isEnabled" web-client/src/`
  — tells you if the feature you're about to document is behind a flag
  not yet on for prod tenants
- **Route handlers**: where in the codebase the relevant route lives,
  to find adjacent flows you might also want to document
- **Error messages**: the actual text users see when things go wrong;
  these become your troubleshooting section
- **Recently modified files**: `git log --since="3 months ago" --name-only --pretty=format: web-client/src/components/Share/`
  — recently-modified code is high-risk for UI drift; flag the article
  for closer review

Output:

```markdown
# Codebase findings — <article title>

## UI strings (canonical labels)
- Share button: `web-client/src/locales/en.json:142` → "Share"
- Add recipients dialog title: `:143` → "Add recipients"
- Policy dropdown placeholder: `:148` → "Select a policy"

## Feature flags affecting this article
- `FEATURE_DIGITAL_SIGNATURE` (used in `web-client/src/...:line`) —
  gates the Digital Signature option in the policy dropdown. Off by
  default. **Note in the article: "If you don't see Digital Signature,
  it's not enabled for your tenant."**

## Adjacent flows worth knowing about
- (links to related code paths that might inform the article)

## Error messages
- "You don't have permission to share this file" — shown when ...
- (these go in troubleshooting)

## Recently modified (last 90 days)
- `web-client/src/components/Share/ShareDialog.tsx` — 14 commits in
  last 90 days. **UI may have shifted; double-check screenshots.**
```

**Code-leak safety**: do not paste source code verbatim into article
drafts. Only the *outputs* of the code (UI strings, error text,
behavior) belong in the article. Code goes in `codebase-findings.md`,
never in `draft-1.md`. Before any commit, run the pre-commit hook
that scans for likely code leaks (regex: lines containing both `=>`
and at least one paren — common signal of pasted JS).

### 6.3 Competitor scan, cache-first → `research/competitor-coverage.md`

For each of these 5 reference KBs:

| Vendor | Base URL | What they're good at |
|---|---|---|
| HubSpot | https://knowledge.hubspot.com/ | General KB structure; how to write for non-technical end users |
| Egnyte | https://helpdesk.egnyte.com/hc/en-us/ | File sharing UX; closest direct competitor on share flows |
| Vera | https://docs.tricentis.com/vera-latest/content/home.htm | Rights management; policy-related articles |
| Dropbox DocSend | https://help.dropbox.com/share/ | Recipient-side UX; viewer/watermark articles |
| Virtru | https://support.virtru.com/hc/en-us | Email protection; Outlook/Gmail integration |

**Cache-first procedure:**

1. Check `references/competitors/INDEX.json` for cached articles
   matching this topic. Match by keyword (e.g. "watermark", "share
   folder", "verify recipient").

2. If 2+ cached matches across vendors exist: skip the online scrape,
   use the cached versions.

3. If you need to go online, **use the Browser Tab tool in the VM
   Chrome** (not curl, not requests). Reason: many KBs require JS
   rendering and lazy-load content. Procedure per vendor:
   - Navigate to the base URL
   - Use the site's own search for the article topic
   - Open the top 1–2 results
   - Wait for the page to fully render
   - Use the tester's "save current page" function to dump:
     - `references/competitors/<vendor>/<slug>.html` — raw HTML
     - `references/competitors/<vendor>/<slug>.md` — Markdown extraction
       via `html2text` or similar
     - Stamp with date in the front matter
   - Update `references/competitors/INDEX.json` with the new entry

4. Extract a coverage checklist from what you cached:

```markdown
# Competitor coverage checklist — <article title>

## What they thought worth covering

From HubSpot's "..." article (cached 2026-05-26):
- [ ] Prerequisite check (who can do this)
- [ ] Step-by-step with one screenshot per step
- [ ] What happens after (the "expected outcome" section)
- [ ] Troubleshooting

From Egnyte's "..." article (cached 2026-05-20):
- [ ] Permissions table at the top
- [ ] Note about how inheritance works
- [ ] "Note" callouts for security implications

From DocSend's "..." article (cached 2026-04-18):
- [ ] Use case framing at the top (when you'd want this)
- [ ] Visual emphasis on the security control

## Coverage gaps in our plan entry
- Egnyte mentions inheritance behaviour; our plan entry doesn't.
  Worth adding?

## Patterns NOT to copy
- HubSpot uses heavy marketing voice ("Empower your team to ..."); we
  don't.
```

**The output is a checklist, not a template.** Do not copy competitor
wording. Use the checklist as a prompt: "Did we cover this? Should we?"
The answer is sometimes no.

### 6.4 UI reconnaissance → `research/ui-snapshot/`

Open the relevant SpecterX surface via Playwright/CDP. Don't execute
the flow yet — just capture the starting state.

1. Navigate to where the article's flow begins (e.g. for "Share a
   folder", navigate to My Files)
2. Capture a full-viewport screenshot → `ui-snapshot/00-start.png`
3. Open any menus or dialogs the flow will use, capture each → `01-share-menu.png`, etc.
4. Read the accessibility tree to extract all visible labels into
   `ui-snapshot/ui-glossary.md`:

```markdown
# UI glossary — <article title>
# Captured: 2026-05-26T14:30:00Z
# SpecterX build: <fetched from /api/version or DOM>

## Page: My Files
- Top-right button: "Upload"
- Each file row's three-dot menu items: "Share", "Rename", "Move",
  "Delete"
- The Share dialog title: "Share <filename>"
- In the Share dialog:
  - Recipient field placeholder: "Add people by email"
  - Permission dropdown options: "Viewer", "Contributor", "Co-Owner"
  - Policy dropdown label: "Security policy"
```

5. Stamp every screenshot's filename with the date.

6. After capture, **diff** `ui-glossary.md` against `canon/GLOSSARY.md`:
   - Terms in both, same casing → fine
   - Terms in UI that aren't in canon → candidates to add to glossary
     (decide during stage 5)
   - Terms in canon that don't match UI → either the UI changed, or
     prior articles used wrong terminology. Flag for review.

### 6.5 Canon read

Load into context (no output file, just for drafting):

1. `canon/STYLE_GUIDE.md` — if it exists (article 6+)
2. `canon/GLOSSARY.md` — always
3. `canon/DO_NOT_DOCUMENT.md` — always; if this article matches an
   entry, STOP and mark the article as skipped
4. The last 3–5 approved articles in this section. Read their `final.md`
   files. If the section has fewer than 3 approved, supplement with the
   most recent approved articles from any section.

---

## 7. Stage 3 — Draft

Write `draft-1.md`. Consumes everything from stage 2 plus the plan entry.

### 7.1 Article skeleton (working hypothesis, may evolve from canon)

Until `STYLE_GUIDE.md` is generated, use this skeleton for procedural
articles:

```markdown
---
title: <Title>
audience: <end-user | admin | recipient | developer>
last-validated: <ISO date>
specterx-build: <build from UI recon>
estimated-reading-time: <N min>
prerequisites:
  - <prereq>
---

# <Title>

<One-paragraph intro: what this teaches, who it's for, what they'll
have at the end. Specific, concrete. No marketing.>

## Before you start

<Prerequisites as a bulleted list. Link to setup articles.>

## Steps

### 1. <Step name>

<What to do. Active voice, second person, one action per step.>

> Screenshot: <description of what should be shown>

### 2. <Step name>

...

## Troubleshooting

<2–5 common issues with fixes. Use error text from
codebase-findings.md when available.>

## What this article doesn't cover

<Explicit out-of-scope statements with links to other articles.
Reduces "but what about X" review comments.>

## Related articles

<3–5 links to related KB articles.>

---
*Last validated against SpecterX build <X> on <date>.*
```

For overview articles ("What is SpecterX?"), use a different skeleton:

```markdown
---
title: What is SpecterX?
audience: everyone
last-validated: <ISO>
specterx-build: <build>
---

# What is SpecterX?

<2–3 paragraph plain-language summary.>

## The problem SpecterX solves

<Concrete: what goes wrong without it.>

## The core concepts

### <Concept 1>
### <Concept 2>
### <Concept 3>

## What you can do with SpecterX

<3–5 bullets, each linking to a how-to article.>

## What SpecterX is NOT

<Important: what people assume it does but it doesn't.>

## Related articles

---
*Last reviewed <date>.*
```

### 7.2 Rules for the draft

- **One action per step.** Splitting is cheaper than merging.
- **Screenshot placeholders are mandatory** on every UI step. Be
  specific about what should be visible.
- **Active voice, second person.** "Click Share", not "the Share
  button should be clicked".
- **No marketing copy.** Compare every sentence: does it tell the
  reader what to do or know, or is it selling? Cut the second kind.
- **Use the canonical labels from `ui-glossary.md`**. If the UI calls
  it "Add recipients", do not write "Enter recipient emails."
- **Cite uncertainty explicitly.** If you don't know whether a button
  is named "Share" or "Send", and the UI recon didn't clear it up,
  write `[verify in test]` and move on.
- **Don't pad.** A 4-step article is 4 steps.
- **Apply the competitor coverage checklist** — for each item, decide
  in or out. Note your decisions briefly in the draft as `<!-- coverage
  decision: yes/no, reason -->` comments. These get stripped before PR.

### 7.3 After writing the draft

Update `articles/<NN-slug>/STATE`:
```
PHASE=TESTING
LAST_UPDATE=<ISO>
NEXT_ACTION=generate test-plan.json from draft-1.md
```

---

## 8. Stage 4 — Validate

Skip this stage entirely for articles flagged `validation: skipped`
(reference and compliance articles).

### 8.1 Generate `test-plan.json` from `draft-1.md`

Convert the draft into a machine-executable plan. See
`pipeline/prompts/02-test-plan.md` for the schema and rules.

### 8.2 Execute the plan

The tester runs each step:

- **Browser steps**: Playwright over CDP against the Windows Chrome
- **Desktop steps**: computer-use API driving the Windows desktop via
  the `win-action-server` on `localhost:9100`

For each step:
1. Execute the action
2. Wait for the expected state (up to 5s; longer for known-slow
   operations like uploads)
3. Capture screenshot to `screenshots/_all/<step-id>-<timestamp>.png`
4. Run the `verify` assertion from the test plan
5. Append observation to `test-notes.md`:

```markdown
## Step 01 — Click the Share button

- Action: click element matching "Share button in file row for
  quarterly-report.pdf"
- Result: SUCCESS
- Found element at: <accessibility tree path>
- Screenshot: _all/01-share-clicked-T1530.png
- Verify "A dialog titled 'Share' is visible": PASS
- Observations:
  - The dialog also shows a "Cancel" button (not mentioned in draft)
  - The recipient field is auto-focused (worth mentioning)
```

If a step fails:
- Capture a screenshot of the failure state
- Try to recover (e.g. close any unexpected modal, retry once)
- If recovery fails, mark the step `BLOCKED` and continue with the
  remaining steps that don't depend on it
- The final `test-notes.md` becomes the input to draft-2

### 8.3 Cleanup

Run cleanup steps from the test plan (delete uploaded files, revoke
shares, etc.) to leave the tenant in the cluster's baseline state.

---

## 9. Stage 5 — Revise, PR, review

### 9.1 Revise → `draft-2.md`

Use `pipeline/prompts/03-revise-from-test.md`. Reconcile `draft-1.md` with
`test-notes.md`. Replace screenshot placeholders with real images
from `_all/`, copying the chosen ones to `screenshots/` with clean
filenames.

### 9.2 Second pass (optional)

If the revisions changed the flow substantially, re-run the test plan
to capture final screenshots in the new order. If the revisions were
minor (wording, ordering of steps that don't affect screenshots), skip
this and use existing screenshots.

### 9.3 Produce `final.md`

Stamp the front matter with `last-validated: <ISO date>` and
`specterx-build: <build>`. Add the closing line `*Last validated
against SpecterX build <X> on <date>.*` at the very bottom.

### 9.4 Open PR

Create branch `article/<NN-slug>`, commit:
- `articles/<NN-slug>/final.md`
- `articles/<NN-slug>/screenshots/*.png` (only chosen ones, not `_all/`)
- `articles/<NN-slug>/test-notes.md` (for the reviewer)

PR body template:

```markdown
## Article NN: <Title>

Cluster: <cluster-id>
Validated against: SpecterX build <X>, <date>

### What this PR contains
- `articles/<NN-slug>/final.md` — the article
- `articles/<NN-slug>/screenshots/` — <N> images
- `articles/<NN-slug>/test-notes.md` — observations from execution

### Tests performed
<bulleted list of high-level flow stages with PASS / BLOCKED indicators>

### Coverage decisions
<from the competitor checklist; what was included or excluded and why>

### Glossary terms proposed
<new terms this article would add to canon/GLOSSARY.md>

### Known limitations
<from test-notes; anything that couldn't be verified>

### How to review
1. Read `final.md` end to end on the GitHub web view
2. For each screenshot, check it matches the step text
3. Leave inline comments on any step that's wrong, unclear, or wordy
4. Use "Request changes" to send revisions back to the pipeline
5. Approve and merge when ready
```

### 9.5 Process review feedback

When the PR gets "Request changes", read the comments, use
`pipeline/prompts/04-revise-from-pr-comments.md`. Push updates to the same
branch. Re-request review.

### 9.6 After merge

This is the key moment for canon growth:

1. **Add proposed glossary terms** from the PR description to
   `canon/GLOSSARY.md`. Commit on a separate branch
   `canon/glossary-update-after-NN-<slug>`, PR for fast approval.
2. **Check approved-article count.** If this is the 5th, 10th, 15th,
   ... approved article: run the style extraction (§10).
3. **Update the cluster STATE.** If all articles in the cluster are
   merged, mark cluster COMPLETE.
4. **Process any DO_NOT_DOCUMENT additions** the bot or reviewer
   identified.
5. **Update `references/competitors/INDEX.json`** if new vendor pages
   were scraped during this article's research.

---

## 10. Style extraction (every 5 approved articles)

Run via `pipeline/prompts/05-extract-style.md`. The bot reads every approved
`final.md`, extracts patterns, writes/updates `canon/STYLE_GUIDE.md`.

Pattern categories to extract:

1. **Voice** — first person? second? Tense? Tone (warm, neutral,
   crisp)? Sample sentences that exemplify it.
2. **Structural rhythm** — intro length, step format, ratio of prose
   to bullets, when to use callouts.
3. **Screenshot conventions** — when to screenshot, what to crop,
   when to annotate, caption format.
4. **Step format** — naming conventions, verb choices, lengths.
5. **Vocabulary** — which terms are canonical for which concepts
   (this feeds GLOSSARY.md too).
6. **What we explicitly don't do** — anti-patterns observed across
   PR comments ("we never say 'simply'", "we never start a step with
   'Now,'", etc.).
7. **Article archetypes** — by article 10–15, we should be able to
   identify 3–5 distinct skeletons: procedural how-to, overview/
   concept, reference table, troubleshooting, integration setup.

After the extraction runs, **open a PR with the updated
`STYLE_GUIDE.md` and wait for Guy's approval before continuing to the
next article.** The first style guide PR (after article 5) is the
most important review of the entire project. Guy should treat it as
making the editorial decisions for the next 100 articles.

---

## 11. The article state machine

Each article's `STATE` file tracks:

```
PHASE=<phase>
CLUSTER=<cluster-id>
LAST_UPDATE=<ISO>
NEXT_ACTION=<short description>
```

Phases (in order):
- `PLANNED` — in the plan but not yet started
- `RESEARCHING` — Stage 2 in progress
- `DRAFTING` — Stage 3 in progress
- `TESTING` — Stage 4 in progress
- `REVISING` — Stage 5.1 in progress
- `FINALIZING` — Stage 5.2 second test pass
- `PR_OPEN` — PR opened, awaiting review
- `PR_REVISION_NEEDED` — review requested changes
- `MERGED` — done, contributing to canon
- `BLOCKED` — waiting for human input (with `BLOCKED_REASON`)
- `SKIPPED` — matched DO_NOT_DOCUMENT (with reason)

---

## 12. Hard rules (never violate)

These are non-negotiable. Treat any conflict with them as a stop-and-ask.

1. **Never push to the codebase repos.** They're read-only references.
2. **Never paste source code into article drafts.** UI strings and
   error text are not source code; copy those freely.
3. **Never document a feature on the DO_NOT_DOCUMENT list.**
4. **Never invent UI elements or labels.** If you can't verify, write
   `[verify in test]` and let the tester resolve it.
5. **Never reproduce competitor article wording.** Use checklists,
   not templates.
6. **Never commit credentials, customer data, or content from
   `screenshots/_all/`** that wasn't moved to `screenshots/` after
   review.
7. **Never proceed past the cluster 1 review pause** without explicit
   approval from Guy on the first STYLE_GUIDE.md.
8. **Never make assumptions about cost.** If a single article costs
   more than $5 in API tokens, stop, log, and surface to Guy.

---

## 13. What to do when stuck

Order of escalation:

1. Re-read the relevant section of this document.
2. Check the last 3 approved articles for how a similar situation was
   handled.
3. Search `references/internal/` and `~/specterx-codebase/` for
   answers.
4. Post a question as a comment on the current PR (Guy will see it
   alongside the article).
5. If no PR is open yet, open a dedicated `pipeline-questions` issue
   on the KB repo.

Do **not**: improvise on infrastructure, change the workflow defined
here without a PR to this document first, or write articles that
contradict the canon without flagging it.
