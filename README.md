# SpecterX Documentation

This repository holds SpecterX product knowledge, KB editorial planning, competitor reference research, and the tooling to author and preview help content.

## Repository layout

| Path | Purpose |
|------|---------|
| [`editorial/`](editorial/) | Article plan ([`ARTICLES_PLAN.md`](editorial/ARTICLES_PLAN.md)), style guide ([`STYLE_GUIDE.md`](editorial/STYLE_GUIDE.md)), public KB scope research |
| [`product/`](product/) | Component taxonomy, flat inventory, workflow source statement |
| [`pipeline/`](pipeline/) | VM plan, pipeline stage prompts |
| [`component-records/`](component-records/) | Internal PRDs and product records by platform area |
| [`legacy-manuals/`](legacy-manuals/) | Historical customer/operator `.docx` manuals (source material) |
| [`reference-library/`](reference-library/) | Crawled competitor KBs + generated research site |
| [`kb/`](kb/) | SpecterX help center scaffold (`articles.json`, CSS, preview pages) |
| [`tools/`](tools/) | Scrape, reference-site, and KB-site builders |
| [`WORKFLOW.md`](WORKFLOW.md) | Authoritative KB article pipeline spec (repo root) |
| [`writer/`](writer/), [`tester/`](tester/), [`workspace/`](workspace/) | Article pipeline runtime (see [WORKFLOW.md](WORKFLOW.md)) |

## Quick start

```bash
source .venv/bin/activate
pip install -r requirements.txt   # first time
playwright install chromium      # first time, for scraper only

python tools/reference-site/build_site.py
python tools/kb-site/build_kb.py

python3 -m http.server 8765
# open http://localhost:8765/index.html
```

## Reference library (competitor research)

Offline snapshots of HubSpot, Egnyte, Dropbox DocSend, Vera/Tricentis, and Virtru help centers, with per-platform pattern analyses.

| Platform | Analysis |
|----------|----------|
| HubSpot | [`reference-library/sources/hubspot/README.md`](reference-library/sources/hubspot/README.md) |
| Egnyte | [`reference-library/sources/egnyte/README.md`](reference-library/sources/egnyte/README.md) |
| DocSend | [`reference-library/sources/docsend/README.md`](reference-library/sources/docsend/README.md) |
| Vera | [`reference-library/sources/vera/README.md`](reference-library/sources/vera/README.md) |
| Virtru | [`reference-library/sources/virtru/README.md`](reference-library/sources/virtru/README.md) |

Browse via [`reference-library/site/index.html`](reference-library/site/index.html) or [`compare.html`](reference-library/site/compare.html).

To refresh crawled content (requires network):

```bash
python tools/scrape/scrape.py hubspot
python tools/reference-site/build_site.py
```

See [`tools/scrape/README.md`](tools/scrape/README.md) and [`AGENTS.md`](AGENTS.md).

## Knowledge base

The editorial plan lists **112 articles** in [`editorial/ARTICLES_PLAN.md`](editorial/ARTICLES_PLAN.md). The pipeline in [`WORKFLOW.md`](WORKFLOW.md) produces real articles under `workspace/articles/`; `tools/kb-site/build_kb.py` generates HTML stubs from [`kb/articles.json`](kb/articles.json) for preview only.

## Disclaimer

Contents of `reference-library/sources/` are downloaded copies of public help-center pages for internal research only. Each saved page records its source URL in `index.json`.
