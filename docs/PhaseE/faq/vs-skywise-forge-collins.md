# FAQ — "Skywise / Honeywell Forge / Collins와 뭐가 다른가요?"

> **30초 답변**
> 이 셋은 **fleet operations** 용 commercial 플랫폼이고
> 이 프로젝트는 **certification-aligned verification platform**이다.
> 같은 lakehouse + ML 패턴을 쓰지만 진입점이 다르다 — Skywise/Forge/Collins는
> 운항 데이터로 maintenance를 최적화하고, 이 프로젝트는 verification
> 산출물로 인증 evidence를 강화한다. 둘은 보완적이지 경쟁적이지 않다.

## 비교 표

| 차원 | Airbus Skywise | Honeywell Forge | Collins Aerospace SaaS | **이 프로젝트** |
|---|---|---|---|---|
| 1차 사용자 | 항공사 운항팀 | 항공사·운영자 | OEM·항공사 | **V&V 엔지니어** |
| 데이터 출처 | 운항 중인 12,300+ 항공기 | 비행 데이터 + 운영 데이터 | 운영 telemetry | **시뮬레이터 + verification 결과** |
| 핵심 가치 | predictive maintenance | preventive alert | operational analytics | **verification prioritization + assurance evidence** |
| 인증 위치 | flight ops 보조 | maintenance 보조 | fleet 분석 | **DO-178C / ARP4754A objective 매핑** |
| 대표 산출물 | 부품 고장 예측 | inspection candidate | KPI 대시보드 | **assurance case + evidence bundle** |

## 같은 점
- Lakehouse 패턴 (Bronze/Silver/Gold)
- MLflow / 모델 레지스트리
- 시계열 anomaly detection
- 운영 의사결정 지원

## 다른 점 (핵심 차별화)
1. **데이터 도착 시점이 다르다** — Skywise/Forge는 운항 후 데이터가 들어온다.
   이 프로젝트는 verification 단계, 즉 *비행 전*에 evidence를 만든다.
2. **소비자가 다르다** — 운항팀 대시보드 vs DO-178C objective 매핑 표
3. **AI 사용 위치가 다르다** — 셋 다 AI를 운영 분석에 쓰지만,
   이 프로젝트는 *verification automation*에 쓴다 (escape predictor,
   trace gap intel)
4. **Runtime assurance shell** — Phase D의 shadow → advisory →
   limited supervised 패턴은 **fleet ops 플랫폼이 아니라 인증 환경에서
   필요한 패턴**이다. Skywise/Forge에는 이 layer가 명시적으로 노출되지 않는다.

## 그래서 채용 맥락에서는?
- "Skywise / Forge / Collins 경험 있나요?" → "직접 경험은 없지만,
  같은 lakehouse + ML 패턴을 verification 도메인에 적용해 만들었습니다.
  fleet 데이터를 verification evidence로 치환하면 그대로 옮겨갑니다."
- 회사 입장에서는 *훈련 비용이 낮은 후보*다. 패턴은 동일, 도메인만 인접.

## 더 깊이
- `docs/PhaseA/architecture/lakehouse-layout.md`
- `docs/PhaseB/architecture/registry-design.md`
- `docs/PhaseE/standards/standards-mapping-v2.md`
