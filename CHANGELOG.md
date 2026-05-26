# Changelog

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
