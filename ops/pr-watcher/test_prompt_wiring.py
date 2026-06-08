"""Prompt wiring test for revise-from-feedback phase."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "writer"))

from run_claude_code import assemble_prompt, PHASE_TO_PROMPT  # noqa: E402


class PromptWiringTests(unittest.TestCase):
    def test_revise_from_feedback_in_phase_map(self):
        self.assertEqual(
            PHASE_TO_PROMPT["revise-from-feedback"],
            "06-revise-from-feedback.md",
        )

    def test_assemble_prompt_includes_header_and_body(self):
        prompt_path = REPO_ROOT / "pipeline" / "prompts" / "06-revise-from-feedback.md"
        self.assertTrue(prompt_path.is_file())
        prompt = assemble_prompt("01-log-in-to-specterx", "revise-from-feedback")
        self.assertIn("revise-from-feedback", prompt)
        self.assertIn("01-log-in-to-specterx", prompt)
        self.assertIn(".ghostwriter/feedback", prompt)


if __name__ == "__main__":
    unittest.main()
