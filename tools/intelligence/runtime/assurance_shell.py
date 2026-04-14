"""Runtime assurance shell — 4-layer guardrail around AI output.

  1. range_check       (hard clamp + violation log)
  2. rate_limiter      (max delta per tick)
  3. authority_cap     (budget on action magnitude)
  4. watchdog          (timeout -> fallback engaged)

Operator gating is layer 5 and lives in `modes.py` because it depends on
the chosen mode (Shadow has no gate; Advisory parks in an ack queue;
LimitedSupervised waits for explicit ack).

The shell never raises on a violation — it always returns a result so the
deterministic pipeline can keep running. Violations are recorded for the
disagreement tracker.
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class ShellViolation(str, Enum):
    RANGE = "RANGE_VIOLATION"
    RATE = "RATE_VIOLATION"
    AUTHORITY = "AUTHORITY_EXCEEDED"
    WATCHDOG = "WATCHDOG_TIMEOUT"
    INVALID_OUTPUT = "INVALID_OUTPUT"


@dataclass
class AuthorityBudget:
    """How far the AI may shift any single dimension. Beyond this -> the
    shell engages the deterministic fallback for that dimension."""
    max_abs_value: float = 1.0
    max_abs_delta: float = 0.5


@dataclass
class ShellConfig:
    output_keys: list[str]
    ranges: dict[str, tuple[float, float]] = field(default_factory=dict)
    rate_limits: dict[str, float] = field(default_factory=dict)
    authority: dict[str, AuthorityBudget] = field(default_factory=dict)
    watchdog_us: int = 50_000   # 50 ms typical


@dataclass
class ShellResult:
    guarded: dict[str, Any]
    raw: dict[str, Any]
    violations: list[ShellViolation] = field(default_factory=list)
    fallback_engaged: bool = False
    elapsed_us: int = 0
    ts_us: int | None = None


class RuntimeAssuranceShell:
    """One shell instance per (model, consumer)."""

    def __init__(self, config: ShellConfig,
                 fallback_provider: Callable[[dict[str, Any]],
                                             dict[str, Any]] | None = None):
        self.cfg = config
        self.fallback_provider = fallback_provider
        self._prev_guarded: dict[str, float] = {}

    # ------------------------------------------------------------------
    def _range_check(self, k: str, v: float, vio: list[ShellViolation]
                     ) -> float:
        rng = self.cfg.ranges.get(k)
        if rng is None:
            return v
        low, high = rng
        if v < low or v > high:
            vio.append(ShellViolation.RANGE)
            return max(low, min(high, v))
        return v

    def _rate_check(self, k: str, v: float, vio: list[ShellViolation]
                    ) -> float:
        cap = self.cfg.rate_limits.get(k)
        if cap is None:
            return v
        prev = self._prev_guarded.get(k)
        if prev is None:
            return v
        delta = v - prev
        if abs(delta) > cap:
            vio.append(ShellViolation.RATE)
            return prev + (cap if delta > 0 else -cap)
        return v

    def _authority_check(self, k: str, v: float, vio: list[ShellViolation]
                         ) -> tuple[float, bool]:
        budget = self.cfg.authority.get(k)
        if budget is None:
            return v, False
        if abs(v) > budget.max_abs_value:
            vio.append(ShellViolation.AUTHORITY)
            return 0.0, True            # signal fallback for this dim
        prev = self._prev_guarded.get(k)
        if prev is not None and abs(v - prev) > budget.max_abs_delta:
            vio.append(ShellViolation.AUTHORITY)
            return prev, True
        return v, False

    # ------------------------------------------------------------------
    def evaluate(self, model_call: Callable[[], dict[str, Any]],
                 *, sim_ts_us: int | None = None,
                 wall_clock: Callable[[], float] = time.perf_counter,
                 ) -> ShellResult:
        """Run the model call under the watchdog and pass the output
        through the layers. ``model_call`` is a thunk returning the raw
        AI dict so the shell controls timing."""
        start = wall_clock()
        try:
            raw = model_call()
        except Exception as exc:
            elapsed = int((wall_clock() - start) * 1_000_000)
            fb = self.fallback_provider({}) if self.fallback_provider else {}
            return ShellResult(
                guarded=fb, raw={"_error": str(exc)},
                violations=[ShellViolation.INVALID_OUTPUT],
                fallback_engaged=True, elapsed_us=elapsed, ts_us=sim_ts_us,
            )
        elapsed = int((wall_clock() - start) * 1_000_000)

        violations: list[ShellViolation] = []
        if elapsed > self.cfg.watchdog_us:
            violations.append(ShellViolation.WATCHDOG)
            fb = self.fallback_provider(raw) if self.fallback_provider else {}
            return ShellResult(
                guarded=fb, raw=raw, violations=violations,
                fallback_engaged=True, elapsed_us=elapsed, ts_us=sim_ts_us,
            )

        if not isinstance(raw, dict):
            violations.append(ShellViolation.INVALID_OUTPUT)
            fb = self.fallback_provider({}) if self.fallback_provider else {}
            return ShellResult(
                guarded=fb, raw={"_raw": str(raw)}, violations=violations,
                fallback_engaged=True, elapsed_us=elapsed, ts_us=sim_ts_us,
            )

        guarded: dict[str, Any] = {}
        any_fallback = False
        for k in self.cfg.output_keys:
            v = raw.get(k)
            if not isinstance(v, (int, float)):
                guarded[k] = v
                continue
            v = float(v)
            v = self._range_check(k, v, violations)
            v = self._rate_check(k, v, violations)
            v, fb = self._authority_check(k, v, violations)
            any_fallback = any_fallback or fb
            guarded[k] = v
            self._prev_guarded[k] = v

        # Pass through non-numeric metadata fields.
        for k, v in raw.items():
            if k not in guarded:
                guarded[k] = v

        if any_fallback and self.fallback_provider is not None:
            guarded = self.fallback_provider(guarded)

        return ShellResult(
            guarded=guarded,
            raw=raw,
            violations=violations,
            fallback_engaged=any_fallback,
            elapsed_us=elapsed,
            ts_us=sim_ts_us,
        )
