# writer/

Wraps `claude -p` (Claude Code non-interactive mode). Given an article
slug and a phase, runs the corresponding prompt from `pipeline/prompts/` with
the article's working directory as context, then exits.

## Entry point

```
python writer/run_claude_code.py --article NN-slug --phase {draft|test-plan|revise-from-test|revise-from-pr}
```

## Phases

| Phase                 | Prompt                                | Reads                                  | Writes                  |
|-----------------------|---------------------------------------|----------------------------------------|-------------------------|
| `draft`               | `pipeline/prompts/01-draft.md`                 | `editorial/ARTICLES_PLAN.md`, `reference-library/sources/`, `kb/` | `draft-1.md`, `STATE`   |
| `test-plan`           | `pipeline/prompts/02-test-plan.md`             | `draft-1.md`                           | `test-plan.json`, `STATE` |
| `revise-from-test`    | `pipeline/prompts/03-revise-from-test.md`      | `draft-1.md`, `test-notes.md`          | `draft-2.md`, `STATE`   |
| `revise-from-pr`      | `pipeline/prompts/04-revise-from-pr-comments.md` | `final.md`, fetched PR review comments | `final.md` (rewritten), `STATE` |

The article working directory is `workspace/articles/NN-slug/`.
