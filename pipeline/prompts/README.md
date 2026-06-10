# Pipeline prompts

Prompt files invoked by the article pipeline (`writer/run_claude_code.py` and manual Claude Code sessions).

| File | Phase | Status |
|------|-------|--------|
| `02-research.md` | Gather research before drafting | Active |
| `01-draft.md` | Draft article from plan + sources | Active |
| `02-test-plan.md` | Generate test plan from draft | Active |
| `03-revise-from-test.md` | Revise draft from test notes | Active |
| `04a-voice-pass.md` | Voice pass against `STYLE_GUIDE.md` before `IN_REVIEW` | Active |
| `06-revise-from-feedback.md` | Revise from Ghostwriter annotations | Active |
| `05-extract-style.md` | Refresh `editorial/STYLE_GUIDE.md` from published articles | Active |
| `04-revise-from-pr-comments.md` | Revise from GitHub PR review | **Retired** (pre–single-branch) |

Stages `00` (setup) and `01` (cluster scenario) prompts are not checked in yet — see [WORKFLOW.md](../../WORKFLOW.md) at the repo root.

Phase → prompt mapping is defined in `writer/run_claude_code.py` (`PHASE_TO_PROMPT`). STATE transitions after each phase are applied by the writer via `store/machine.py` — prompts must not edit `STATE` directly.
