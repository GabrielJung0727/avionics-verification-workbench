# LinkedIn post draft

I've been building something I'd actually want to talk about in an avionics interview:

**Certification-Aware Avionics Integration & Verification Workbench** — a learning-grade platform that takes the *boring but career-defining* parts of flight-software work seriously.

Not another fly-by-wire demo. Instead:

* IMA-style partitioned scheduler with budget enforcement and a health monitor
* ARINC 429-lite and AFDX-lite virtual buses with fault injection (drop, delay, reorder, stale-data)
* FCC surrogate with independent command/monitor lanes and mode reversion
* Display Computer with alert prioritization, color rule, and mode-latency budget
* Requirement-based JSON test runner, line coverage, MC/DC on designated decisions (100%)
* Fault-injection campaigns classified as detected / mitigated / escaped
* AC 20-175 / AC 25.1322 human-factors evaluators + mode-confusion scenario library
* HIL-lite loopback with latency/jitter/drop/reboot measurement
* Immutable evidence bundles with sha256 replay verification

Everything is traceable end-to-end: Req → HLR → Code → Test → Result → Evidence bundle.

DO-178C / ARP4754A / DO-297 / AC 20-175 mappings are learning-grade assumptions — clearly disclaimered — but the engineering vocabulary and lifecycle are real.

If this kind of work speaks to you, the repo is on GitHub. Feedback from V&V, IMA integration, and HF engineers is the feedback I most want.

#avionics #DO178C #verification #flightsoftware #humanfactors
