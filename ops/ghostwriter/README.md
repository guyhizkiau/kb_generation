# SpecterX Ghostwriter

Product-facing control panel for the KB article pipeline: **Articles** (review + plan), **Health** (daemon status), and **Feedback** (annotation inbox).

Built with React, TypeScript, Vite, Mantine, and TanStack Query.

## Local development

Three terminals from the **repo root**. No VM or network required.

### Terminal A — control API (real `clusters/queue.json`)

```bash
python ops/ghostwriter/control_server.py
# → http://127.0.0.1:9191/api/queue
```

Starts only the pr-watcher REST control plane. Reads/writes the real queue file and `articles/*/STATE` on **main**; in-progress articles on `article/<slug>` branches are read by git ref (no checkout). Annotations live in `.ghostwriter/feedback/<slug>.json`. Does not poll GitHub or launch Claude.

### Terminal B — local API shim

```bash
# Optional: disable Health demo animation for a quiet dashboard
# GHOSTWRITER_AUTO_DEMO=0 python ops/ghostwriter/dev_server.py

python ops/ghostwriter/dev_server.py
# → http://127.0.0.1:8767
```

| Route | Behaviour |
|-------|-----------|
| `/status/status.json`, `/status/health.json` | Dashboard simulator |
| `/api/*`, `/poll-now`, `/retry` | Proxied to Terminal A when `:9191` is up |
| `/api/articles/{slug}/preview` | Rendered article HTML + Recogito/Annotorious widget |
| `/static/*` | Recogito, Annotorious, `ghostwriter-annotate.js` |
| `/api/feedback` GET/POST | Read/append `.ghostwriter/feedback/{slug}.json` |
| `POST /api/queue/merge` | Merge open `article/<slug>` PR into `main` via `gh` |

### Terminal C — SPA

```bash
cd ops/ghostwriter
cp .env.example .env.local   # first time — .env.local is gitignored
npm install                  # first time
npm run dev
# → http://localhost:5173/ghostwriter/
```

**Important:** For article review, use **same-origin** dev mode. The included `.env.local` leaves `VITE_API_BASE` unset so Vite proxies `/api` and `/static` to the shim. That lets the review iframe share origin with the SPA (reviewer name in `localStorage`, commenting works).

If you set `VITE_API_BASE=http://127.0.0.1:8767` instead, the UI loads but the review iframe is cross-origin and inline comments may not persist the reviewer name.

---

## Sanity test: article review + commenting

Use this checklist before running automated tests. ~5 minutes.

### Preflight (restart Terminal B after code updates)

```bash
# Must return HTML (not {"error":...})
curl -s http://127.0.0.1:8767/api/articles/01-log-in-to-specterx/preview | head -c 200
curl -s http://127.0.0.1:8767/api/articles/01-log-in-to-specterx/preview | grep -o 'ghostwriter-annotate.js'

# Feedback API (empty until you add a comment in the reader)
curl -s 'http://127.0.0.1:8767/api/feedback?slug=01-log-in-to-specterx' | python3 -m json.tool
```

### In the browser

Open **http://localhost:5173/ghostwriter/** (not `:8767` directly).

| Step | Action | Expected |
|------|--------|----------|
| 1 | Land on **Articles** (default view) | Cluster list + **Written & in progress** / **Up next** sections |
| 2 | Cluster **Logging in & account access** | Row **Log in to the SpecterX web platform** shows **Review** |
| 3 | Click **Review** | Full-screen reader overlay; article HTML in main pane |
| 4 | Right sidebar | Empty comments prompt, or list if you added comments earlier |
| 5 | In article pane, **select text** → add comment (Recogito popup) | Prompt for name first time; comment saves |
| 6 | Sidebar | New comment appears **without** clicking Refresh (postMessage sync) |
| 7 | **Back** | Returns to Articles |
| 8 | **Feedback** nav → click same article | Opens reader again; comments still listed |

### Verify persistence

After step 5, check the file grew:

```bash
cat .ghostwriter/feedback/01-log-in-to-specterx.json
```

### Articles without HTML

If an article has `final.md` but no HTML yet, the preview endpoint **renders it automatically** on first open. Planned articles with no draft show a blank preview only.

### Reviewable articles in this repo

| Slug | Phase | Has preview HTML |
|------|-------|-------------------|
| `01-log-in-to-specterx` | DONE | Yes — **use for review sanity test** |
| `02-set-or-reset-password` | varies | Yes (if rendered) |
| `03-what-is-specterx` | varies | Yes (if rendered) |

---

## Other smoke checks

- [ ] **Health** — navigate explicitly; counters load from `/status/status.json`
- [ ] **Poll now** — fires `POST /poll-now`
- [ ] **Articles → Up next** — reorder, Save, guarded delete (type `delete`)
- [ ] **Write this next** — confirm modal → `POST /api/queue/trigger`

---

## Automated tests

```bash
# Backend (repo root)
python3 -m unittest discover -s ops/pr-watcher -p 'test_*.py' -v

# Shim (repo root)
python3 -m unittest ops.ghostwriter.test_dev_shim -v

# SPA unit (ops/ghostwriter)
npm test

# Browser tests (Playwright) — mocked API
npx playwright install chromium   # one-time
npm run test:e2e                  # specs in tests/browser/
```

## Production build

```bash
cd ops/ghostwriter
npm run build
# Output: dist/ghostwriter/ (repo root)
```

Deploy to the VM is documented in [ops/pr-watcher/README.md](../pr-watcher/README.md).

## Architecture notes

- **Serving tree:** stays on `main` — merged articles read from the working tree
- **In-progress articles:** STATE + preview HTML read via `git show article/<slug>:…` (background `git fetch` keeps refs fresh)
- **Queue source of truth:** [`clusters/queue.json`](../../clusters/queue.json)
- **Per-article phase:** `articles/<slug>/STATE` (main when merged; branch ref when in-progress)
- **Annotations:** `.ghostwriter/feedback/<slug>.json` (VM: `/home/ubuntu/ghostwriter-feedback/<slug>.json`)
- **Daemon edits:** isolated git worktree at `.ghostwriter/worktree/` (VM: `/home/ubuntu/kb_generation-work`)
- **Preview widget:** [`static/ghostwriter-annotate.js`](static/ghostwriter-annotate.js) + [`preview_transform.py`](../pr-watcher/preview_transform.py)
- **Control server:** [`control_server.py`](control_server.py)
- **Shim:** [`dev_server.py`](dev_server.py)
