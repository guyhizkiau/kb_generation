# workspace/

Runtime working directory for pipeline-driven article drafts.

- `workspace/articles/NN-slug/STATE` — current pipeline state
- `workspace/articles/NN-slug/draft-1.md` — first draft
- `workspace/articles/NN-slug/test-plan.json` — extracted test plan
- `workspace/articles/NN-slug/test-notes.md` — tester observations
- `workspace/articles/NN-slug/draft-2.md` — revised draft
- `workspace/articles/NN-slug/final.md` — the deliverable
- `workspace/articles/NN-slug/screenshots/` — visual evidence
- `workspace/articles/NN-slug/screenshots/_flagged/` — PII-flagged
  originals (git-ignored)

This is intentionally separate from the top-level `articles/` directory,
which holds generated static-site HTML for the existing
reference-library project.
