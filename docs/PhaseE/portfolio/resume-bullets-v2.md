# Resume Bullets v2 (Phase A–D included)

> v1 lives at `docs/M6/portfolio/resume-bullets.md`. v2 adds the data
> foundation, certification intelligence, safety case workflow, and
> bounded operational AI threads.

## Headline (3-line, strongest)

- Designed and built a **certification-aligned avionics verification
  intelligence platform**: IMA-style partitioned scheduler, ARINC 429-lite
  + AFDX-lite buses, FCC / Engine / Display surrogates, end-to-end
  Req↔Test↔Result traceability, immutable evidence bundles with sha256
  replay verification, all aligned with DO-178C / ARP4754A / DO-297 / AC
  20-175 lifecycles.

- Built an **enterprise-grade data foundation** (Bronze / Silver / Gold
  Lakehouse with ANSI-SQL portability to Databricks / BigQuery / Athena),
  a **frozen-model registry** with dataset_hash + label_version +
  approval_state, three v0 learned components (escape predictor, engine
  anomaly detector, trace gap intel), and a **GSN-lite assurance case**
  with reviewer workflow + DO-330 tool qualification hypotheses.

- Implemented a **runtime assurance shell** (range / rate / authority /
  watchdog) and Shadow → Advisory → LimitedSupervised mode progression so
  AI components stay strictly outside the control loop, aligning with
  EASA AI Concept Paper Level 1·2 and the FAA AI Roadmap incremental
  approach. Online learning attempts raise an exception at load time.

## Position-tailored variants

### Airbus / Boeing — Flight software
> Built an IMA-style cooperative partitioned scheduler with budget
> enforcement, deadline-miss reporting, partition restart, cold/warm
> start, and a configurable health monitor. Layered on top: an FCC
> surrogate with independent command and monitor lanes, mode reversion
> (NORMAL / ALTERNATE / DIRECT), input validation. Verification driven
> by JSON test cases linked to DO-178C-style HLRs with MC/DC instrumented
> on designated decisions.

### Verification & Validation
> Requirement-based JSON test runner, fault campaign loader with
> detected/mitigated/escaped classification, line + MC/DC coverage,
> immutable evidence bundles with sha256 replay verification. Phase B
> escape predictor (sklearn GBC) sits on top — proposes which campaigns
> to run first, never gates them.

### Display / HMI
> Flight Deck Display Computer with alert prioritization (warning >
> caution > advisory), static red/amber/green color rule, mode
> annunciation latency budget enforcement, dashed values on stale
> inputs, mode-confusion scenario library aligned to AC 20-175 / AC
> 25.1322 guidance.

### IMA / System integration
> ARP4754A-style requirements flow + ARP4761A-style FHA hypotheses, IMA
> partitioning with sampling and queuing IPC ports, configurable health
> monitor with event→action mapping, fault containment validated by a
> stable recorder hash used as the determinism regression test.

### Defence / Space
> Deterministic loopback HIL with configurable latency / jitter / drop /
> reboot / brownout faults; runtime assurance shell separating
> deterministic safety primacy from frozen learned components.
> Architecture mirrors the FAA Roadmap's incremental approach +
> runtime assurance recommendation.

### Data / Platform engineering
> Bronze / Silver / Gold Lakehouse on a SQLite backend that maps
> one-to-one onto Databricks / BigQuery / Azure ML. 9 normalized Silver
> tables (run_manifest, verification_outcome, fault_injection_case,
> telemetry_event, …) all reachable by run_id. Dataset contract with
> schema-drift gate fails the build on silent breakage. Local
> MLflow-style model registry with frozen-model + assurance metadata
> bundle.
