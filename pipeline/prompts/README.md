# Pipeline prompts

Prompt files invoked by the article pipeline (`writer/run_claude_code.py` and manual Claude Code sessions).

| File | Stage | Status |
|------|-------|--------|
| `01-draft.md` | Draft article from plan + sources | Active |
| `02-test-plan.md` | Generate test plan from draft | Active |
| `02-research.md` | Gather research before drafting | Active |
| `03-revise-from-test.md` | Revise draft from test notes | Active |
| `04a-voice-pass.md` | Voice and tone pass against `STYLE_GUIDE.md` before PR | Active |
| `04-revise-from-pr-comments.md` | Revise from PR review | Active |
| `05-extract-style.md` | Refresh `editorial/STYLE_GUIDE.md` from approved articles | Active |

Stages `00` (setup) and `01` (cluster scenario) prompts are not checked in yet — see [WORKFLOW.md](../WORKFLOW.md) at the repo root.
