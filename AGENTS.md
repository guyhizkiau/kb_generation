# AGENTS.md

## Cursor Cloud specific instructions

This is a Python-based documentation tooling project (scraper + static site generators) for SpecterX. There is no traditional "lint" or "test" suite — correctness is verified by running the build scripts and serving the output.

### Services

| Service | Command | Purpose |
|---------|---------|---------|
| Static site server | `python3 -m http.server 8765` (from repo root) | Browse reference library and KB |

### Key commands (run from repo root with venv activated)

- **Activate venv:** `source .venv/bin/activate`
- **Build reference library site:** `python tools/reference-site/build_site.py` (generates `reference-library/site/*.html` and per-platform `reference-library/sources/*/index.html`)
- **Build KB stubs:** `python tools/kb-site/build_kb.py` (generates `kb/index.html`, category pages, article stubs from `kb/articles.json`)
- **List scraper seeds:** `python tools/scrape/scrape.py <platform> --list` (dry-run; no network needed)
- **Run scraper:** `python tools/scrape/scrape.py <platform>` (requires internet; fetches external help-center pages)
- **Serve site locally:** `python3 -m http.server 8765` then open `http://localhost:8765/index.html`

### Non-obvious notes

- The venv is at `.venv/` in the repo root. Always activate it before running any Python tool.
- `playwright install chromium` must have been run at least once after installing dependencies.
- The scraper requires network access to external help centers — it is **not** needed for building or viewing already-scraped content.
- Generated HTML under `reference-library/` and `kb/` is committed; `git diff` after a rebuild can show large diffs.
- Pipeline article work lives in `workspace/articles/` per [WORKFLOW.md](WORKFLOW.md); do not confuse with deleted root-level `articles/` prototypes.
- [CLAUDE.md](CLAUDE.md) covers the KB article pipeline; this file covers reference-library and static-site tooling.
