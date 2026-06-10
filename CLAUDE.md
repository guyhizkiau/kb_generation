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
   `tester/`, `store/`, `pipeline/`, `editorial/`, `articles/`, and the
   long-running `ops/pr-watcher/` daemon on the EC2 VM. Phases can be
   run manually (`python writer/run_claude_code.py --phase …`) OR
   driven autonomously by the pr-watcher dispatcher when an article is
   in an active `PHASE`. See [`ops/pr-watcher/README.md`](ops/pr-watcher/README.md)
   for the operational runbook.

Do not let work in one path silently mutate the other. The static-site
build output lives in `kb/` (stubs from `tools/kb-site/`); pipeline
articles live in `articles/NN-slug/` on `main`.

## Branches & commits

- **All article work commits directly to `main`.** There are no
  per-article branches in the current pipeline.
- Infra / pipeline code may still use feature branches
  (`pipeline/<short-topic>`) with normal PRs into `main`.
- Conventional Commits format. Types in use: `feat`, `fix`, `chore`,
  `docs`, `refactor`, `test`. Article work uses scope `article`:
  `feat(article): 01-share-file — first draft`.
- One commit per pipeline phase where practical (`draft`, `test-notes`,
  `revise`, `voice-pass`). Do not amend screenshots into prior commits —
  history of what the tester saw is part of the audit trail.
- Exception — review feedback resolution (WORKFLOW.md §9.5) produces
  **two** commits when a canonical rule applies: a `docs(...)` commit
  that fixes the source of truth first, then a `fix(article):` commit
  that applies it to the article.
- Do not auto-commit when the user has not asked. The autonomous
  dispatcher may commit on `main` under `articles/<slug>/`; human-driven
  sessions need explicit consent.

> **Historical note:** Earlier pipeline versions used `article/<NN-slug>`
> branches and GitHub PRs for review. That flow is retired.

## STATE files are authoritative

Each article under `articles/NN-slug/` has a `STATE` file recording its
position in the pipeline state machine (`QUEUED → RESEARCHING →
DRAFTING → TESTING → REVISING → FINALIZING → IN_REVIEW → APPROVED →
PUBLISHED`). Exact transitions are enforced in `store/machine.py`.

Before editing any article file, read its `STATE` first. Do not advance
state implicitly by editing the wrong file for the current phase — only
`writer/run_claude_code.py`, `tester/runner.py`, `store/machine.py`, or
the pr-watcher control plane should call `transition()`, as the last
action of that phase.

## Reviewer feedback

Ghostwriter annotations are stored in
`articles/<slug>/feedback.json` by default. On the VM,
`GHOSTWRITER_FEEDBACK_DIR` may override the path (e.g.
`/home/ubuntu/ghostwriter-feedback/<slug>.json`).

Approve, request-changes, and publish are control-plane actions on
`IN_REVIEW` / `APPROVED` articles — not git merges. See WORKFLOW.md §9.6.

## Secrets

- Credentials live in `~/.config/specterx-kb/.env` (mode 600). Never
  commit them. Never paste them into commit messages or log lines.
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

- `python writer/run_claude_code.py --article NN-slug --phase {research|draft|test-plan|revise-from-test|voice-pass|revise-from-feedback}`
- `python tester/runner.py --article NN-slug`

The `voice-pass` phase runs after `revise-from-test` (or
`revise-from-feedback`) and transitions the article to `IN_REVIEW`. It
rewrites prose against `editorial/STYLE_GUIDE.md` (Sections 2.4, 3, 10,
13, 13a, 14) and strips internal QA metadata from `final.md`. See
`pipeline/prompts/04a-voice-pass.md`.

Follow [WORKFLOW.md](WORKFLOW.md) for phase order and review/publish.
When the pr-watcher daemon is running on the VM, see
[`ops/pr-watcher/README.md`](ops/pr-watcher/README.md) — including how
the daemon talks to Claude (PTY + `--output-format stream-json`), the
three timeout dials, the dashboard at `http://18.192.122.48/status/`,
and the deploy procedure via AWS SSM.
