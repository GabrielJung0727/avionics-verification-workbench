# Avionics Verification Workbench — One-page architecture

_System-of-systems verification workbench; not a flight-control demo._

```
+------------------------------------------------------------------+
|                      Engineering Workbench                       |
|  Req tree | Trace graph | Evidence bundles | AI assist (DRAFT)   |
+-----------------------+------------------------------------------+
                        |                         ^
                        v                         |
+------------------------------------------------------------------+
|                 Verification Orchestrator                        |
|  Requirement-based runner | Coverage | MC/DC | Fault campaigns   |
|                       HF eval | HIL-lite                         |
+-----------------------+------------------------------------------+
                        |
                        v
+------------------------------------------------------------------+
|            Deterministic Sim Kernel  (Python reference)          |
|   IMA Scheduler | Health Monitor | Cold/Warm/Restart             |
|             Sampling + Queuing IPC | Recorder (sha256)           |
+---+---------+---------+--------+---------+----------------------+
    |         |         |        |         |
+---v-+   +---v----+ +--v-----+ +v------+ +v-----+
| DC  |   |  FCC   | |  ENG   | | DSP   | |  HM  |
|     |   | cmd+mon| |        | |PFD/EIC| |      |
+--+--+   +---+----+ +---+----+ +---+---+ +------+
   |          |          |         |
+--v----------v----------v---------v---+
|  Virtual Bus  (ARINC 429-lite + AFDX-lite + fault hooks)
+--------------------------------------+
           |
           v
   +-------+-------+
   | HIL-lite bridge  ->  LoopbackMcu (latency/jitter/drop/reboot)
   +---------------+
```

## Key properties
- **Deterministic sim clock** — no wall-clock anywhere, seeded PRNG.
- **Partitioned runtime** — period/offset/budget enforcement, deadline-miss
  detection, cold/warm start, partition restart.
- **Traceable end-to-end** — Req ↔ Design ↔ Code ↔ Test ↔ Result ↔ Evidence.
- **AI only in assurance layer** — draft artifacts, human-in-the-loop.

## Standards mapping (learning-grade)
| Area | Reference |
|---|---|
| Software assurance | DO-178C |
| Tool qualification | DO-330 |
| Model-based supplement | DO-331 |
| System assurance | ARP4754A |
| IMA integration | DO-297 / AC 20-170 |
| Flight-deck HF | AC 20-175 / AC 25.1322 |

## Evidence bundle
Each verification run produces a hermetic `bundle-<uuid>-<gitsha>.zip`
containing:
- `manifest.json` — schema v1.0, git SHA, tool versions, per-file sha256
- `inputs/` — partition table, test cases, fault campaigns
- `results/` — test results, campaigns, MC/DC, coverage, HF, HIL
- `trace/` — req→test graph, gap report
- `env/` — git SHA, tool versions

Any reviewer can run `python scripts/replay_bundle.py <bundle.zip>` to
re-verify every file's hash against the manifest.

## Disclaimer
Learning-grade workbench. DAL ratings, TQL assumptions, failure conditions,
and HF thresholds are documented assumptions. Nothing here is a certified
verification record.
