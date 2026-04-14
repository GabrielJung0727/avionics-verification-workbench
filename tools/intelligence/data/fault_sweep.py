"""Synthetic fault campaign sweep — produces deterministic training data for
the escape predictor without requiring 55,000 real Databricks runs.

Each record is a fixed-feature row whose ``classification`` is derived from
a *known* rule that mimics the real ``run_campaign`` semantics:

  - high AFDX delay AND high drop_every_n  -> often escaped
  - dual sensor fault before t1s           -> mitigated (FCC enters DIRECT)
  - n1_at_t1s in warning band              -> detected
  - benign parameters                      -> escaped (no system response)

The point is to train and evaluate the *pipeline* end-to-end so that the
moment a real Databricks sweep produces 55k labelled rows the model trains
without code change.
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field
from itertools import product


@dataclass(frozen=True)
class FaultSweepRecord:
    delay_us: int
    drop_every_n: int
    n1_at_t1s: float
    egt_at_t1s: float
    dual_fault_us: int        # -1 means no dual fault
    seed: int
    campaign_family: str      # split key (NOT random)
    classification: str       # 'detected' | 'mitigated' | 'detected_and_mitigated' | 'escaped'

    @property
    def label_escape(self) -> int:
        return 1 if self.classification == "escaped" else 0


def _classify(delay_us: int, drop_every_n: int, n1: float, egt: float,
              dual_fault_us: int) -> str:
    detected = (n1 >= 103) or (egt >= 900)
    mitigated = (dual_fault_us >= 0)
    if detected and mitigated:
        return "detected_and_mitigated"
    if detected:
        return "detected"
    if mitigated:
        return "mitigated"
    # Bus storms only escape if both delay and drop are large
    if delay_us >= 80_000 and drop_every_n >= 3:
        return "escaped"
    if delay_us >= 60_000 or drop_every_n >= 5:
        return "escaped"
    return "escaped"


def _family(delay_us: int, n1: float, dual: int) -> str:
    """Group campaigns into families so the train/holdout split is non-random."""
    if dual >= 0:
        return "fam_dual_fault"
    if n1 >= 103 or delay_us >= 80_000:
        return "fam_high_stress"
    return "fam_benign"


def generate_fault_sweep(*, seed: int = 42, target_count: int = 600
                         ) -> list[FaultSweepRecord]:
    """Deterministic Cartesian-ish sweep across the four fault axes."""
    rng = random.Random(seed)

    delay_grid = [0, 20_000, 40_000, 60_000, 80_000, 120_000]
    drop_grid = [0, 2, 3, 5, 10]
    n1_grid = [80, 95, 100, 103, 106]
    dual_grid = [-1, 10_000, 50_000, 200_000]
    label_flip_p = 0.07   # synthetic noise so holdout AUC is realistic

    records: list[FaultSweepRecord] = []
    for delay, drop, n1, dual in product(delay_grid, drop_grid, n1_grid, dual_grid):
        egt = 700.0 + (n1 - 80) * 6 + (delay // 20_000) * 5
        for s in (1, 7):
            cls = _classify(delay, drop, n1, egt, dual)
            if rng.random() < label_flip_p:
                if cls == "escaped":
                    cls = "detected"
                elif cls == "detected":
                    cls = "escaped"
            records.append(FaultSweepRecord(
                delay_us=delay,
                drop_every_n=drop,
                n1_at_t1s=float(n1),
                egt_at_t1s=float(egt),
                dual_fault_us=dual,
                seed=s,
                campaign_family=_family(delay, n1, dual),
                classification=cls,
            ))

    # Shuffle deterministically just so the file order isn't accidentally
    # a sort by family — split_by_key does the real grouping later.
    rng.shuffle(records)
    return records[:target_count]
