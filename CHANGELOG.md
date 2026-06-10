# Changelog

## 2026-06-10 — Single-branch status-driven pipeline

- Replaced per-article PR branches with commits on `main` and a `PHASE`
  state machine (`store/machine.py`).
- pr-watcher now dispatches phases via `dispatcher.py` (serial: one
  active article at a time) instead of polling GitHub PRs.
- Review flow: `IN_REVIEW` → approve (`POST /api/queue/approve`) →
  publish (`pipeline/publish/`). Request changes via
  `POST /api/queue/request-changes`.
- New STATE fields: `VERIFIED_AS_OF`, `APPROVED_BY`/`APPROVED_AT`,
  `REWORK_REASON`. Feedback annotations at
  `articles/<slug>/feedback.json`.
- Deterministic research gate (`pipeline/gates.py`), re-verification
  (`pipeline/reverify.py`), and re-lint (`pipeline/relint.py`).
- Updated `WORKFLOW.md`, `CLAUDE.md`, `ops/pr-watcher/README.md`,
  `writer/README.md`, and `pipeline/prompts/README.md`.

## 2026-05-26 — Drop unused orchestrator/infra

- Removed `orchestrator/` (never implemented; article phases run via `writer/` and an agent or operator).
- Removed `infra/` (systemd/cron were never added). Moved `sensitive-terms.txt` to `tester/`.
- Updated `CLAUDE.md`, `WORKFLOW.md`, prompts, and `writer/run_claude_code.py` (`pipeline/prompts/` path).

## 2026-05-26 — Repository restructure

Reorganized the flat repo root into purposeful top-level areas:

| Path | Purpose |
|------|---------|
| `editorial/` | KB article plan, style guide placeholder, public-scope research |
| `product/` | Component taxonomy, inventory, source workflow statement |
| `pipeline/` | VM plan, pipeline stage prompts |
| `component-records/` | Internal product-record documents by platform area |
| `legacy-manuals/` | Historical customer/operator `.docx` manuals |
| `reference-library/` | Competitor KB crawl + generated research site |
| `kb/` | SpecterX help center scaffold (`articles.json`, CSS, index) |
| `tools/scrape/`, `tools/reference-site/`, `tools/kb-site/` | Build and crawl tooling |

Other changes:

- Single canonical article plan: `editorial/ARTICLES_PLAN.md` (removed v1/v2/v3 naming).
- `WORKFLOW.md` stays at repo root.
- Removed prototype articles (`articles/`, all `kb/articles/*.html`, `kb/categories/*.html`).
- Root `index.html` links to the reference library and KB.
