# Coverage & MC/DC (M4)

## 수집 방법
- LLVM `-fprofile-instr-generate -fcoverage-mapping`
- per-test profraw → merge → llvm-cov export json
- per-test coverage → req-based 매핑까지 합산

## 리포트 종류
- Statement / Branch / Decision (전 모듈)
- MC/DC (지정 함수만)

## MC/DC 대상 함수 (M4 v0)
- FCC input validation
- FCC mode transition decision
- FCC reversion guard
- Engine exceedance latch decision
- DSP alert priority decision

## MC/DC 분석 절차
1. AST에서 decision/condition 추출
2. truth table 생성
3. 각 condition별 MC/DC pair 후보 계산
4. 테스트 실행 trace에서 pair 충족 여부 확인
5. 미충족 condition을 리포트

## CI 게이트
- 전체 statement coverage ≥ 80% (학습 목표)
- MC/DC 대상 함수 충족률 ≥ 90%
- 미달 시 PR fail
