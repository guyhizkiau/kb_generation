# AGENTS.md

## Cursor Cloud specific instructions

This is a Python-based documentation tooling project (scraper + static site generator) for SpecterX. There is no traditional "lint" or "test" suite — correctness is verified by running the build scripts and serving the output.

### Services

| Service | Command | Purpose |
|---------|---------|---------|
| Static site server | `python3 -m http.server 8765` (from repo root) | Browse generated reference library and KB |

### Key commands (run from repo root with venv activated)

- **Activate venv:** `source .venv/bin/activate`
- **Build reference library site:** `python tools/build_site.py` (generates `index.html`, `compare.html`, per-platform pages)
- **Build KB:** `python tools/build_kb.py` (generates `kb/index.html`, category pages, article stubs from `kb/articles.json`)
- **List scraper seeds:** `python tools/scrape.py <platform> --list` (dry-run; no network needed)
- **Run scraper:** `python tools/scrape.py <platform>` (requires internet; fetches external help-center pages)
- **Serve site locally:** `python3 -m http.server 8765` then open `http://localhost:8765/index.html`

### Non-obvious notes

- The venv is at `.venv/` in the repo root. Always activate it before running any Python tool.
- `playwright install chromium` must have been run at least once after installing dependencies (the update script handles this).
- The scraper (`tools/scrape.py`) requires network access to external help centers — it is **not** needed for building or viewing already-scraped content.
- `build_kb.py` skips 3 hand-written article files (listed in `HAND_WRITTEN` set) and won't overwrite them.
- There is no linter, formatter, or automated test suite configured in this repository. Validation is done by running the build scripts and confirming they exit 0 and produce the expected HTML files.
- Generated HTML files (`index.html`, `compare.html`, `sources/*/index.html`, `kb/**/*.html`) are committed to the repo, so `git diff` after a rebuild can show unintended regressions.
