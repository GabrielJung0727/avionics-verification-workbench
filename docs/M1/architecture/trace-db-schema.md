# Trace DB Schema (v0)

목적: Req ↔ Design ↔ Code ↔ Test ↔ Result 양방향 trace + change impact + gap report.

## ER Diagram (텍스트)
```
┌──────────────┐        ┌────────────────┐        ┌──────────────┐
│ Requirement  │1      *│ ReqLink        │*      1│ Requirement  │
│              │────────│ (parent/child) │────────│              │
└──────┬───────┘        └────────────────┘        └──────────────┘
       │ 1
       │
       │ *
┌──────v───────┐        ┌────────────────┐
│ TestCase     │*──────*│ TestRun        │
│              │        │                │
└──────┬───────┘        └────────┬───────┘
       │ *                       │ *
       │                         │
       │ *                       │ *
┌──────v───────┐         ┌───────v────────┐
│ CodePath     │         │ Artifact       │
│ (file:func)  │         │ (bus rec, hm)  │
└──────────────┘         └────────────────┘

┌──────────────┐        ┌────────────────┐
│ ChangeReq    │1      *│ Impact         │
│              │────────│ (target ref)   │
└──────────────┘        └────────────────┘
```

## 테이블 정의 (요약 DDL)
```sql
CREATE TABLE requirement (
  id            TEXT PRIMARY KEY,         -- SYS-001 / HLR-FCC-003
  level         TEXT NOT NULL,            -- SYS / HLR / LLR
  text          TEXT NOT NULL,
  rationale     TEXT,
  source        TEXT,
  criticality   TEXT NOT NULL,            -- High / Med / Low
  verify_method TEXT,
  status        TEXT NOT NULL DEFAULT 'draft',
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE req_link (
  parent_id  TEXT REFERENCES requirement(id),
  child_id   TEXT REFERENCES requirement(id),
  kind       TEXT NOT NULL,               -- derives / refines / satisfies
  PRIMARY KEY (parent_id, child_id)
);

CREATE TABLE test_case (
  id          TEXT PRIMARY KEY,           -- TC-FCC-001
  description TEXT,
  scenario    TEXT,                       -- yaml path
  seed        BIGINT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE test_req_link (
  test_id TEXT REFERENCES test_case(id),
  req_id  TEXT REFERENCES requirement(id),
  PRIMARY KEY (test_id, req_id)
);

CREATE TABLE code_path (
  id        BIGSERIAL PRIMARY KEY,
  file      TEXT NOT NULL,
  symbol    TEXT NOT NULL,                -- function / class
  language  TEXT
);

CREATE TABLE test_code_link (
  test_id     TEXT REFERENCES test_case(id),
  code_path_id BIGINT REFERENCES code_path(id),
  PRIMARY KEY (test_id, code_path_id)
);

CREATE TABLE test_run (
  id          BIGSERIAL PRIMARY KEY,
  test_id     TEXT REFERENCES test_case(id),
  run_uuid    UUID NOT NULL,
  result      TEXT NOT NULL,              -- PASS / FAIL / ERROR / FLAKY
  started_at  TIMESTAMPTZ NOT NULL,
  finished_at TIMESTAMPTZ NOT NULL,
  git_sha     TEXT NOT NULL,
  seed        BIGINT NOT NULL,
  bundle_hash TEXT
);

CREATE TABLE artifact (
  id          BIGSERIAL PRIMARY KEY,
  run_id      BIGINT REFERENCES test_run(id),
  kind        TEXT NOT NULL,              -- bus_rec / hm_log / coverage / mcdc
  path        TEXT NOT NULL,
  sha256      TEXT NOT NULL
);

CREATE TABLE change_request (
  id           TEXT PRIMARY KEY,          -- CR-YYYYMMDD-NN
  title        TEXT NOT NULL,
  type         TEXT NOT NULL,
  trigger      TEXT,
  risk         TEXT,
  status       TEXT NOT NULL DEFAULT 'draft',
  author       TEXT,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE change_impact (
  cr_id     TEXT REFERENCES change_request(id),
  ref_kind  TEXT NOT NULL,                -- requirement / test / code / icd
  ref_id    TEXT NOT NULL,
  PRIMARY KEY (cr_id, ref_kind, ref_id)
);
```

## 핵심 쿼리
- **Orphan req**: `SELECT id FROM requirement WHERE id NOT IN (SELECT req_id FROM test_req_link);`
- **Trace gap (test without req)**: `SELECT id FROM test_case WHERE id NOT IN (SELECT test_id FROM test_req_link);`
- **Latest run per test**: window function on `test_run(test_id, started_at DESC)`
- **Change impact**: join `change_impact` ↔ tests/code/req

## 마이그레이션
- M1: schema 초안만 (이 문서)
- M2: alembic / sqlx-migrate 도입
- M3: code_path 자동 수집기 (clang index)
- M4: dashboard 쿼리 + gap/escape 리포트
