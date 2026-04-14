// Tiny typed client for the FastAPI backend at web/backend/.
//
// Configured at build time via NEXT_PUBLIC_BACKEND_URL (defaults to
// http://localhost:8000). All callers should treat backend absence as a
// non-error: the frontend stays useful as a static portfolio without it.

export const BACKEND_URL =
  process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://localhost:8000";

export type ApiResult<T> =
  | { ok: true; data: T }
  | { ok: false; error: string };

async function jget<T>(path: string): Promise<ApiResult<T>> {
  try {
    const r = await fetch(BACKEND_URL + path, {
      cache: "no-store",
      headers: { Accept: "application/json" },
    });
    if (!r.ok) return { ok: false, error: `HTTP ${r.status}` };
    return { ok: true, data: (await r.json()) as T };
  } catch (e: unknown) {
    return { ok: false, error: e instanceof Error ? e.message : String(e) };
  }
}

async function jpost<T>(path: string, body: unknown): Promise<ApiResult<T>> {
  try {
    const r = await fetch(BACKEND_URL + path, {
      method: "POST",
      cache: "no-store",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(body),
    });
    if (!r.ok) {
      const text = await r.text();
      return { ok: false, error: `HTTP ${r.status}: ${text.slice(0, 200)}` };
    }
    return { ok: true, data: (await r.json()) as T };
  } catch (e: unknown) {
    return { ok: false, error: e instanceof Error ? e.message : String(e) };
  }
}

// ---- typed routes -------------------------------------------------------

export type HealthPayload = {
  ok: boolean;
  report_present: boolean;
  lakehouse_present: boolean;
  registry_present: boolean;
  intelligence_endpoint: string | null;
};
export const apiHealth = () => jget<HealthPayload>("/api/health");

export type SummaryPayload = {
  summary: Record<string, number | string>;
};
export const apiSummary = () => jget<SummaryPayload>("/api/results/summary");

export type ModelEntry = {
  model_name: string;
  version: string;
  approval_state?: string;
  frozen?: boolean;
  intended_use?: string;
  out_of_scope?: string[];
  git_sha?: string;
  training_seed?: number;
  dataset?: {
    version?: string;
    hash_short?: string;
    split_strategy?: string;
    split_key?: string;
    n_train?: number;
    n_holdout?: number;
    label_version?: string;
  };
  metrics?: Record<string, unknown>;
};
export const apiModels = () =>
  jget<{ models: ModelEntry[] }>("/api/registry/models");

export type PredictHealth = {
  endpoint: string | null;
  available: boolean;
  upstream?: unknown;
  error?: string;
};
export const apiPredictHealth = () =>
  jget<PredictHealth>("/api/predict/health");

export type EscapePrediction = {
  model: string;
  version?: string;
  p_escape: number;
  advice: string;
};
export const apiPredictEscape = (body: {
  delay_us: number;
  drop_every_n: number;
  n1_at_t1s: number;
  egt_at_t1s: number;
  dual_fault_us: number;
  seed?: number;
}) => jpost<EscapePrediction>("/api/predict/fault_escape", body);
