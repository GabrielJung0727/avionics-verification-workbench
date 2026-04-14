export default function ArchDiagram({ caption }: { caption?: string }) {
  return (
    <figure className="panel grid-bg p-5">
      <pre className="overflow-x-auto whitespace-pre font-mono text-[11px] leading-relaxed text-ink-200 md:text-[12px]">{`
+----------------------------------------------------------------+
|        Verification Intelligence  (Phase B / C / D)            |
|                                                                |
|   Phase B frozen models             Phase D runtime guard      |
|   +------------------+              +-----------------------+  |
|   | escape predictor | -- raw -->   | range / rate /        |  |
|   | engine anomaly   |              | authority / watchdog  |  |
|   | trace gap intel  |              +-----------+-----------+  |
|   +------------------+                          |              |
|          ^                                      v              |
|          | load(approval_state)        Shadow / Advisory /     |
|          |                              LimitedSupervised      |
|   Phase C: GSN-lite assurance + 3-state reviewer workflow      |
+----------------------------------------------------------------+
                                ^
                                | trains on Silver
+----------------------------------------------------------------+
|   Phase A — Lakehouse  (Bronze -> Silver -> Gold)              |
|   schema-drift gate · run_id lineage · dataset contract        |
+----------------------------------------------------------------+
                                ^
                                | orchestrator dumps
+----------------------------------------------------------------+
|   Deterministic Verification Workbench (M1–M6)                 |
|                                                                |
|   IMA Scheduler · ARINC 429-lite · AFDX-lite ·                 |
|   FCC / Engine / Display · Requirement runner · MC/DC ·        |
|   Fault campaigns · HF · HIL · Immutable evidence bundles      |
+----------------------------------------------------------------+
`}</pre>
      {caption && (
        <figcaption className="mt-3 text-center text-[12px] text-ink-400">
          {caption}
        </figcaption>
      )}
    </figure>
  );
}
