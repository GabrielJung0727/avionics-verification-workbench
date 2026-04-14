"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiSummary, type SummaryPayload } from "@/lib/api";
import MetricCard from "./MetricCard";

type Loaded =
  | { kind: "loading" }
  | { kind: "down"; reason: string }
  | { kind: "ok"; data: SummaryPayload["summary"] };

const FIELDS: { key: string; label: string; tone?: "amber" | "cyan" | "ok" }[] = [
  { key: "tests_passed", label: "Tests passed", tone: "ok" },
  { key: "tests_total", label: "Tests total" },
  { key: "campaigns_passed", label: "Campaigns passed" },
  { key: "campaigns_total", label: "Campaigns total" },
  { key: "coverage_pct", label: "Line coverage %", tone: "cyan" },
  { key: "mcdc_pct_avg", label: "MC/DC avg %", tone: "amber" },
  { key: "hf_passed", label: "HF passed", tone: "ok" },
  { key: "hil_runs", label: "HIL runs" },
  { key: "mode_confusion_ok", label: "Mode-confusion OK" },
  { key: "gap_uncovered_count", label: "Uncovered req" },
];

export default function LiveSummary() {
  const t = useTranslations("live");
  const [state, setState] = useState<Loaded>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const r = await apiSummary();
      if (cancelled) return;
      if (!r.ok) setState({ kind: "down", reason: r.error });
      else setState({ kind: "ok", data: r.data.summary });
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (state.kind === "loading")
    return <SkeletonGrid label={t("loading")} />;
  if (state.kind === "down")
    return (
      <p className="panel px-4 py-3 text-[13px] text-ink-400">
        {t("backend_unreachable")} <code>{state.reason}</code>
      </p>
    );

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {FIELDS.map((f) => {
        const raw = state.data[f.key];
        if (raw === undefined || raw === null) return null;
        const value =
          typeof raw === "number" && f.key.includes("pct")
            ? `${Number(raw).toFixed(2)}%`
            : String(raw);
        return (
          <MetricCard
            key={f.key}
            label={f.label}
            value={value}
            tone={f.tone}
          />
        );
      })}
    </div>
  );
}

function SkeletonGrid({ label }: { label: string }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="panel p-4">
          <div className="label-mono">{label}</div>
          <div className="mt-2 h-7 w-24 animate-pulse rounded bg-graphite-700" />
        </div>
      ))}
    </div>
  );
}
