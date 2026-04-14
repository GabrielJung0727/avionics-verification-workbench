#!/usr/bin/env python3
"""Start the local intelligence endpoint.

By default binds 127.0.0.1:8081. Use ``--port 0`` to pick any free port.
The server runs until Ctrl-C; in CI / orchestrator contexts use the
``IntelligenceServer.start_in_thread()`` API directly instead.

Routes:
    GET  /health
    GET  /models
    POST /predict/fault_escape
    POST /predict/engine_anomaly
    POST /predict/trace_gap
"""
from __future__ import annotations
import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from intelligence import build_server  # noqa: E402

REGISTRY = ROOT / "evidence" / "registry"
REQ_CSV = ROOT / "docs" / "M1" / "requirements" / "requirements.csv"


def _load_req_ids() -> list[str]:
    out: list[str] = []
    if not REQ_CSV.exists():
        return out
    with REQ_CSV.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rid = row.get("id")
            if rid:
                out.append(rid)
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="serve_intelligence")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8081)
    args = parser.parse_args(argv)

    server = build_server(
        registry_root=REGISTRY,
        host=args.host, port=args.port,
        requirement_ids=_load_req_ids(),
    )
    print(f"intelligence endpoint: http://{args.host}:{server.port}")
    print("routes: /health  /models  /predict/{fault_escape, engine_anomaly, trace_gap}")
    print("Ctrl-C to stop")
    try:
        server.httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")
    finally:
        server.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
