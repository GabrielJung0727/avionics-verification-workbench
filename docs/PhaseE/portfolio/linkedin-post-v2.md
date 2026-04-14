# LinkedIn post v2

> v1 lives at `docs/M6/portfolio/linkedin-post.md`. v2 highlights the
> Phase A–D pivot (data foundation → assurance case → runtime guard).

---

After a few months of building, here's the project I'd actually want to
discuss in an avionics interview:

**Certification-Aligned Avionics Verification Intelligence Platform**

Not a fly-by-wire demo. Not "AI for autopilot." The opposite — a platform
that takes the boring-but-career-defining parts of flight software work
seriously:

🛩️  **The classical workbench (M1–M6)**
- IMA-style partitioned scheduler with budget enforcement
- ARINC 429-lite + AFDX-lite virtual buses with fault injection
- FCC surrogate with independent command/monitor lanes + mode reversion
- DO-178C requirement-based test runner + MC/DC + line coverage
- AC 20-175 / 25.1322 human-factors evaluators + HIL-lite loopback
- Immutable evidence bundles with sha256 replay verification

🗄️  **Phase A — Enterprise Data Foundation**
- Bronze/Silver/Gold Lakehouse (SQLite locally; same SQL on Databricks,
  BigQuery, Athena)
- 9 Silver tables, every row reachable by `run_id`
- Schema-drift gate fails the build on silent breakage

🧠  **Phase B — Certification Intelligence**
- 3 frozen learned components: escape predictor, engine anomaly
  detector, trace gap intel
- Local MLflow-style registry with `dataset_hash + label_version +
  approval_state`
- Non-random splits enforced (campaign-family / bench-seed / date)

📜  **Phase C — Reviewable Safety Case**
- GSN-lite assurance case per model — 12 required sections, linter as
  PR gate
- 3-state approval workflow with audit log; self-review prohibited
- DO-330 tool classification + TQL hypotheses

🔬  **Phase D — Bounded Operational AI**
- Runtime assurance shell: range / rate / authority / watchdog
- Shadow → Advisory → LimitedSupervised mode progression
- Below `board-approved` → loader refuses Advisory+ at runtime
- `model.fit()` and `partial_fit()` raise `OnlineLearningAttempt`
- Aligns with EASA AI Concept Paper Level 1·2 + FAA AI Roadmap

The hard line, restated:

> *This project is not an AI flight controller. It is a
> certification-aligned avionics verification intelligence platform that
> uses governed datasets, traceable evidence, and bounded learned
> components to improve verification prioritization, anomaly detection,
> and operational assurance under existing aviation safety frameworks.*

145 tests passing. Repo is on GitHub. If this kind of work resonates —
V&V engineers, IMA integrators, human-factors specialists, lakehouse
folks in aerospace — I'd love your harshest review.

#avionics #DO178C #ARP4754A #verification #lakehouse #frozenmodels
#runtimeassurance #flightsoftware #humanfactors
