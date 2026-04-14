# `web/backend/` — read-only FastAPI surface

A small FastAPI app that serves the artefacts the Python orchestrator
already wrote to `evidence/` — verification report, lakehouse, registry,
shadow run — plus a thin proxy to the Phase B intelligence-serving
endpoint. **The backend never triggers a verification run and never
mutates the workbench.**

## Quick start

```bash
cd web/backend
pip install -r requirements.txt

# Make sure evidence/ exists. From repo root:
#   python scripts/run_verification.py

# Start the API
uvicorn app.main:app --reload --port 8000
# → http://127.0.0.1:8000
# → http://127.0.0.1:8000/docs (interactive Swagger UI)
```

If you also want the predict endpoints to work, run the Phase B
intelligence server in another shell and point the backend at it:

```bash
# shell A
python scripts/serve_intelligence.py            # listens on :8081

# shell B
INTELLIGENCE_ENDPOINT=http://127.0.0.1:8081 \
  uvicorn web.backend.app.main:app --reload --port 8000
```

## Routes

| Method | Path | What it returns |
|---|---|---|
| GET | `/` | Service descriptor + route index |
| GET | `/api/health` | Presence flags for report / lakehouse / registry |
| GET | `/api/results/summary` | Headline numbers (tests, MC/DC, HF, HIL, …) |
| GET | `/api/results/tests` | Per-test pass/fail with req links |
| GET | `/api/results/campaigns` | Fault-injection campaign outcomes |
| GET | `/api/results/mcdc` | Per-decision MC/DC stats |
| GET | `/api/results/coverage` | Line-coverage report |
| GET | `/api/results/hf` | Human-factors evaluator findings |
| GET | `/api/results/hil` | HIL-lite per-config measurements |
| GET | `/api/results/trace` | Req → test trace + gap report |
| GET | `/api/results/shadow` | Latest Phase D shadow-run report |
| GET | `/api/results/bundles` | Discoverable evidence bundle archives |
| GET | `/api/lakehouse/health` | DB presence flag |
| GET | `/api/lakehouse/gold` | List of available Gold views |
| GET | `/api/lakehouse/gold/{view}` | Rows from a Gold view (whitelisted) |
| GET | `/api/lakehouse/runs` | Recent run_manifest rows |
| GET | `/api/lakehouse/runs/{run_id}/lineage` | Full lineage record |
| GET | `/api/registry/models` | Every registered model + assurance metadata |
| GET | `/api/registry/models/{name}/{version}` | Full meta + dataset + metrics + assurance stub |
| GET | `/api/predict/health` | Upstream intelligence endpoint reachability |
| POST | `/api/predict/fault_escape` | Proxy to upstream `/predict/fault_escape` |
| POST | `/api/predict/engine_anomaly` | Proxy to upstream `/predict/engine_anomaly` |
| POST | `/api/predict/trace_gap` | Proxy to upstream `/predict/trace_gap` |

Every response body carries a `_draft` field that re-states the disclaimer.

## Read-only by design

This API is intentionally read-only:

- **No** route triggers `run_verification.py` or any other heavy job
- **No** route writes to `evidence/`, the lakehouse, or the registry
- Predict calls are *proxied* to the existing intelligence endpoint, so
  Phase D's `OnlineLearningAttempt` / approval-gate enforcement still
  applies upstream
- Gold-view names are whitelisted to prevent arbitrary SQL through the URL

## CORS

Default allows `http://localhost:3000` (the Next.js dev server). Override
with the `BACKEND_ALLOWED_ORIGINS` env var (comma-separated).

## Disclaimer

Like every other surface in this repository, the backend ships
`docs/regulatory/disclaimer.md` semantics. Nothing here is substantiated
certification evidence. DAL / TQL / AI-level ratings are hypotheses.
