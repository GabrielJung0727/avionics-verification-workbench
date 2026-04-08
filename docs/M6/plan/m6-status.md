# M6 — Status Snapshot

## Module map
| Component | File | Notes |
|---|---|---|
| Bundle exporter | `tools/evidence_bundler/bundler.py` | Hermetic zip + manifest + sha256 |
| Replay verifier | `tools/evidence_bundler/bundler.py` `verify_bundle()` | Recompute & diff hashes |
| Replay CLI | `scripts/replay_bundle.py` | `python scripts/replay_bundle.py <bundle.zip>` |
| Orchestrator integration | `scripts/run_verification.py` | Builds + self-verifies bundle on every run |
| Portfolio resume bullets | `docs/M6/portfolio/resume-bullets.md` | Short + 5 position-tailored variants |
| LinkedIn post draft | `docs/M6/portfolio/linkedin-post.md` | — |
| Demo script | `docs/M6/demo/demo-script.md` | 5-min flow from M1 |
| Tests | `tests/python/test_bundler.py` | 4 cases incl. tamper detection |

## Bundle layout
```
bundle-<run_id>-<git_sha>.zip
├── manifest.json          schema + run_id + git + summary + per-file sha256 + DAL + disclaimer
├── env/
│   ├── git_sha.txt
│   └── tool_versions.json
├── inputs/
│   ├── partition_table.txt
│   ├── test_cases/*.json
│   └── campaigns/*.json
├── results/
│   ├── test_results.json
│   ├── campaigns.json
│   ├── mcdc_report.json
│   ├── coverage.json
│   ├── hf_findings.json
│   ├── mode_confusion.json
│   └── hil_runs.json
└── trace/
    ├── req_to_test.json
    └── gap_report.json
```

## Local run
```
Ran 78 tests in 1.328s — OK

=== Evidence bundle ===
  path: evidence/bundles/bundle-bd016f7d-aab7f670.zip
  files: 21
  git_sha: aab7f6707d0c
  verify: OK
```

```
$ python scripts/replay_bundle.py evidence/bundles/bundle-*.zip
files         : 21
summary:
  tests_total: 6     tests_passed: 6
  campaigns_total: 3 campaigns_passed: 2
  mcdc_pct_avg: 100.0
  hf_total: 6        hf_passed: 6
  hil_runs: 4
verify: OK (all sha256 hashes match manifest)
```

## Exit Criteria
- [x] evidence bundle exporter 동작 (zip + manifest + hash)
- [x] bundle만으로 무결성 재검증 가능 — `replay_bundle.py`
- [x] DO-178C objective 매핑 — `docs/M1/certification/do178c-mapping.md` v0
- [x] 통합 데모 시나리오 — `docs/M6/demo/demo-script.md`
- [x] 영문 README 핵심 메시지 — `README.md` 이미 영문 portfolio-grade
- [x] 이력서 bullet 3종 + 포지션별 5종 — `docs/M6/portfolio/resume-bullets.md`
- [x] LinkedIn 포스트 초안 — `docs/M6/portfolio/linkedin-post.md`
- [x] Airbus / Boeing 포지션별 강조 매핑 — `resume-bullets.md` 하단

## Carry-overs / not in scope
- 5분 video 녹화 → manual recording task
- HTML coverage 시각화 → optional
- Real UDP HIL transport → optional
- DER 수준의 evidence (이건 학습 워크벤치라 의도적으로 out of scope, manifest disclaimer에 명시)
