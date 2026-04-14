"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { apiPredictEscape, type EscapePrediction } from "@/lib/api";

const PRESETS = [
  { name: "benign", delay_us: 0, drop_every_n: 0, n1_at_t1s: 80, egt_at_t1s: 700, dual_fault_us: -1, seed: 1 },
  { name: "bus storm", delay_us: 80000, drop_every_n: 3, n1_at_t1s: 80, egt_at_t1s: 700, dual_fault_us: -1, seed: 1 },
  { name: "engine warning", delay_us: 0, drop_every_n: 0, n1_at_t1s: 104, egt_at_t1s: 880, dual_fault_us: -1, seed: 1 },
  { name: "dual sensor fault", delay_us: 0, drop_every_n: 0, n1_at_t1s: 80, egt_at_t1s: 700, dual_fault_us: 50000, seed: 1 },
];

type Body = (typeof PRESETS)[number];

type State =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "down"; reason: string }
  | { kind: "ok"; result: EscapePrediction; req: Body };

export default function PredictWidget() {
  const t = useTranslations("live");
  const [body, setBody] = useState<Body>(PRESETS[1]);
  const [state, setState] = useState<State>({ kind: "idle" });

  const setField = (k: keyof Body, v: number) =>
    setBody((b) => ({ ...b, [k]: v }));

  const submit = async () => {
    setState({ kind: "loading" });
    const r = await apiPredictEscape(body);
    if (!r.ok) setState({ kind: "down", reason: r.error });
    else setState({ kind: "ok", result: r.data, req: body });
  };

  return (
    <section className="panel p-5">
      <div className="label-mono mb-3 text-cyan">{t("predict_h")}</div>
      <p className="mb-4 text-[13px] text-ink-200">{t("predict_intro")}</p>

      <div className="mb-4 flex flex-wrap gap-2">
        {PRESETS.map((p) => (
          <button
            key={p.name}
            type="button"
            onClick={() => setBody({ ...p, name: p.name })}
            className={
              "badge transition " +
              (body.name === p.name ? "badge-amber" : "hover:border-amber/40")
            }
          >
            {p.name}
          </button>
        ))}
      </div>

      <div className="grid gap-3 text-[12px] sm:grid-cols-2 lg:grid-cols-3">
        <Num label="delay_us" v={body.delay_us} on={(v) => setField("delay_us", v)} step={10000} />
        <Num label="drop_every_n" v={body.drop_every_n} on={(v) => setField("drop_every_n", v)} step={1} />
        <Num label="n1_at_t1s" v={body.n1_at_t1s} on={(v) => setField("n1_at_t1s", v)} step={1} />
        <Num label="egt_at_t1s" v={body.egt_at_t1s} on={(v) => setField("egt_at_t1s", v)} step={10} />
        <Num label="dual_fault_us" v={body.dual_fault_us} on={(v) => setField("dual_fault_us", v)} step={10000} />
        <Num label="seed" v={body.seed ?? 1} on={(v) => setField("seed", v)} step={1} />
      </div>

      <button
        type="button"
        onClick={submit}
        disabled={state.kind === "loading"}
        className="mt-5 badge badge-cyan disabled:opacity-50"
      >
        {state.kind === "loading" ? t("loading") : t("predict_run")}
      </button>

      {state.kind === "down" && (
        <p className="mt-4 text-[13px] text-amber">
          {t("predict_unreachable")} <code>{state.reason}</code>
        </p>
      )}
      {state.kind === "ok" && (
        <div className="mt-5 panel ring-amber p-4">
          <div className="label-mono text-amber">{t("predict_result")}</div>
          <div className="mt-2 grid gap-3 sm:grid-cols-3">
            <Stat label="model" v={`${state.result.model} ${state.result.version ?? ""}`} />
            <Stat
              label="P(escape)"
              v={state.result.p_escape.toFixed(3)}
              tone="amber"
            />
            <Stat label="advice" v={state.result.advice} tone="cyan" />
          </div>
        </div>
      )}
    </section>
  );
}

function Num({
  label,
  v,
  on,
  step,
}: {
  label: string;
  v: number;
  on: (v: number) => void;
  step: number;
}) {
  return (
    <label className="block">
      <span className="label-mono">{label}</span>
      <input
        type="number"
        step={step}
        value={v}
        onChange={(e) => on(Number(e.target.value))}
        className="mt-1 w-full rounded-sm border border-graphite-700 bg-navy-950 px-2 py-1 font-mono text-[13px] text-ink-50 focus:border-amber focus:outline-none"
      />
    </label>
  );
}

function Stat({
  label,
  v,
  tone,
}: {
  label: string;
  v: string;
  tone?: "amber" | "cyan";
}) {
  const cls = tone === "amber" ? "text-amber" : tone === "cyan" ? "text-cyan" : "text-ink-50";
  return (
    <div>
      <div className="label-mono">{label}</div>
      <div className={`mt-1 font-mono text-base ${cls}`}>{v}</div>
    </div>
  );
}
