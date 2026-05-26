# Changelog

## 2026-05-26 — Repository restructure

Reorganized the flat repo root into purposeful top-level areas:

| Path | Purpose |
|------|---------|
| `editorial/` | KB article plan and public-scope research |
| `product/` | Component taxonomy, inventory, source workflow statement |
| `pipeline/` | VM plan, pipeline prompts (orchestrator/writer/tester remain at root per WORKFLOW) |
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
