"""Assurance case linter.

Validates that each `docs/PhaseC/cases/*.md` file contains every required
section (per `docs/PhaseC/template/assurance-case-template.md`) and that
the Identity block parses with all five fields populated.

Used as a CI gate in the orchestrator: any missing required section blocks
the run from completing.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path


REQUIRED_SECTIONS: list[str] = [
    "1. Identity",
    "2. Top claim",
    "3. Context",
    "4. Assumptions",
    "5. Strategy",
    "6. Sub-goals + evidence",
    "7. Failure modes",
    "8. Fallback behavior",
    "9. Human override path",
    "10. Change impact",
    "11. Standards mapping",
    "12. Reviewer log",
]

_SECTION_PATTERNS = {
    s: re.compile(rf"^#{{2,3}}\s+{re.escape(s)}\b", re.MULTILINE)
    for s in REQUIRED_SECTIONS
}

_IDENTITY_BLOCK_RE = re.compile(
    r"#{2,3}\s+1\. Identity\s*\n```([\s\S]*?)```", re.MULTILINE
)

REQUIRED_IDENTITY_FIELDS = [
    "model_name", "version", "case_owner", "last_reviewed", "state",
]

VALID_STATES = {"auto-generated", "reviewer-confirmed", "board-approved"}


@dataclass
class LintReport:
    path: Path
    missing_sections: list[str] = field(default_factory=list)
    missing_identity: list[str] = field(default_factory=list)
    invalid_state: str | None = None
    state: str | None = None

    @property
    def ok(self) -> bool:
        return (not self.missing_sections
                and not self.missing_identity
                and self.invalid_state is None)

    def to_dict(self) -> dict:
        return {
            "path": str(self.path),
            "ok": self.ok,
            "missing_sections": self.missing_sections,
            "missing_identity": self.missing_identity,
            "invalid_state": self.invalid_state,
            "state": self.state,
        }


def _extract_identity_block(text: str) -> dict[str, str]:
    """Find the first triple-backtick block under the Identity section
    and parse `key: value` lines out of it."""
    m = _IDENTITY_BLOCK_RE.search(text)
    if not m:
        return {}
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def lint_case(path: Path) -> LintReport:
    text = path.read_text(encoding="utf-8")
    rep = LintReport(path=path)

    for section, pattern in _SECTION_PATTERNS.items():
        if not pattern.search(text):
            rep.missing_sections.append(section)

    identity = _extract_identity_block(text)
    for f in REQUIRED_IDENTITY_FIELDS:
        if not identity.get(f):
            rep.missing_identity.append(f)

    state = identity.get("state")
    rep.state = state
    if state and state not in VALID_STATES:
        rep.invalid_state = state

    return rep


def lint_all_cases(cases_dir: Path) -> list[LintReport]:
    reports: list[LintReport] = []
    for p in sorted(Path(cases_dir).glob("*.md")):
        reports.append(lint_case(p))
    return reports
