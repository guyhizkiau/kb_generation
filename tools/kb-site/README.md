# KB site builder

Generates stub HTML for the SpecterX help center from [`kb/articles.json`](../kb/articles.json).

```bash
source .venv/bin/activate
python tools/kb-site/build_kb.py
```

Outputs: `kb/index.html`, `kb/sitemap.html`, `kb/categories/*.html`, `kb/articles/*.html`. The article pipeline in [WORKFLOW.md](../WORKFLOW.md) will replace stubs with real articles over time.
