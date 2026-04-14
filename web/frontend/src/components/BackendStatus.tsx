"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiHealth, apiPredictHealth, BACKEND_URL } from "@/lib/api";

type State =
  | { kind: "loading" }
  | { kind: "down"; reason: string }
  | {
      kind: "up";
      report: boolean;
      lakehouse: boolean;
      registry: boolean;
      predict: boolean;
    };

export default function BackendStatus({ compact = false }: { compact?: boolean }) {
  const t = useTranslations("live");
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const [h, p] = await Promise.all([apiHealth(), apiPredictHealth()]);
      if (cancelled) return;
      if (!h.ok) {
        setState({ kind: "down", reason: h.error });
        return;
      }
      setState({
        kind: "up",
        report: h.data.report_present,
        lakehouse: h.data.lakehouse_present,
        registry: h.data.registry_present,
        predict: p.ok && p.data.available,
      });
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (compact) {
    return <CompactBadge state={state} t={t} />;
  }

  return (
    <div className="panel flex flex-wrap items-center justify-between gap-3 p-3 text-[12px]">
      <div className="flex items-center gap-2">
        <Dot state={state} />
        <span className="label-mono">{t("backend_label")}</span>
        <code className="font-mono text-ink-200">{BACKEND_URL}</code>
      </div>
      <Indicators state={state} t={t} />
    </div>
  );
}

function Dot({ state }: { state: State }) {
  if (state.kind === "loading")
    return <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-ink-400" />;
  if (state.kind === "down")
    return <span className="inline-block h-2 w-2 rounded-full bg-amber" />;
  return <span className="inline-block h-2 w-2 rounded-full bg-ok" />;
}

function CompactBadge({
  state,
  t,
}: {
  state: State;
  t: ReturnType<typeof useTranslations>;
}) {
  const label =
    state.kind === "loading"
      ? t("loading")
      : state.kind === "down"
      ? t("down")
      : t("live");
  const cls =
    state.kind === "up"
      ? "badge badge-ok"
      : state.kind === "down"
      ? "badge badge-amber"
      : "badge";
  return (
    <span className={cls}>
      <Dot state={state} />
      {label}
    </span>
  );
}

function Indicators({
  state,
  t,
}: {
  state: State;
  t: ReturnType<typeof useTranslations>;
}) {
  if (state.kind === "loading") return <span className="text-ink-400">…</span>;
  if (state.kind === "down")
    return (
      <span className="text-amber">
        {t("down")} · {state.reason}
      </span>
    );
  return (
    <ul className="flex flex-wrap gap-3 font-mono text-[11px]">
      <Pill on={state.report} label="report" />
      <Pill on={state.lakehouse} label="lakehouse" />
      <Pill on={state.registry} label="registry" />
      <Pill on={state.predict} label="predict" />
    </ul>
  );
}

function Pill({ on, label }: { on: boolean; label: string }) {
  return (
    <li
      className={
        "rounded-sm border px-2 py-0.5 " +
        (on
          ? "border-ok/50 text-ok"
          : "border-graphite-600 text-ink-400")
      }
    >
      {label}
      {on ? " ✓" : " —"}
    </li>
  );
}
