# Tool Qualification Notes (DO-330 / DO-331)

> Learning-grade notes, not a qualification kit. Every entry documents what
> the tool does, how it is used in this workbench, the **assumed** Tool
> Qualification Level (TQL) if this were a real program, and known
> limitations. None of the in-house tools in this repository have been
> formally qualified.

## Tool use classification

DO-330 splits tools into three **criteria** driven by how their output is
used:

| Criterion | Meaning | TQL range (under DO-178C DAL B) |
|---|---|---|
| 1 | Tool output is part of the airborne software AND could insert an error | TQL-1..2 |
| 2 | Tool output is part of verification AND could fail to detect an error | TQL-4..5 |
| 3 | Tool output is used for verification but is independently checked | TQL-5 |

Under the **assumed** DAL-B allocation for FCC / HM in this workbench,
most of our in-house tools sit at criterion 2 or 3.

## Per-tool notes

### `tools/runner` — requirement-based verification runner
- **Use classification**: criterion 2 (verification tool; failure to detect
  an error could lead to an unverified requirement).
- **Assumed TQL**: TQL-5 (DAL-B × criterion 3) if every test result were
  cross-checked by at least one independent assertion. Today the runner is
  the only check, so assume TQL-4.
- **Operational requirements**: deterministic execution, JSON schema
  validation, per-test isolation (no shared mutable state), recorder
  sha256 unchanged between runs.
- **Verification activities**: `tests/python/test_runner.py` exercises the
  loader, trace builder, and gap reporter on the sample test set.
- **Known limitations**: no flake detection loop; no coverage-of-expectations
  analysis; world builder is hand-written and not driven by a formal IDL.

### `tools/coverage_reporter` — line coverage via `sys.settrace`
- **Use classification**: criterion 3 (structural coverage evidence is
  independently checked by human review of per-file deltas).
- **Assumed TQL**: TQL-5.
- **Operational requirements**: `sys.settrace` hook must not alter program
  behaviour; `ast`-derived executable-line set must be stable across runs.
- **Verification activities**: `tests/python/test_coverage_helper.py`.
- **Known limitations**: no branch / decision coverage; ``ast`` line
  detection counts decorators as executable; no source-level exclusion.

### `tools/sim_py/avx_sim/mcdc.py` — MC/DC tracker
- **Use classification**: criterion 2 (without this, MC/DC evidence would
  not exist).
- **Assumed TQL**: TQL-4.
- **Operational requirements**: pair-detection algorithm must be textbook
  (masking MC/DC), tracker must be disabled on production runs to
  avoid heisenbugs.
- **Verification activities**: `tests/python/test_mcdc.py` with a fully
  enumerated truth table.
- **Known limitations**: only decisions instrumented via explicit
  `McdcTracker.record` calls are observed; no AST-level auto-discovery.

### `tools/fault_injector` — campaign runner
- **Use classification**: criterion 2 (verification).
- **Assumed TQL**: TQL-5.
- **Known limitations**: fault taxonomy is deliberately small; compute-layer
  faults (clock skew, brownout) only reachable via the HIL-lite bridge.

### `tools/evidence_bundler` — bundle exporter + verifier
- **Use classification**: criterion 3 (configuration management helper).
- **Assumed TQL**: TQL-5.
- **Verification activities**: `tests/python/test_bundler.py` including a
  tamper-detection case.
- **Known limitations**: git metadata is captured as a plain SHA, no GPG
  signing; zip timestamps pinned to 2026-01-01 for determinism.

### `tools/ai_assistant` — rule-based assurance helpers
- **Use classification**: criterion 3 strictly. Every output is labelled
  ``DRAFT — human-in-the-loop`` and is never directly merged.
- **Assumed TQL**: not qualifiable for airborne software generation; the
  only supported mode is "draft for human review."
- **Known limitations**: deterministic rules with no learned components;
  no natural-language reasoning; change-impact index is a prefix heuristic.

## DO-331 (model-based development) applicability

The workbench does not use a graphical modelling tool, but two boundaries
could be framed as DO-331 supplements if future work wanted to:

- **ICD messages** (`avx_sim/messages.py`) are dataclass-level schemas; a
  code-generator that emits them from a YAML source would sit under the
  "model coverage" framing in DO-331.
- **Partition table** (`config/partitions/default.txt`) is a declarative
  model of the schedule; the scheduler interprets it directly. A real
  DO-331 use case would add model-level analysis (schedulability proof,
  bandwidth calculation) before feeding it to the runtime.

## Summary disclaimer

Nothing in this document constitutes qualification. The TQL entries are the
**assumptions** this workbench uses to sanity-check its own process; they
have not been substantiated against DO-330's objective tables.
