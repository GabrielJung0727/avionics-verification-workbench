# Evidence Bundle Manifest Format (v0)

M6에서 채워질 evidence bundle의 매니페스트 포맷을 M1 단계에서 합의한다. 모든 산출물이 처음부터 이 포맷을 가정하고 만들어진다.

## manifest.json 스펙

```json
{
  "schema_version": "1.0",
  "run_id": "uuid-v4",
  "created_at": "ISO-8601",
  "workbench_version": "git-describe-style",

  "build": {
    "git_sha": "string",
    "git_dirty": false,
    "compiler": "string",
    "cmake_version": "string",
    "tool_versions": {
      "python": "3.12.x",
      "llvm": "x.y.z",
      "protoc": "x.y.z"
    }
  },

  "scenario": {
    "id": "string",
    "seed": 0,
    "duration_ms": 0,
    "config_files": ["string"],
    "fault_campaign": "string|null"
  },

  "inputs": [
    {
      "path": "inputs/scenario.yaml",
      "sha256": "hex"
    }
  ],

  "results": [
    {
      "path": "results/bus_recording.bin",
      "kind": "bus_recording",
      "sha256": "hex"
    },
    {
      "path": "results/hm_log.csv",
      "kind": "hm_log",
      "sha256": "hex"
    },
    {
      "path": "results/test_results.json",
      "kind": "test_results",
      "sha256": "hex"
    },
    {
      "path": "results/coverage_html/",
      "kind": "coverage_html",
      "sha256": "tree-hash-hex"
    },
    {
      "path": "results/mcdc_report.json",
      "kind": "mcdc_report",
      "sha256": "hex"
    }
  ],

  "trace": [
    {
      "path": "trace/req_to_test.json",
      "sha256": "hex"
    },
    {
      "path": "trace/gap_report.json",
      "sha256": "hex"
    }
  ],

  "summary": {
    "tests_total": 0,
    "tests_passed": 0,
    "tests_failed": 0,
    "tests_flaky": 0,
    "coverage_statement": 0.0,
    "coverage_branch": 0.0,
    "coverage_mcdc_target_pct": 0.0,
    "escapes_total": 0
  },

  "dal_assumptions": [
    {"module": "fcc_cmd_lane", "dal": "B"},
    {"module": "fcc_mon_lane", "dal": "B"},
    {"module": "health_monitor", "dal": "B"},
    {"module": "engine_interface", "dal": "C"},
    {"module": "display_computer", "dal": "C"},
    {"module": "data_concentrator", "dal": "C"}
  ],

  "disclaimer": "Learning-grade workbench. DAL ratings are assumptions and not certified."
}
```

## 무결성 / 재현성 규칙
1. 모든 파일은 sha256 (디렉터리는 정렬된 path-content tree hash) 가 manifest에 있어야 한다.
2. `bundle.zip`을 풀고 `scripts/replay.sh bundle/` 실행 시 동일 hash가 나와야 한다.
3. mismatch 시 replay tool은 비-0 종료 코드와 mismatch 목록을 출력한다.
4. `git_dirty=true`인 bundle은 "experimental" 태그를 manifest에 추가한다.

## 명명 규칙
- 파일명: `bundle-<run_id_short>-<git_sha_short>.zip`
- 폴더 구조는 `docs/M6/evidence/bundle-format.md` 를 따른다.

## M2~M6 진행 시 책임
- M2: scenario.yaml / bus_recording.bin schema 고정
- M3: hm_log.csv / test_results.json schema 고정
- M4: coverage_html / mcdc_report.json schema 고정 + gap_report 자동 생성
- M6: exporter + replay tool 구현
