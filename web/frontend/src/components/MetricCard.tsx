export default function MetricCard({
  label,
  value,
  hint,
  tone = "default",
}: {
  label: string;
  value: string;
  hint?: string;
  tone?: "default" | "amber" | "cyan" | "ok";
}) {
  const valueColor =
    tone === "amber"
      ? "text-amber"
      : tone === "cyan"
      ? "text-cyan"
      : tone === "ok"
      ? "text-ok"
      : "text-ink-50";
  return (
    <div className="panel p-4">
      <div className="label-mono">{label}</div>
      <div className={`mt-2 font-mono text-2xl ${valueColor}`}>{value}</div>
      {hint && <div className="mt-1 text-[12px] text-ink-400">{hint}</div>}
    </div>
  );
}
