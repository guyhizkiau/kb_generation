# ARTICLES_PLAN_V2.md

The pipeline queue. Distinct from `ARTICLES_PLAN.md` (the legacy /
research plan for the reference-library project).

Each entry is one row that the orchestrator picks up. The orchestrator
walks this file top-to-bottom, claims the first entry whose `status` is
`PLANNED`, creates a working directory at
`workspace/articles/NN-slug/`, and runs the pipeline.

## Schema

```
NN. <title>
  status:      PLANNED | DRAFTING | TESTING | REVISING | FINALIZING | PR_OPEN | DONE | BLOCKED
  audience:    admin | end-user | developer
  intent:      <one-sentence statement of what the article teaches>
  scope:       <one-sentence statement of what's in and out>
  sources:     <optional list of paths under sources/ or kb/ to read first>
  notes:       <optional reviewer notes>
```

## Queue

<!-- Guy: add entries here. Example below; remove or replace. -->

```
01. Share a file with an external user (web)
  status:    PLANNED
  audience:  end-user
  intent:    Show a SpecterX end user how to share one file with one external
             recipient, with default policy, from the web app.
  scope:     In: web flow, default policy, single recipient. Out: bulk share,
             custom policies, desktop drag-drop (separate article).
  sources:   kb/articles/share-files-from-web.html
  notes:     First end-to-end article. Keep flow tight; this is also the
             pipeline shake-down article.
```
