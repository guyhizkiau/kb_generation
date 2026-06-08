# CLAUDE.md — Pipeline workflow rules

> Rules for any future Claude Code session operating the article pipeline
> in this repo. (See `AGENTS.md` for rules covering the reference-library
> scraper and static-site tooling — that lives in `tools/`, `kb/`,
> `reference-library/`, and is a separate concern.)

## Two projects, one repo

This repository hosts two related but separate code paths:

1. **Reference library + static site** (existing). Documented in
   `AGENTS.md`. Touches `tools/`, `kb/`, `reference-library/`.
2. **KB article pipeline** (new). This file. Touches `writer/`,
   `tester/`, `pipeline/prompts/`, `editorial/`, `articles/`, and the
   long-running `ops/pr-watcher/` daemon on the EC2 VM. Phases can be
   run manually (`python writer/run_claude_code.py --phase …`) OR
   driven autonomously by the pr-watcher daemon when an article PR is
   open. The autonomous bot resolves PR comments, watches for merges,
   and triggers the next article in the cluster. See
   [`ops/pr-watcher/README.md`](ops/pr-watcher/README.md) for its full
   operational runbook.

Do not let work in one path silently mutate the other. The static-site
build output lives in `kb/` (stubs from `tools/kb-site/`); pipeline
articles live in `articles/NN-slug/` (the canonical location;
historical docs may still reference the deprecated
`workspace/articles/NN-slug/` path — `writer/run_claude_code.py`
resolves both for backward compatibility).

## Branches & commits

- Never commit directly to `main`. Always work on a branch.
- Branch naming:
  - Per-article work: `article/NN-slug`
  - Infra / pipeline code: `pipeline/<short-topic>`
  - Bootstrap / one-offs: `bootstrap/<short-topic>`
- Conventional Commits format. Types in use: `feat`, `fix`, `chore`,
  `docs`, `refactor`, `test`. Article work uses scope `article`:
  `feat(article): 01-share-file — first draft`.
- One commit per pipeline phase (`draft`, `test-notes`, `revise`,
  `final`). Do not amend screenshots into prior commits — history of
  what the tester saw is part of the audit trail.
- Exception — comment resolution (WORKFLOW.md §9.5) produces **two**
  commits: a `docs(...)` commit that fixes the canonical source of
  truth (style guide, glossary, taxonomy, scope, or a prompt) first,
  then a `fix(article):` commit that applies it to the article. Keep
  them separate and in that order so the durable rule is visible apart
  from its first application. If the validate-then-expand loop runs, each
  rule expansion is its own amended `docs(...)` commit.
- Do not auto-commit when the user has not asked. The pipeline is
  allowed to commit on its own branch under `workspace/articles/...`;
  human-driven sessions need explicit consent.

## STATE files are authoritative

Each article under `workspace/articles/NN-slug/` has a `STATE` file
recording its position in the pipeline state machine
(`PLANNED → DRAFTING → TESTING → REVISING → FINALIZING → PR_OPEN →
DONE`). Before editing any article file, read its `STATE` first. Do
not advance state implicitly by editing the wrong file for the current
phase — only the writer, tester, or the human/agent running a phase
should update `STATE`, as the last action of that phase.

## Secrets

- Credentials live in `~/.config/specterx-kb/.env` (mode 600). Never
  commit them. Never paste them into a PR description, commit message,
  or log line.
- `SPECTERX_PASSWORD` is a real account password. Treat it like one.
- PII / customer data must never appear in screenshots that get
  committed. Before committing screenshots, check them against
  `tester/sensitive-terms.txt` (and common sense). Flagged originals
  belong in `screenshots/_flagged/` (git-ignored), not in the article.

## When to ask Guy

Ask before anything that costs money, touches customer data, or changes
repo-level configuration. See [WORKFLOW.md](WORKFLOW.md) for the full
pipeline rules.

## Pipeline entry points

Run from the repo root with `.venv` activated (or `VENV_PYTHON` on a VM):

- `python writer/run_claude_code.py --article NN-slug --phase {draft|test-plan|revise-from-test|voice-pass|revise-from-pr}`
- `python tester/runner.py --article NN-slug`

The `voice-pass` phase runs after `revise-from-test` and before the PR
is opened. It rewrites the prose against `editorial/STYLE_GUIDE.md`
(Sections 2.4, 3, 10, 13, 13a, 14) and strips internal QA metadata
from `final.md`. See `pipeline/prompts/04a-voice-pass.md`.

Follow [WORKFLOW.md](WORKFLOW.md) for phase order and when to open or
merge PRs. When the pipeline is in autonomous mode (an article PR is
open and the pr-watcher daemon is running on the VM), see
[`ops/pr-watcher/README.md`](ops/pr-watcher/README.md) for the
operational runbook — including how the daemon talks to Claude (PTY +
`--output-format stream-json`), the three timeout dials, the
dashboard at `http://18.192.122.48/status/`, and the deploy procedure
via AWS SSM.

Ghostwriter reviewer annotations live in the branch-independent feedback
store (`.ghostwriter/feedback/<slug>.json` locally;
`/home/ubuntu/ghostwriter-feedback/<slug>.json` on the VM) — not in
`articles/<slug>/feedback.json`. The serving tree stays on `main`; each
in-progress article is read from its `article/<slug>` branch by git ref.
