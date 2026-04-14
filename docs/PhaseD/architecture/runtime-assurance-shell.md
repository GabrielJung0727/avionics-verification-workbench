# Runtime Assurance Shell

```
   AI raw output
        │
        ▼
┌─────────────────────────────────────────┐
│  RuntimeAssuranceShell                  │
│                                         │
│  1. range_check       (hard clamp)      │
│  2. rate_limiter      (Δ/tick cap)      │
│  3. authority_cap     (max influence)   │
│  4. watchdog          (timeout → fail)  │
│  5. operator_gate     (ack required)    │
│                                         │
│  Any violation → log + deterministic    │
│  fallback path engaged, never silent    │
└────────────┬────────────────────────────┘
             │ guarded output
             ▼
   ┌─────────────────────────────┐
   │ Mode-specific consumer       │
   │  • Shadow      log only      │
   │  • Advisory    UI flag       │
   │  • LimitedSup  ack-gated act │
   └─────────────────────────────┘

   In parallel — ALWAYS:
   ┌─────────────────────────────┐
   │ Deterministic fallback       │
   │ (the existing M3 pipeline)   │
   └─────────────────────────────┘
```

## Layer 1 — Range
Every output dimension declares `[low, high]`. Out-of-range → clamped at
the boundary AND a `RANGE_VIOLATION` event is logged. Output beyond a
configurable "hard limit" → output suppressed and fallback engaged.

## Layer 2 — Rate
Per-output `max_delta_per_tick`. If the AI suddenly proposes a 50%
change, the shell emits the previous-step value plus the rate-limited
delta and logs a `RATE_VIOLATION`. The unsmoothed AI value is preserved
in the violation record so a reviewer can see what the model wanted.

## Layer 3 — Authority
For each consumer service, the shell knows the **maximum influence** the
AI is allowed to have on any state variable (e.g. "may shift display
priority by ≤1 level; may NOT change FCC mode"). The shell rejects any
output whose decoded action exceeds the authority budget.

## Layer 4 — Watchdog
Each AI inference call has a `timeout_us`. If the model exceeds budget,
the shell:
1. cancels the call
2. emits `WATCHDOG_TIMEOUT`
3. proceeds with the deterministic-only path

## Layer 5 — Operator gate
For `Advisory` and `LimitedSupervised` modes, every AI suggestion is
parked in an **ack queue**. No action happens until the operator (a
test bench engineer here, a flight crew in production) writes an
explicit `ack` record. The `Shadow` mode skips this layer (it never
acts).

## Telemetry
Every shell call writes a row to `runtime_shell_log.jsonl`:
```
{
  "ts_us": 12345,
  "model": "engine_anomaly_detector",
  "mode": "shadow",
  "ai_raw": {...},
  "guarded": {...},
  "violations": ["RATE_VIOLATION"],
  "fallback_engaged": false
}
```

This stream is the input to the AI-vs-deterministic comparison report.
