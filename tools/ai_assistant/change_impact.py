"""Change impact analyzer — "if I touch this requirement, what tests and
what source files should I re-inspect?".

The index is built from two sources:
  * JSON test cases under ``tools/runner/test_cases`` — each has a ``req``
    field; that gives us Req -> Test links.
  * A simple keyword heuristic mapping requirement ID prefixes to source
    module paths. That gives us Req -> Code links without needing a real
    clang index.

Every result carries a DRAFT disclaimer so no one confuses this with a
certified change-impact analysis.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path


_PREFIX_TO_MODULES = {
    "HLR-FCC": ["tools/sim_py/avx_sim/modules/fcc.py"],
    "HLR-ENG": ["tools/sim_py/avx_sim/modules/engine.py"],
    "HLR-DSP": ["tools/sim_py/avx_sim/modules/display.py"],
    "HLR-DC":  ["tools/sim_py/avx_sim/modules/data_concentrator.py"],
    "HLR-HM":  ["tools/sim_py/avx_sim/health_monitor.py",
                "tools/sim_py/avx_sim/scheduler.py"],
    "SYS":     ["tools/sim_py/avx_sim/scheduler.py",
                "tools/sim_py/avx_sim/sim_clock.py",
                "tools/sim_py/avx_sim/recorder.py"],
}


@dataclass
class ImpactIndex:
    req_to_tests: dict[str, list[str]] = field(default_factory=dict)
    req_to_code: dict[str, list[str]] = field(default_factory=dict)
    test_paths: dict[str, str] = field(default_factory=dict)  # TC id -> path


def _match_modules(req_id: str) -> list[str]:
    for prefix, mods in _PREFIX_TO_MODULES.items():
        if req_id.startswith(prefix):
            return list(mods)
    return []


def build_impact_index(test_cases_dir: str | Path) -> ImpactIndex:
    idx = ImpactIndex()
    for path in sorted(Path(test_cases_dir).glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        tc_id = data.get("id", path.stem)
        idx.test_paths[tc_id] = str(path)
        for req in data.get("req", []):
            idx.req_to_tests.setdefault(req, []).append(tc_id)
            if req not in idx.req_to_code:
                idx.req_to_code[req] = _match_modules(req)
    return idx


def impact_for_requirement(idx: ImpactIndex, req_id: str) -> dict:
    tests = idx.req_to_tests.get(req_id, [])
    code = idx.req_to_code.get(req_id) or _match_modules(req_id)
    return {
        "_draft": "DRAFT - human-in-the-loop change impact; review before use.",
        "req": req_id,
        "tests": sorted(tests),
        "code_paths": sorted(code),
    }
