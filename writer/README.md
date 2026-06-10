# writer/

Wraps `claude -p` (Claude Code non-interactive mode). Given an article
slug and a phase, runs the corresponding prompt from `pipeline/prompts/` with
the article's working directory as context, then applies the STATE
transition via `store/machine.py`.

## Entry point

```
python writer/run_claude_code.py --article NN-slug --phase {research|draft|test-plan|revise-from-test|voice-pass|revise-from-feedback}
```

## Phases

| Phase                 | Prompt                                | Reads                                  | Writes                         | STATE transition        |
|-----------------------|---------------------------------------|----------------------------------------|--------------------------------|-------------------------|
| `research`            | `pipeline/prompts/02-research.md`     | plan, references, canon                | `research/competitor-coverage.md` | `RESEARCHING` → `DRAFTING` |
| `draft`               | `pipeline/prompts/01-draft.md`        | research outputs, plan                 | `draft-1.md`                   | `DRAFTING` → `TESTING`  |
| `test-plan`           | `pipeline/prompts/02-test-plan.md`    | `draft-1.md`                           | `test-plan.json`               | *(none — tester follows)* |
| `revise-from-test`    | `pipeline/prompts/03-revise-from-test.md` | `draft-1.md`, `test-notes.md`      | `draft-2.md`                   | `REVISING` → `FINALIZING` |
| `voice-pass`          | `pipeline/prompts/04a-voice-pass.md`  | `draft-2.md`, style guide              | `final.md`                     | `FINALIZING` → `IN_REVIEW` |
| `revise-from-feedback`| `pipeline/prompts/06-revise-from-feedback.md` | `final.md`, `feedback.json`    | `final.md` (rewritten)         | `REVISING` → `FINALIZING` |

The article working directory is `articles/NN-slug/` on `main`.

After the `research` phase, `pipeline/gates.check_research_gate()` must
pass (≥3 competitor articles in `competitor-coverage.md`) or the article
is blocked.

The tester (`tester/runner.py`) transitions `TESTING` → `REVISING` and
sets `VERIFIED_AS_OF` on a passing run. Approve/publish transitions are
handled by the pr-watcher control plane, not the writer.

Only one article may be in an active phase at a time; the script exits
with code 3 if another article is in-flight (override with
`KB_SERIAL_OVERRIDE=1`).
