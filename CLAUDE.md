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
   `tester/`, `pipeline/prompts/`, `workspace/`, and adds article drafts
   under `workspace/articles/NN-slug/`. Phases are run manually or via
   Cursor — there is no long-running orchestrator service.

Do not let work in one path silently mutate the other. The static-site
build output lives in `kb/` (stubs from `tools/kb-site/`); pipeline articles
live in `workspace/articles/NN-slug/` until they are promoted.

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

- `python writer/run_claude_code.py --article NN-slug --phase {draft|test-plan|revise-from-test|revise-from-pr}`
- `python tester/runner.py --article NN-slug`

Follow [WORKFLOW.md](WORKFLOW.md) for phase order and when to open or merge PRs.
