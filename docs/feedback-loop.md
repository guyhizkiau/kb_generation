# KB Feedback Loop — Design Plan

> Status: **proposed** (design note for circulation, not yet implemented).
> Branch: `claude/article-review-workflow-zfpF7`.
> Authentication (e.g. Google SSO via `oauth2-proxy`) is intentionally
> **out of scope** for this version of the plan — see
> [Deferred / open](#deferred--open-decisions).

## Goal

Let more people — non-technical SMEs included — review KB articles:

- comment on **specific lines and image regions**, not just whole pages;
- review **already-merged** articles as well as in-flight ones;
- have accepted feedback **automatically re-enter the pipeline** as a new
  revision PR.

## Problem with today's flow

All feedback runs through GitHub PR comments, which leaves two hard gaps:

- **Identity** — SMEs won't open PRs or leave inline review comments.
- **Lifecycle** — the state machine terminates at `MERGED`; a merged
  article has no open PR to comment on and no path back in.

## Backbone

```
   CAPTURE (anchored, on-page)        ROUTE (n8n hub)            STORE / TRIAGE            RE-ENTRY (VM daemon)
 +--------------------------+  W3C  +----------------+  one    +------------------+ enqueue +--------------------+
 | article page (all states,| anno- | WF1 intake:    | issue/  | Issue per article |        | pr-watcher control |
 | incl. MERGED)            | tation|  normalize     | thread  |  = review thread  |        | plane /enqueue-    |
 | - select line -> comment  | JSON  |  selector ->   |-------->|  - quoted text    |        | revision           |
 | - box screenshot -> comment|--POST>|  human text +  | create  |  - image thumbnail| picks  | -> revise-from-    |
 | RecogitoJS + Annotorious  |       |  raw JSON      |         |  + ```json block  |  up    |   feedback phase   |
 +--------------------------+       |  + Slack ping  |         |  labels: slug,    |  via   | -> voice-pass      |
        ^ existing annotations       |                |<--------|  feedback, status |  WF2   | -> render -> new PR |
        +--- n8n read-back by slug ---+ WF2 trigger:  | accepted +------------------+        +--------------------+
                                      |  on accepted   |  label                                       |
                                      |  -> /enqueue   |                            existing review -> merge ->
                                      +----------------+                            re-paste Zendesk (PUBLISH_STALE)
```

## Component map — reuse vs. build

| Layer | Reuse (off the shelf) | Build (bespoke) |
|---|---|---|
| Line/text annotation | **RecogitoJS** — select prose → comment; emits W3C `TextQuoteSelector` + `TextPositionSelector` | — |
| Image-region annotation | **Annotorious** — draw a box on a screenshot → comment; emits `FragmentSelector` (`xywh=`) | — |
| Whole-page / general comment | same libs, page-level target | — |
| Capture host | the existing rendered article pages | inject both `<script>`s into the template in `pipeline/render_html.py` |
| Route form→issue + read-back | **n8n** (self-hosted) — two workflows | the two workflow definitions (exported JSON) |
| Store | **GitHub Issues** (one "review thread" issue per article) | — |
| Triage queue | **GitHub Projects** board (`new → accepted → in-revision → done`) | — |
| Re-entry trigger | n8n WF2 on `issues.labeled == accepted` | small `/enqueue-revision` endpoint on the existing control plane |
| Claude execution | the existing `pr-watcher` daemon (PTY + stream-json + watchdog) | a third action type in its main loop |
| Revise phase | the existing `voice-pass` + render + PR + merge flow | **`pipeline/prompts/06-revise-from-feedback.md`** + `--phase revise-from-feedback` |

### Design choices that fell out of this

- **W3C Web Annotation is the backbone format.** The selector (quoted text
  / image `xywh`) flows all the way into the revise prompt, so Claude
  resolves *"this exact sentence"* or *"this region of `step-3.png`"*
  rather than "somewhere on the page." More robust than GitHub PR line
  comments — text-quote anchors survive reflow; line numbers don't.
- **GitHub Issues as single source of truth.** Each annotation lands in a
  per-article review-thread issue as both a human-readable block (quoted
  text, or a thumbnail with the box drawn) and a fenced ` ```json ` block
  with the raw selector. On page load, n8n reads open `slug:NN` issues and
  returns the JSON so prior annotations **re-anchor on the page** — that's
  what makes it real multi-person review (see others' comments, avoid
  dupes, reply). Fallback only if this proves clunky: a per-slug JSON file
  on the VM.
- **n8n = integration/eventing; pr-watcher = Claude execution.** n8n never
  runs Claude; it only talks to forms/GitHub/Slack and enqueues work. The
  VM daemon reuses its proven Claude harness.
- **Triage gate.** Accepted feedback auto-re-enters, but only issues
  carrying the **`accepted`** label do — one cheap human (or
  trusted-group) click prevents duplicate / "+1" / disagreement noise from
  spawning branches against the one-article-at-a-time cadence.

## Re-entry into the pipeline (bespoke pieces)

1. **`/enqueue-revision {slug, issue}`** — a thin addition to the control
   plane (already listens on `127.0.0.1:9191` with `/poll-now`, `/retry`).
   Appends a job; the daemon's main loop gains a third action type beside
   open-PR and merged-PR handling. No new Claude-execution code.
2. **`pipeline/prompts/06-revise-from-feedback.md`** — a near-clone of
   `04-revise-from-pr-comments.md`, swapping the input source to the issue
   body + its annotation JSON. Resolves a `TextQuoteSelector` against
   `final.md` (exact quote → exact line) or an `xywh` box against the named
   file in `articles/NN-slug/screenshots/` (the renderer already maps each
   `<img src>` to its repo screenshot path). Same hard rules +
   `editorial/STYLE_GUIDE.md` constraints, followed by the existing
   `voice-pass`.
3. **State-machine cycle** (`WORKFLOW.md §11`): add
   `MERGED → (accepted feedback) → REVISING → FINALIZING → PR_OPEN → MERGED`,
   with new `STATE` fields `REVISION_CYCLE`, `FEEDBACK_ISSUE`, and
   `PUBLISH_STALE=true` on re-merge. Guard `trigger_next_article()` on
   `REVISION_CYCLE == 0` so a re-merge doesn't kick the next cluster
   article. Surface `PUBLISH_STALE` on the dashboard so the manual Zendesk
   re-paste isn't forgotten.

## n8n workflows

- **WF1 — Intake:** annotation `POST` → normalize selector → search open
  issues for `slug:NN` + dedupe → if dup, add a "+1 / additional note"
  comment; else create the review-thread issue (labels `article-feedback`,
  `slug:NN-slug`, `status:new`) with human block + raw JSON → Slack ping to
  a triage channel with an Approve link. Also serves the **read-back**
  (return annotations JSON for a slug on page load).
- **WF2 — Trigger:** GitHub trigger on `issues.labeled == accepted` →
  `POST /enqueue-revision` → comment queued status on the issue → move the
  Project card to *in-revision*.

## Phasing

| Phase | Ships | Standalone value |
|---|---|---|
| **1 — Annotate + capture** | RecogitoJS + Annotorious in `render_html.py`; n8n WF1 → per-article Issue (text + image, anchored) | SMEs leave precise, anchored feedback on any article incl. merged |
| **2 — Collaborative display** | n8n read-back so existing annotations re-anchor on load | true multi-reviewer experience |
| **3 — Re-entry** | `06-revise-from-feedback.md` + selector resolution, `/enqueue-revision`, state cycle, n8n WF2 | accepted → automatic revision PR |
| **4 — Polish** | Projects board, `PUBLISH_STALE` dashboard flag, dedupe, Slack triage | closes loop + Zendesk drift safety |

**Cheapest proof of concept:** RecogitoJS + Annotorious on a single
already-rendered article page, no backend — validates the SME annotation
UX before any infra goes up.

## Deferred / open decisions

- **Authentication** — set aside for now. Google SSO via `oauth2-proxy`
  was the leading option; it would also gate the currently-open
  `18.192.122.48` browser, but it's orthogonal to this design and can be
  layered into Phase 1 later.
- **Re-paste to Zendesk** stays manual; `PUBLISH_STALE` is the safety
  flag, not automation.
- Whether triage `accepted` is one person (Guy) or a trusted group.

## Alternatives considered (and why not)

- **Giscus / Utterances** — canonical OSS "comments on a static site,"
  but both require a *GitHub* login and neither does image-region
  annotation. Out for non-technical SMEs + the image requirement.
- **Hypothesis (self-hosted `h`)** — full annotation product, but
  text/page-centric with weak image-box support, so screenshots wouldn't
  be covered; you'd end up running it *plus* Annotorious anyway.
  RecogitoJS + Annotorious (same family, one shared layer) is lighter.
- **Formbricks / Tally form** — fine for whole-page feedback, but a survey
  tool can't anchor to a text selection or image box. Obsoleted by the
  line/image-level requirement.
