# Reference site builder

Regenerates the offline navigation site under [`reference-library/site/`](../reference-library/site/) from `reference-library/sources/*/index.json`.

```bash
source .venv/bin/activate
python tools/reference-site/build_site.py
```

Outputs: `reference-library/site/index.html`, `compare.html`, and per-platform pages under `reference-library/sources/<slug>/index.html`.
