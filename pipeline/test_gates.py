"""Unit tests for pipeline/gates.py."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

import json

from pipeline.gates import (
    RESEARCH_CONTRACT,
    RESEARCH_MIN_ENTRIES,
    RESEARCH_SECTION_HEADING,
    check_research_gate,
    check_test_plan_gate,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
RESEARCH_PROMPT = REPO_ROOT / "pipeline" / "prompts" / "02-research.md"


class GatesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        os.environ["KB_REPO_ROOT"] = str(self.root)
        self.slug = "01-test"
        self.coverage = self.root / "articles" / self.slug / "research"
        self.coverage.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("KB_REPO_ROOT", None)

    def _write(self, bullets: list[str]) -> None:
        body = "## Articles read\n\n" + "\n".join(f"- {b}" for b in bullets)
        (self.coverage / "competitor-coverage.md").write_text(body)

    def _write_raw(self, content: str) -> None:
        (self.coverage / "competitor-coverage.md").write_text(content)

    # ── original passing / failing cases ────────────────────────────────────

    def test_passes_with_three(self):
        self._write(["A", "B", "C"])
        ok, msg = check_research_gate(self.slug)
        self.assertTrue(ok)
        self.assertIn("3", msg)

    def test_fails_with_two(self):
        self._write(["A", "B"])
        ok, msg = check_research_gate(self.slug)
        self.assertFalse(ok)
        self.assertIn("2", msg)

    def test_missing_file(self):
        ok, msg = check_research_gate(self.slug)
        self.assertFalse(ok)
        self.assertIn("missing", msg)

    # ── tolerance: heading variants ──────────────────────────────────────────

    def test_heading_with_suffix_passes(self):
        """'## Articles read end to end' should still open the section."""
        self._write_raw(
            "## Articles read end to end\n\n"
            '- Egnyte -- "Permissions" (cached 2026-06-01)\n'
            '- Virtru -- "Secure Share" (cached 2026-06-01)\n'
            '- Dropbox -- "Share" (cached 2026-06-01)\n'
        )
        ok, msg = check_research_gate(self.slug)
        self.assertTrue(ok, msg)

    def test_heading_case_insensitive(self):
        """Heading match is case-insensitive."""
        self._write_raw(
            "## ARTICLES READ\n\n"
            "- A\n- B\n- C\n"
        )
        ok, msg = check_research_gate(self.slug)
        self.assertTrue(ok, msg)

    # ── tolerance: table format ──────────────────────────────────────────────

    def test_table_format_passes(self):
        """Markdown table data rows count as source entries."""
        self._write_raw(
            "## Articles read\n\n"
            "| Vendor | Title | Date |\n"
            "|--------|-------|------|\n"
            "| Egnyte | Permissions | 2026-06-01 |\n"
            "| Virtru | Secure Share | 2026-06-01 |\n"
            "| Dropbox | Share | 2026-06-01 |\n"
        )
        ok, msg = check_research_gate(self.slug)
        self.assertTrue(ok, msg)

    def test_table_separator_not_counted(self):
        """Pure separator rows (|---|---|) are not counted as sources."""
        # header + separator + 2 data rows = 3 non-separator rows → passes
        self._write_raw(
            "## Articles read\n\n"
            "| Vendor | Title |\n"
            "|--------|-------|\n"
            "| Egnyte | Perm |\n"
            "| Virtru | Share |\n"
        )
        ok, _msg = check_research_gate(self.slug)
        self.assertTrue(ok)

    def test_table_only_separator_fails(self):
        """A table with only separator rows gives zero entries."""
        self._write_raw(
            "## Articles read\n\n"
            "|------|------|\n"
            "|------|------|\n"
        )
        ok, _msg = check_research_gate(self.slug)
        self.assertFalse(ok)

    # ── error messages embed the contract ───────────────────────────────────

    def test_error_missing_section_contains_contract(self):
        """Missing section error must contain the contract so an agent can self-correct."""
        self._write_raw("# No articles read heading here\n\nSome prose.\n")
        ok, msg = check_research_gate(self.slug)
        self.assertFalse(ok)
        self.assertIn(RESEARCH_SECTION_HEADING, msg)
        self.assertIn(str(RESEARCH_MIN_ENTRIES), msg)

    def test_error_too_few_entries_contains_contract(self):
        """Too-few-entries error must contain the contract."""
        self._write(["Only one"])
        ok, msg = check_research_gate(self.slug)
        self.assertFalse(ok)
        self.assertIn(str(RESEARCH_MIN_ENTRIES), msg)
        self.assertIn(RESEARCH_SECTION_HEADING, msg)

    def test_error_too_few_entries_shows_actual_count(self):
        self._write(["A", "B"])
        ok, msg = check_research_gate(self.slug)
        self.assertFalse(ok)
        self.assertIn("2", msg)

    # ── gate stops at next ## heading ───────────────────────────────────────

    def test_bullets_under_next_heading_not_counted(self):
        """Bullets in a section after ## Articles read don't contribute to the count."""
        self._write_raw(
            "## Articles read\n\n"
            "- A\n"
            "- B\n"
            "## Other section\n\n"
            "- C\n- D\n- E\n"
        )
        ok, msg = check_research_gate(self.slug)
        self.assertFalse(ok)  # only 2 bullets in the Articles read section

    # ── anti-drift: prompt ↔ gate contract ──────────────────────────────────

    def test_prompt_contains_section_heading(self):
        """02-research.md must literally mention the gate heading so they can't silently drift."""
        prompt_text = RESEARCH_PROMPT.read_text(encoding="utf-8")
        self.assertIn(
            RESEARCH_SECTION_HEADING,
            prompt_text,
            f"Prompt {RESEARCH_PROMPT.name} does not mention '{RESEARCH_SECTION_HEADING}'. "
            "Gate and prompt have drifted — update the prompt to state the exact contract.",
        )

    def test_prompt_mentions_minimum_count(self):
        """02-research.md must mention the minimum entry count (RESEARCH_MIN_ENTRIES = 3)."""
        prompt_text = RESEARCH_PROMPT.read_text(encoding="utf-8")
        self.assertIn(
            str(RESEARCH_MIN_ENTRIES),
            prompt_text,
            f"Prompt {RESEARCH_PROMPT.name} does not mention the minimum entry count "
            f"({RESEARCH_MIN_ENTRIES}). Gate and prompt have drifted.",
        )

    def test_research_contract_constant_nonempty(self):
        """RESEARCH_CONTRACT must be a non-empty, human-readable description."""
        self.assertGreater(len(RESEARCH_CONTRACT), 50)
        self.assertIn(RESEARCH_SECTION_HEADING, RESEARCH_CONTRACT)
        self.assertIn(str(RESEARCH_MIN_ENTRIES), RESEARCH_CONTRACT)


class TestPlanGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        os.environ["KB_REPO_ROOT"] = str(self.root)
        self.slug = "01-test"
        self.art = self.root / "articles" / self.slug
        self.art.mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()
        os.environ.pop("KB_REPO_ROOT", None)

    def _write_plan(self, steps: list) -> None:
        (self.art / "test-plan.json").write_text(json.dumps({"steps": steps}))

    def test_valid_minimal_plan(self):
        self._write_plan([
            {"id": "00-goto", "backend": "browser", "action": {"type": "goto", "url": "https://x"}},
            {"id": "01-click", "backend": "browser", "action": {"type": "click", "role": "button", "name": "Go"}},
        ])
        ok, msg = check_test_plan_gate(self.slug)
        self.assertTrue(ok, msg)

    def test_missing_login_fails(self):
        self._write_plan([
            {"id": "01-click", "backend": "browser", "action": {"type": "click", "role": "button", "name": "Go"}},
        ])
        ok, msg = check_test_plan_gate(self.slug)
        self.assertFalse(ok)
        self.assertIn("00-", msg)

    def test_prose_selector_hint_fails(self):
        self._write_plan([
            {"id": "00-goto", "backend": "browser", "action": {"type": "goto", "url": "https://x"}},
            {
                "id": "01-click",
                "backend": "browser",
                "action": {
                    "type": "click",
                    "selector_hint": "the button that opens the share dialog for folders",
                },
            },
        ])
        ok, msg = check_test_plan_gate(self.slug)
        self.assertFalse(ok)
        self.assertIn("selector_hint", msg)
