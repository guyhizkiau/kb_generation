# orchestrator/

The long-running poll loop. Decides what article to work on next, calls
into `writer/` and `tester/` via subprocess, opens and tracks PRs.

## Layout (target)

- `main.py` — entry point, the poll loop
- `article_pipeline.py` — state-machine driver (one article at a time)
- `github_client.py` — wraps the `gh` CLI for PR operations
- `idle.py` — self-stop after 15 minutes of no work
- `cost_check.py` — daily AWS Cost Explorer check

## Status

Phase A scaffolding only. Implementation lands in Phase E per
`docs/02-HANDOFF.md`. This README is a placeholder so the directory is
tracked by git.
