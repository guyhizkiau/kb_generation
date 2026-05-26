# Scrape tools

Crawls external competitor help centers into [`reference-library/sources/`](../reference-library/sources/).

```bash
source .venv/bin/activate
python tools/scrape/scrape.py <platform>          # hubspot | egnyte | docsend | vera
python tools/scrape/scrape.py <platform> --list
python tools/scrape/discover_links.py <url> --include /path/prefix
```

Platform configs: `tools/scrape/platforms/*.yml`. Crawl state: `.scrape-state/` (gitignored).
