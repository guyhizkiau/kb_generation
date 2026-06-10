"""Re-lint approved articles when style assets change."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from store.machine import LEGACY_MAP, current_phase
from store.paths import articles_root, repo_root
from store.state import write_state

APPROVED_PHASES = {"PUBLISHED", "APPROVED", "DONE", "MERGED"}
ASSET_PATHS = {
    "editorial/STYLE_GUIDE.md",
    "canon/GLOSSARY.md",
    "product/COMPONENT_TAXONOMY.md",
    "editorial/lint_rules.json",
}


@dataclass
class Violation:
    file: str
    line: int
    rule: str
    excerpt: str


def lint_article(slug: str, rules: dict) -> list[Violation]:
    """Check final.md against lint_rules.json."""
    path = articles_root() / slug / "final.md"
    if not path.is_file():
        return []
    violations: list[Violation] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines, 1):
        for entry in rules.get("banned_phrases", []):
            if re.search(entry["pattern"], line, re.IGNORECASE):
                violations.append(Violation(str(path), i, entry["rule"], line.strip()[:80]))
        for term in rules.get("glossary_terms", []):
            for bad in term.get("violations", []):
                if bad in line:
                    violations.append(Violation(
                        str(path), i,
                        f"glossary: use '{term['canonical']}'",
                        line.strip()[:80],
                    ))
    return violations


def relint_catalog(rules_path: Path | None = None) -> dict[str, list[Violation]]:
    """Lint all approved articles."""
    rp = rules_path or repo_root() / "editorial" / "lint_rules.json"
    rules = json.loads(rp.read_text(encoding="utf-8"))
    results: dict[str, list[Violation]] = {}
    if not articles_root().exists():
        return results
    for art_dir in sorted(articles_root().iterdir()):
        if not art_dir.is_dir():
            continue
        slug = art_dir.name
        if current_phase(slug) not in APPROVED_PHASES and LEGACY_MAP.get(
            __import__("store.state", fromlist=["read_state"]).read_state(slug).get("PHASE", ""),
            "",
        ) not in APPROVED_PHASES:
            phase = current_phase(slug)
            if phase not in APPROVED_PHASES:
                continue
        v = lint_article(slug, rules)
        if v:
            results[slug] = v
    return results


def apply_rework_flags(results: dict[str, list[Violation]]) -> None:
    """Flag articles with lint violations."""
    for slug, violations in results.items():
        report = [
            {"file": v.file, "line": v.line, "rule": v.rule, "excerpt": v.excerpt}
            for v in violations
        ]
        report_path = articles_root() / slug / "relint-report.json"
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        write_state(slug, {
            "REWORK_REASON": f"re-lint: {len(violations)} violations — see relint-report.json",
        })


def diff_touches_assets(diff_text: str) -> bool:
    """Return True if a git diff touches style-asset paths."""
    return any(p in diff_text for p in ASSET_PATHS)
