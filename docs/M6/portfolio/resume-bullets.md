# Resume Bullets — Avionics Verification Workbench

## Short (3-line, strongest)
- Designed and built a certification-aware avionics integration & verification workbench: IMA-style partitioned scheduler, ARINC 429-lite + AFDX-lite buses, FCC/Engine/Display surrogates, and end-to-end Req ↔ Test ↔ Result traceability aligned with DO-178C objectives.
- Implemented a requirement-based verification runner with line coverage, MC/DC analysis on designated decisions (100% on both instrumented decisions), and deterministic fault-injection campaigns classified as detected / mitigated / escaped.
- Added AC 20-175 / 25.1322 human-factors evaluators, mode-confusion scenarios, an HIL-lite loopback with latency/jitter/drop/reboot measurement, and an immutable evidence bundle exporter with manifest + sha256 replay verification.

## Position-tailored variants

### Airbus / Boeing flight software
- Built an IMA-style cooperative partitioned scheduler with budget enforcement, deadline-miss reporting, and a health monitor, plus an FCC surrogate with independent command and monitor lanes, mode reversion logic, and input validation — all driven by a deterministic sim clock and exercised by requirement-based JSON test cases linked to DO-178C-style HLRs.

### Display / HMI
- Implemented a Flight Deck Display Computer with alert prioritization (warning > caution > advisory), static red/amber/green color rule checks, mode-annunciation latency budgets, dashed values on stale inputs, and a mode-confusion scenario library aligned to AC 20-175 / AC 25.1322 guidance.

### Verification & validation
- Built a requirement-based verification runner on top of a deterministic simulator, including line coverage via `sys.settrace`, MC/DC pair detection on instrumented decisions, fault-injection campaigns with detected/mitigated/escaped classification, and immutable evidence bundles with sha256 replay verification.

### IMA / system integration
- Designed and implemented IMA-style partitioning (period/offset/budget enforcement), sampling and queuing IPC ports with freshness flags, a health monitor with configurable event → action mapping, and a fault-containing runtime validated by a shared recorder with a stable sha256 hash used as the determinism regression test.

### Defence / space variant
- Added an HIL-lite bridge that couples the workbench to a deterministic loopback MCU surrogate with configurable latency, jitter, drop, reboot, and brownout faults, reporting mean/max latency and jitter stddev per run; results feed the same evidence bundle pipeline used by the civil-aviation modules.
