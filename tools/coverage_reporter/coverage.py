"""Minimal line coverage tracker built on ``sys.settrace``.

No external dependencies. Tracks executed (file, line) pairs across an
explicit set of source roots, and computes coverage% by counting executable
statements via ``ast``.
"""
from __future__ import annotations
import ast
import sys
from dataclasses import dataclass, field
from pathlib import Path


def _executable_lines(path: Path) -> set[int]:
    src = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return set()
    lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef, ast.Module)):
            continue
        if hasattr(node, "lineno"):
            lines.add(node.lineno)
    return lines


@dataclass
class LineCoverage:
    roots: list[Path]
    hit: dict[str, set[int]] = field(default_factory=dict)
    _prev_trace = None

    def _matches(self, filename: str) -> bool:
        try:
            p = Path(filename).resolve()
        except Exception:
            return False
        for r in self.roots:
            try:
                p.relative_to(r)
                return True
            except ValueError:
                continue
        return False

    def _trace(self, frame, event, arg):
        if event == "line":
            fn = frame.f_code.co_filename
            if self._matches(fn):
                self.hit.setdefault(fn, set()).add(frame.f_lineno)
        return self._trace

    def __enter__(self):
        self._prev_trace = sys.gettrace()
        sys.settrace(self._trace)
        return self

    def __exit__(self, *exc):
        sys.settrace(self._prev_trace)
        return False

    def report(self) -> dict:
        out: dict[str, dict] = {}
        total_exec = 0
        total_hit = 0
        for root in self.roots:
            for path in root.rglob("*.py"):
                if "__pycache__" in path.parts:
                    continue
                exec_lines = _executable_lines(path)
                if not exec_lines:
                    continue
                hit_lines = self.hit.get(str(path), set()) & exec_lines
                out[str(path.relative_to(root.parent))] = {
                    "executable": len(exec_lines),
                    "hit": len(hit_lines),
                    "pct": (len(hit_lines) / len(exec_lines)) if exec_lines else 0.0,
                }
                total_exec += len(exec_lines)
                total_hit += len(hit_lines)
        out["__summary__"] = {
            "executable": total_exec,
            "hit": total_hit,
            "pct": (total_hit / total_exec) if total_exec else 0.0,
        }
        return out
