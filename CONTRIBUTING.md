# Contributing

Thanks for taking the time. This is a personal portfolio project, but
external review is exactly the feedback it exists to attract — especially
from people who actually work in real avionics V&V, IMA integration,
human factors, or AI safety assurance.

If something here would make a real reviewer wince, **please open an
issue**. Saying "you got X wrong" with a one-line explanation is more
useful than a long PR.

## Ground rules

1. **AI never closes a control loop.** This is enforced in code (Phase D
   `tools/intelligence/runtime/loader.py` — `OnlineLearningAttempt`).
   Any contribution that violates this rule will be rejected.
2. **Random splits are forbidden** in any ML training script. Use
   `tools/intelligence/data/splits.py::split_by_key` or `split_by_date`.
3. **Every assurance case keeps the 12 required sections.** The Phase C
   linter runs in CI.
4. **No certification credit is claimed.** DAL, TQL, AI-level ratings are
   hypotheses. See `docs/regulatory/disclaimer.md`.
5. **Determinism.** Every scenario must be reproducible from a seed. The
   `tools/sim_py/avx_sim/sim_clock.py` is the only source of time.

## Local development

```bash
git clone https://github.com/<you>/avionics-verification-workbench.git
cd avionics-verification-workbench
pip install -r requirements.txt

# Run the whole platform end-to-end
python scripts/run_verification.py

# Run only the Python tests
python -m unittest discover -s tests/python -t .
```

Optional:
```bash
# Start the local intelligence-serving endpoint
python scripts/serve_intelligence.py

# Ingest the latest evidence into the lakehouse
python scripts/ingest_evidence.py ingest evidence/verification-report.json

# Verify a bundle
python scripts/replay_bundle.py evidence/bundles/bundle-*.zip

# Print the elevator pitch (5s / 30s / 60s / hard-line)
python scripts/elevator_pitch.py 30s
```

## How to add things

### A new requirement
1. Add a row to `docs/M1/requirements/requirements.csv` (id, level, text,
   rationale, source, criticality, verify_method).
2. Mirror it in `docs/M1/requirements/requirements-tree.md`.
3. The CI requirements-check job validates uniqueness + count thresholds.

### A new test case
1. Add a JSON file under `tools/runner/test_cases/` linking to one or
   more `req` ids.
2. The verification runner picks it up automatically.

### A new fault campaign
1. Add a JSON file under `tools/fault_injector/campaigns/`.
2. Document the fault hint mapping in `tools/fault_injector/escape.py`
   if it should map to an FC- entry.

### A new Phase B model
1. Train it via a script under `scripts/`.
2. Register through `LocalRegistry.register()` with the full metadata
   bundle (`dataset.json` + `meta.json` + `metrics.json` +
   `model_card.json` + `assurance_stub.md`).
3. Write the Phase C assurance case at `docs/PhaseC/cases/<model>.md`
   with all 12 required sections.

### A new in-house tool
1. Add it under `tools/`.
2. Append a row to `docs/PhaseC/tool-qualification/do330-classification.md`
   (use criterion + TQL hypothesis + known limitations).

## Code style

- Python 3.11+, type hints where they help, `dataclass` over hand-rolled
  classes.
- `f"..."` strings; no `%`-formatting in new code.
- One module = one responsibility; cross-package imports go runtime →
  analytics, never the reverse.
- ASCII in CLI scripts (Windows cp949 friendliness).
- No external network calls in tests; HIL-lite is in-process loopback by
  design.

## Commit messages

Conventional Commits style (`feat:`, `fix:`, `chore:`, `docs:`, `ci:`).
Multi-line bodies welcome; explain *why*, not just *what*.

## Pull request checklist

- [ ] `python -m unittest discover -s tests/python -t .` is green
- [ ] `python scripts/run_verification.py` is green
- [ ] If you touched a Phase B model, the Phase C case still lints
- [ ] If you touched the dataset contract, you bumped the schema
  version in `tools/data_foundation/catalog.py`
- [ ] `CHANGELOG.md` updated under `## [Unreleased]`
- [ ] No DAL / TQL / AI-level claim added without `docs/regulatory/disclaimer.md` cross-reference

## Reporting issues

Please include:
- What you ran (`scripts/...` command)
- What happened (output, hash, screenshot)
- What you expected
- Your `python --version`, OS, and `pip freeze | grep -E 'numpy|sklearn'`

If you saw a violation of any of the **Ground rules** above, prefix the
issue title with `[hard-line]` so it gets the highest priority.

## Code of conduct

Be honest, be specific, and aim for a real-reviewer tone. No emojis in
issue titles. Korean or English both fine.
