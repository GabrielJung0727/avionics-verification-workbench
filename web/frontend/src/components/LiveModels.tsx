"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { apiModels, type ModelEntry } from "@/lib/api";

type Loaded =
  | { kind: "loading" }
  | { kind: "down"; reason: string }
  | { kind: "ok"; models: ModelEntry[] };

export default function LiveModels() {
  const t = useTranslations("live");
  const [state, setState] = useState<Loaded>({ kind: "loading" });

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const r = await apiModels();
      if (cancelled) return;
      if (!r.ok) setState({ kind: "down", reason: r.error });
      else setState({ kind: "ok", models: r.data.models });
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (state.kind === "loading")
    return <p className="text-[13px] text-ink-400">{t("loading")}</p>;
  if (state.kind === "down")
    return (
      <p className="panel px-4 py-3 text-[13px] text-ink-400">
        {t("backend_unreachable")} <code>{state.reason}</code>
      </p>
    );
  if (!state.models.length)
    return (
      <p className="panel px-4 py-3 text-[13px] text-ink-400">
        {t("no_models")}
      </p>
    );

  return (
    <div className="grid gap-3 md:grid-cols-3">
      {state.models.map((m) => {
        const stateBadge =
          m.approval_state === "board-approved"
            ? "badge badge-ok"
            : m.approval_state === "reviewer-confirmed"
            ? "badge badge-cyan"
            : "badge badge-amber";
        const headlineMetric = pickHeadlineMetric(m.metrics);
        return (
          <article
            key={`${m.model_name}-${m.version}`}
            className="panel p-5"
          >
            <div className="flex items-baseline justify-between gap-3">
              <h3 className="text-base font-semibold">{m.model_name}</h3>
              <span className="font-mono text-[11px] text-ink-400">
                {m.version}
              </span>
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              <span className={stateBadge}>{m.approval_state ?? "?"}</span>
              {m.frozen && <span className="badge">frozen</span>}
            </div>
            {m.intended_use && (
              <p className="mt-3 text-[13px] text-ink-200">{m.intended_use}</p>
            )}
            {m.dataset && (
              <dl className="mt-3 space-y-1 text-[11px] font-mono text-ink-400">
                <Row k="dataset" v={m.dataset.version} />
                <Row k="hash" v={m.dataset.hash_short} />
                <Row k="split" v={`${m.dataset.split_strategy} / ${m.dataset.split_key}`} />
                <Row
                  k="train/holdout"
                  v={`${m.dataset.n_train ?? "?"} / ${m.dataset.n_holdout ?? "?"}`}
                />
              </dl>
            )}
            {headlineMetric && (
              <p className="mt-3 font-mono text-[12px] text-amber">
                {headlineMetric}
              </p>
            )}
          </article>
        );
      })}
    </div>
  );
}

function Row({ k, v }: { k: string; v?: string | null }) {
  if (!v) return null;
  return (
    <div className="flex gap-2">
      <dt className="w-20 text-ink-600">{k}</dt>
      <dd className="text-ink-200">{v}</dd>
    </div>
  );
}

function pickHeadlineMetric(m?: Record<string, unknown>): string | null {
  if (!m) return null;
  if (typeof m.auc === "number") return `AUC ${m.auc.toFixed(3)}`;
  if (typeof m.detection_rate === "number" && typeof m.false_alarm_rate === "number")
    return `detect ${(m.detection_rate as number).toFixed(2)} / fa ${(m.false_alarm_rate as number).toFixed(2)}`;
  if (typeof m.precision_at_3 === "number")
    return `precision@3 ${(m.precision_at_3 as number).toFixed(2)}`;
  return null;
}
